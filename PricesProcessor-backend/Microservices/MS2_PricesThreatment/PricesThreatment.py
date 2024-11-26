import time
import requests
import os
import logging
import configparser
import numpy as np
import pandas as pd
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression
from datetime import datetime
from collections import OrderedDict
import json


class PricesThreatment:

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logger = logging.getLogger()
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    CONFIG_FILE_PATH = os.path.join(BASE_DIR, '../config/config.ini')

    def __init__(self):
        """Inicjalizacja pustych pól klasy"""
        self.config_path = None
        self.symbols_endpoint = None
        self.fetch_data_endpoint = None
        self.save_data_endpoint = None
        self.degree = None
        self.num_bars = None
        self.extrapolated_timestamp = None
        self.sleep_between_symbols = None
        self.sleep_between_cycles = None
        self.view = None
        self.symbols = []  # Lista ID aktywnych symboli

    def load_config(self):
        """Ładuje konfigurację z pliku"""
        self.logger.info("Loading configuration...")
        self.config_path = self.CONFIG_FILE_PATH
        config = configparser.ConfigParser()
        self.logger.debug(f"Config path: {self.config_path}")

        if not os.path.exists(self.config_path):
            self.logger.error(f"Config file not found at: {self.config_path}")
            raise FileNotFoundError(f"Config file not found at: {self.config_path}")

        config.read(self.config_path)
        self.logger.info("Config file loaded successfully.")

        try:
            self.symbols_endpoint = 'http://localhost:8080/api/prices/activesymbols'
            self.fetch_data_endpoint = 'http://localhost:8080/api/prices/latest'
            self.save_data_endpoint = 'http://localhost:8080/api/pricesProcesssed/batch-add'

            self.degree = config.getint('settings ExtrapolateSymbols', 'degree')
            self.num_bars = config.getint('settings ExtrapolateSymbols', 'num_bars')
            self.extrapolated_timestamp = config.getint('settings ExtrapolateSymbols', 'extrapolated_timestamp')
            self.sleep_between_symbols = config.getfloat('settings ExtrapolateSymbols', 'sleep_between_symbols')
            self.sleep_between_cycles = config.getfloat('settings ExtrapolateSymbols', 'sleep_between_cycles')
            self.view = config.getboolean('settings ExtrapolateSymbols', 'view')
        except configparser.Error as e:
            self.logger.error(f"Error reading config: {e}")
            raise

    def get_active_symbols(self):
        """Pobiera aktywne symbole z serwera i zapisuje je jako listę ID"""
        self.logger.info("Fetching active symbols...")
        try:
            response = requests.get(self.symbols_endpoint, timeout=5)
            response.raise_for_status()
            self.logger.debug(f"Response from symbols endpoint: {response.text}")

            if response.status_code == 204 or not response.json():
                self.logger.warning("No active symbols returned from server.")
                self.symbols = []
            else:
                self.symbols = response.json()
                self.logger.info(f"Fetched {len(self.symbols)} active symbols: {self.symbols}")
        except requests.RequestException as e:
            self.logger.error(f"Error fetching active symbols: {e}")
            self.symbols = []
        except (TypeError, ValueError) as e:
            self.logger.error(f"Unexpected data format: {e}")
            self.symbols = []

    def fetch_and_prepare(self, symbol_id):
        """Pobiera dane historyczne dla symbolu w przygotowanym formacie"""
        self.logger.info(f"Fetching prepared data for symbol ID: {symbol_id}")
        try:
            response = requests.get(
                f"{self.fetch_data_endpoint}?symbolId={symbol_id}&limit={self.num_bars}",
                timeout=5
            )
            self.logger.debug(f"Response: {response.status_code}, Content: {response.text}")
            response.raise_for_status()
            prepared_data = response.json()
            self.logger.info(f"Fetched {len(prepared_data)} prepared data points for symbol ID: {symbol_id}")

            # Walidacja danych
            for record in prepared_data:
                if "server_time_raw" not in record or "last" not in record:
                    self.logger.error(f"Invalid data format: {record}")
                    raise ValueError(f"Missing required fields in data: {record}")

            return prepared_data
        except requests.RequestException as e:
            self.logger.error(f"Error fetching prepared data for symbol ID: {symbol_id}: {e}")
            return []
        except ValueError as e:
            self.logger.error(f"Data validation error: {e}")
            return []

    def extrapolate_values(self, data):
        """Ekstrapoluje wartości dla podanych danych, pomijając wpisy z nullami"""
        self.logger.info("Starting extrapolation...")
        if len(data) < 3:
            self.logger.warning("Not enough data to fit polynomial model")
            return []

        try:
            # Filtrujemy dane - usuwamy rekordy, które zawierają null w 'server_time_raw' lub 'last'
            valid_data = [record for record in data if record.get('server_time_raw') is not None and record.get('last') is not None]

            # Jeżeli po filtracji nie ma wystarczających danych, logujemy ostrzeżenie i kończymy
            if len(valid_data) < 3:
                self.logger.warning("Not enough valid data to perform extrapolation.")
                return []

            df = pd.DataFrame(valid_data)
            df['server_time_raw'] = pd.to_numeric(df['server_time_raw'])
            df['last'] = pd.to_numeric(df['last'])

            poly = PolynomialFeatures(degree=self.degree)
            X_poly = poly.fit_transform(df['server_time_raw'].values.reshape(-1, 1))
            model = LinearRegression()
            model.fit(X_poly, df['last'])

            start_time = df['server_time_raw'].min()  # Początek przedziału
            end_time = df['server_time_raw'].max()  # Koniec przedziału

            timestamp = self.extrapolated_timestamp  # Timestamp z konfiguracji

            # Generowanie punktów timestamp w ramach przedziału start_time - end_time
            valid_intervals = []
            for point in range(start_time, end_time + 1):
                if point % timestamp == 0:  # Sprawdzamy, czy punkt jest wielokrotnością `timestamp`
                    valid_intervals.append(point)

            valid_X_poly = poly.transform(np.array(valid_intervals).reshape(-1, 1))
            predictions = model.predict(valid_X_poly)

            results = []
            for timestamp, last in zip(valid_intervals, predictions):
                record = {
                    "timestamp": datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%dT%H:%M:%S'),
                    "server_time_raw": int(timestamp),
                    "last": round(last, 3)
                }
                results.append(record)
                if self.view:
                    self.logger.info(f"Extrapolated data: {record}")

            self.logger.info("Extrapolation completed successfully.")
            return results
        except Exception as e:
            self.logger.error(f"Error during extrapolation: {e}")
            return []


    def save_prices_batch(self, records):
        """Zapisuje batch przetworzonych cen jako listę rekordów"""
        self.logger.info(f"Saving batch of {len(records)} prices...")

        # Lista OrderedDict do zapisania jako JSON
        batch_list = [
            OrderedDict([
                ("symbolId", record["symbol_id"]),  # Zmieniono na 'symbolId'
                ("timestamp", record["timestamp"]),
                ("serverTimeRaw", record["server_time_raw"]),  # Zmieniono na 'serverTimeRaw'
                ("last", record["last"]),
            ])
            for record in records
        ]

        # Wyświetlenie JSON-a przed wysłaniem
        self.logger.info(f"Batch JSON to be sent: {json.dumps(batch_list, indent=4)}")

        # Wysłanie danych do endpointa
        try:
            response = requests.post(self.save_data_endpoint, json=batch_list, timeout=10)
            response.raise_for_status()
            self.logger.info("Batch of processed prices saved successfully.")
        except requests.RequestException as e:
            self.logger.error(f"Error saving batch of processed prices: {e}")

    def process_symbols(self):
        """Główna metoda przetwarzania symboli z zapisem batchowym"""
        self.logger.info("Processing symbols...")

        # Lista do przechowywania rekordów
        batch_records = []

        for symbol_id in self.symbols:  # Iteracja po liście symboli
            self.logger.info(f"Processing symbol ID: {symbol_id}")
            data = self.fetch_and_prepare(symbol_id)
            if not data:
                self.logger.warning(f"No data fetched for symbol ID: {symbol_id}")
                continue

            # Ekstrapolacja danych
            extrapolated_data = self.extrapolate_values(data)
            for record in extrapolated_data:
                record['symbol_id'] = symbol_id
                batch_records.append(record)

            time.sleep(self.sleep_between_symbols)  # Opcjonalny czas między symbolami

        # Zapis wszystkich rekordów w batchu
        if batch_records:
            self.save_prices_batch(batch_records)

        self.logger.info("Processing cycle completed.")

        self.logger.info("Processing cycle completed.")


    def main(self):
        self.logger.info("Starting PricesThreatment...")
        self.load_config()
        self.get_active_symbols()  # Pobieramy symbole raz na starcie

        while True:
            self.process_symbols()
            time.sleep(self.sleep_between_cycles)


if __name__ == "__main__":
    processor = PricesThreatment()
    processor.main()
