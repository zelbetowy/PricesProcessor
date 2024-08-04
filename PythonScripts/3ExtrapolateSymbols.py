import time
import requests
import os
from datetime import datetime, timedelta
import logging
import configparser
import numpy as np
import pandas as pd
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression

# Konfiguracja logowania
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

# Ścieżki do plików
CONFIG_FILE_PATH = 'D:/#SOFT/JAVA/Kutarate/Kutarate/PythonScripts/config/config.ini'
SYMBOLS_FILE_PATH = 'D:/#SOFT/JAVA/Kutarate/Kutarate/PythonScripts/config/symbols.txt'

def load_config():
    config = configparser.ConfigParser()
    logger.info(f"Loading config file from: {CONFIG_FILE_PATH}")
    if not os.path.exists(CONFIG_FILE_PATH):
        logger.error(f"Config file not found at: {CONFIG_FILE_PATH}")
        raise FileNotFoundError(f"Config file not found at: {CONFIG_FILE_PATH}")
    config.read(CONFIG_FILE_PATH)
    logger.info(f"Config file loaded successfully from: {CONFIG_FILE_PATH}")
    return config

# Pobieranie zmiennych z sekcji settings ExtrapolateSymbols
config = load_config()
DEGREE = config.getint('settings ExtrapolateSymbols', 'degree')
NUM_BARS = config.getint('settings ExtrapolateSymbols', 'num_bars')
EXTRAPOLATED_TIMESTAMP = config.getint('settings ExtrapolateSymbols', 'extrapolated_timestamp')
SLEEP_BETWEEN_SYMBOLS = config.getint('settings ExtrapolateSymbols', 'sleep_between_symbols')
SLEEP_BETWEEN_CYCLES = config.getint('settings ExtrapolateSymbols', 'sleep_between_cycles')
view = config.getboolean('settings ExtrapolateSymbols', 'view')

def load_symbols():
    if not os.path.exists(SYMBOLS_FILE_PATH):
        logger.error(f"Symbols file not found at: {SYMBOLS_FILE_PATH}")
        raise FileNotFoundError(f"Symbols file not found at: {SYMBOLS_FILE_PATH}")

    with open(SYMBOLS_FILE_PATH, 'r') as file:
        symbols = [line.strip() for line in file.readlines()]

    logger.info(f"Symbols loaded successfully from: {SYMBOLS_FILE_PATH}")
    return symbols

def send_data_to_server(url, data):
    try:
        response = requests.post(url, json=data, timeout=2)  # Ustawienie timeout na 2 sekundy
        response.raise_for_status()
    except requests.Timeout:
        logger.warning("Server did not respond within 2 seconds.")
    except requests.RequestException as e:
        logger.error(f"Error sending data to server: {e}")

def create_schema_if_not_exists():
    create_process_schema_sql = "CREATE SCHEMA IF NOT EXISTS FOREX_PROCESSDATA;"
    try:
        response = requests.post('http://localhost:8080/SqlApi/executeSQL', data=create_process_schema_sql, timeout=2)
        response.raise_for_status()
        logger.info(f"Process schema creation response: {response.text}")
    except requests.Timeout:
        logger.warning("Server did not respond within 2 seconds while creating schema.")
    except requests.RequestException as e:
        logger.error(f"Error creating schema: {e}")

def create_table_pricesprocessed_if_not_exists(symbol):
    create_table_sql = f"""
    CREATE TABLE IF NOT EXISTS FOREX_PROCESSDATA.PRICESPROCESSED_{symbol} (
        ID IDENTITY PRIMARY KEY,
        TIMESTAMP TIMESTAMP,
        LAST DECIMAL(20, 3),
        CONSTRAINT UNIQUE_INDEX UNIQUE (TIMESTAMP)
    );
    """
    try:
        response = requests.post('http://localhost:8080/SqlApi/executeSQL', data=create_table_sql, timeout=2)
        response.raise_for_status()
        logger.info(f"Create PRICESPROCESSED table response for {symbol}: {response.text}")
    except requests.Timeout:
        logger.warning("Server did not respond within 2 seconds while creating table.")
    except requests.RequestException as e:
        logger.error(f"Error creating table: {e}")

def fetch_last_n_bars(symbol, num_bars):
    fetch_sql = f"""
    SELECT TIMESTAMP, BID, ASK, LAST FROM FOREX_DATA.PRICES_{symbol} ORDER BY TIMESTAMP DESC LIMIT {num_bars};
    """
    try:
        response = requests.post('http://localhost:8080/SqlApi/querySQL', data=fetch_sql, timeout=2)
        response.raise_for_status()
        response_data = response.json()
        return response_data
    except requests.Timeout:
        logger.warning("Server did not respond within 2 seconds while fetching data.")
        return None
    except requests.RequestException as e:
        logger.error(f"Error fetching data from server: {e}")
        return None

def extrapolate_values(symbol, data, degree, extrapolated_timestamp):
    if len(data) < NUM_BARS:
        logger.warning(f"Not enough data to fit the polynomial for {symbol}")
        return None

    # Tworzenie DataFrame z danych
    df = pd.DataFrame(data)
    df['timestamp'] = pd.to_datetime(df['TIMESTAMP']).dt.tz_localize(None)
    df['time_seconds'] = (df['timestamp'] - df['timestamp'].min()).dt.total_seconds()

    # Wybieranie ostatnich num_bars kroków czasowych
    last_bars = df.tail(NUM_BARS)

    # Dopasowanie wielomianu o określonym stopniu do danych
    poly = PolynomialFeatures(degree=degree)
    X_poly = poly.fit_transform(last_bars['time_seconds'].values.reshape(-1, 1))
    model = LinearRegression()
    model.fit(X_poly, last_bars['LAST'])

    # Określenie zakresu czasu
    start_time = last_bars['timestamp'].min()
    end_time = last_bars['timestamp'].max()

    # Generowanie równych kroków czasowych w przeszłości
    equal_intervals = pd.date_range(start=start_time, end=end_time, freq=f'{extrapolated_timestamp}s')

    # Przekształcanie czasów na sekundy
    equal_seconds = (equal_intervals - start_time).total_seconds().astype(int)

    # Upewnienie się, że equal_seconds jest tablicą numpy
    equal_seconds = np.array(equal_seconds).reshape(-1, 1)

    # Przekształcanie na cechy wielomianowe
    equal_X_poly = poly.transform(equal_seconds)

    # Przewidywanie wartości dla równych kroków czasowych
    predicted_values = model.predict(equal_X_poly)

    # Tworzenie wynikowej listy słowników
    extrapolated_data = []
    for ts, value in zip(equal_intervals, predicted_values):
        if (ts.second % extrapolated_timestamp) == 0:
            record = {
                "symbol": symbol,
                "timestamp": ts.strftime('%Y-%m-%d %H:%M:%S'),
                "last": round(value, 3)
            }
            extrapolated_data.append(record)
            logger.info(f"Extrapolated data: {record}")  # Wyświetlanie w konsoli

    return extrapolated_data

def process_symbols(symbols, degree, num_bars, extrapolated_timestamp, sleep_between_symbols, sleep_between_cycles):
    for symbol in symbols:
        create_table_pricesprocessed_if_not_exists(symbol)

    while True:
        for symbol in symbols:
            logger.info(f"Processing symbol: {symbol}")
            try:
                data = fetch_last_n_bars(symbol, num_bars)
                if data:
                    extrapolated_data = extrapolate_values(symbol, data, degree, extrapolated_timestamp)
                    if extrapolated_data:
                        for record in extrapolated_data:
                            # Wyświetlenie danych ekstrapolowanych przed wstawieniem do bazy danych
                            logger.info(f"Attempting to insert extrapolated data: {record}")
                            insert_sql = f"""
                            INSERT INTO FOREX_PROCESSDATA.PRICESPROCESSED_{symbol} (TIMESTAMP, LAST)
                            SELECT '{record['timestamp']}', {record['last']}
                            WHERE NOT EXISTS (
                                SELECT 1 FROM FOREX_PROCESSDATA.PRICESPROCESSED_{symbol} WHERE TIMESTAMP = '{record['timestamp']}'
                            );
                            """
                            try:
                                response = requests.post('http://localhost:8080/SqlApi/executeSQL', data=insert_sql, timeout=2)
                                response.raise_for_status()
                                logger.debug(f"Inserted data: {record}")
                            except requests.Timeout:
                                logger.warning(f"Server did not respond within 2 seconds while inserting data: {record}")
                            except requests.RequestException as e:
                                logger.error(f"Error inserting data: {e}")
            except Exception as e:
                logger.error(f"Exception processing symbol {symbol}: {e}")
            time.sleep(sleep_between_symbols)

        logger.info("Sleeping between cycles")
        time.sleep(sleep_between_cycles)

def main():
    logger.info("Rozpoczynanie działania skryptu Process Symbols")
    symbols = load_symbols()

    create_schema_if_not_exists()

    try:
        process_symbols(symbols, DEGREE, NUM_BARS, EXTRAPOLATED_TIMESTAMP, SLEEP_BETWEEN_SYMBOLS, SLEEP_BETWEEN_CYCLES)
    except KeyboardInterrupt:
        logger.info("Process interrupted by user")

if __name__ == "__main__":
    main()