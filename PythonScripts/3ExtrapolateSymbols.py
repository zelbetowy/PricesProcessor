import time
import requests
import os
import logging
import MetaTrader5 as mt5
import configparser
import numpy as np
import pandas as pd
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression
from datetime import datetime

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

def get_login_info(config):
    try:
        account = config.getint('login', 'account')
        password = config.get('login', 'password')
        server = config.get('login', 'server')
    except configparser.NoSectionError as e:
        logger.error(f"Config file is missing section: {e.section}")
        raise
    except configparser.NoOptionError as e:
        logger.error(f"Config file is missing option: {e.option}")
        raise
    logger.info("Login configuration loaded successfully")
    return account, password, server

def get_settings(config):
    try:
        DEGREE = config.getint('settings ExtrapolateSymbols', 'degree')
        NUM_BARS = config.getint('settings ExtrapolateSymbols', 'num_bars')
        EXTRAPOLATED_TIMESTAMP = config.getint('settings ExtrapolateSymbols', 'extrapolated_timestamp')
        SLEEP_BETWEEN_SYMBOLS = config.getfloat('settings ExtrapolateSymbols', 'sleep_between_symbols')
        SLEEP_BETWEEN_CYCLES = config.getfloat('settings ExtrapolateSymbols', 'sleep_between_cycles')
        VIEW = config.getboolean('settings ExtrapolateSymbols', 'view')

    except configparser.NoSectionError as e:
        logger.error(f"Config file is missing section: {e.section}")
        raise
    except configparser.NoOptionError as e:
        logger.error(f"Config file is missing option: {e.option}")
        raise
    logger.info("Settings loaded successfully from [settings ExtrapolateSymbols]")
    return DEGREE, NUM_BARS, EXTRAPOLATED_TIMESTAMP, SLEEP_BETWEEN_SYMBOLS, SLEEP_BETWEEN_CYCLES, VIEW

def load_symbols():
    if not os.path.exists(SYMBOLS_FILE_PATH):
        logger.error(f"Symbols file not found at: {SYMBOLS_FILE_PATH}")
        raise FileNotFoundError(f"Symbols file not found at: {SYMBOLS_FILE_PATH}")

    with open(SYMBOLS_FILE_PATH, 'r') as file:
        symbols = [line.strip() for line in file.readlines()]

    logger.info(f"Symbols loaded successfully from: {SYMBOLS_FILE_PATH}")
    return symbols

def initialize_mt5(account, password, server):
    try:
        if not mt5.initialize():
            logger.error(f"initialize() failed, error code = {mt5.last_error()}")
            raise RuntimeError('initialize() failed')
        logger.info("MT5 initialized successfully")

        if not mt5.login(account, password, server):
            logger.error(f"login() failed, error code = {mt5.last_error()}")
            raise RuntimeError('login() failed')
        logger.info("Logged in to MT5 successfully")
    except Exception as e:
        logger.error(f"Exception during MT5 initialization or login: {e}")
        raise

def send_data_to_server(url, data):
    timeout = 2
    try:
        response = requests.post(url, json=data, timeout=timeout)
        response.raise_for_status()
    except requests.Timeout:
        logger.warning("Server did not respond in time. Timeout: " + str(timeout) + " s")
    except requests.RequestException as e:
        logger.error(f"Error sending data to server: {e}")

def create_schema_if_not_exists():
    create_process_schema_sql = "CREATE SCHEMA IF NOT EXISTS FOREX_PROCESSDATA;"
    timeout = 2
    try:
        response = requests.post('http://localhost:8080/SqlApi/executeSQL', data=create_process_schema_sql, timeout=timeout)
        response.raise_for_status()
        logger.info(f"Process schema creation response: {response.text}")
    except requests.Timeout:
        logger.warning("Server did not respond within " + str(timeout) + " seconds while creating schema.")
    except requests.RequestException as e:
        logger.error(f"Error creating schema: {e}")

def create_table_pricesprocessed_if_not_exists(symbol):
    create_table_sql = f"""
    CREATE TABLE IF NOT EXISTS FOREX_PROCESSDATA.PRICESPROCESSED_{symbol} (
        TIMESTAMP TIMESTAMP,
        SERVERTIME BIGINT PRIMARY KEY,
        LAST DECIMAL(20, 3)
    );
    """
    timeout = 2
    try:
        response = requests.post('http://localhost:8080/SqlApi/executeSQL', data=create_table_sql, timeout=timeout)
        response.raise_for_status()
        logger.info(f"Create PRICESPROCESSED table response for {symbol}: {response.text}")
    except requests.Timeout:
        logger.warning("Server did not respond within " + str(timeout) + " seconds while creating table.")
    except requests.RequestException as e:
        logger.error(f"Error creating table: {e}")

def fetch_data(symbol, num_bars):
    logger.info(f"Fetching historical data for symbol: {symbol}")
    timeout = 2

    try:
        # Tworzenie zapytania SQL do pobrania najnowszych danych
        fetch_sql = f"""
        SELECT SERVERTIME, LAST FROM FOREX_DATA.PRICES_{symbol} ORDER BY SERVERTIME DESC LIMIT {num_bars}; """
        response = requests.post('http://localhost:8080/SqlApi/querySQL', data=fetch_sql, timeout=timeout)
        response.raise_for_status()

        response_data = response.json()
        return response_data

    except requests.Timeout:
        logger.warning("Server did not respond within " + str(timeout) + " seconds while fetching data.")
        return None
    except requests.RequestException as e:
        logger.error(f"Error fetching data from server: {e}")
        return None

def extrapolate_values(data, degree, extrapolated_timestamp, num_bars, view):
    if len(data) < 2:  # Minimalna liczba punktów do dopasowania wielomianu
        logger.warning("Nie ma wystarczającej ilości danych, aby dopasować wielomian")
        return None

    # Tworzenie DataFrame z danych
    df = pd.DataFrame(data)

    # Dopasowanie wielomianu o określonym stopniu do danych
    poly = PolynomialFeatures(degree=degree)
    X_poly = poly.fit_transform(df['SERVERTIME'].values.reshape(-1, 1))
    model = LinearRegression()

    try:
        model.fit(X_poly, df['LAST'])
    except ValueError as e:
        logger.error(f"Błąd podczas dopasowywania modelu: {e}")
        return None

    # Określenie zakresu czasu
    start_time = df['SERVERTIME'].min()
    end_time = df['SERVERTIME'].max()

    # Generowanie wszystkich potencjalnych kroków czasowych w przedziale
    all_intervals = np.arange(start_time, end_time + 1)

    # Filtrowanie kroków czasowych, aby były zgodne z modułem czasowym
    valid_intervals = [ts for ts in all_intervals if ts % extrapolated_timestamp == 0]

    if len(valid_intervals) == 0:
        logger.warning(f"Brak wystarczających kroków czasowych do ekstrapolacji dla przedziału {start_time} - {end_time}")
        return None

    # Przekształcanie czasów na tablicę numpy
    valid_seconds = np.array(valid_intervals).reshape(-1, 1)

    # Przekształcanie na cechy wielomianowe
    valid_X_poly = poly.transform(valid_seconds)

    # Przewidywanie wartości dla równych kroków czasowych
    predicted_values = model.predict(valid_X_poly)

    # Tworzenie wynikowej listy słowników
    extrapolated_output = []
    for ts, value in zip(valid_intervals, predicted_values):
        timestamp = datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
        record = {
            "TIMESTAMP": timestamp,
            "SERVERTIME": int(ts),
            "LAST": round(value, 3)
        }
        extrapolated_output.append(record)
        if view:
            logger.info(f"Extrapolated data: {record}")  # Wyświetlanie w konsoli

    return extrapolated_output

def process_symbols(symbols, degree, num_bars, extrapolated_timestamp, sleep_between_symbols, sleep_between_cycles, view):
    timeout = 6

    while True:
        for symbol in symbols:
            logger.info(f"Processing symbol: {symbol}")
            try:
                data = fetch_data(symbol, num_bars)
                if not data:
                    logger.warning(f"Brak danych do przetworzenia dla symbolu: {symbol}")
                    continue

                extrapolated_data = extrapolate_values(data, degree, extrapolated_timestamp, num_bars, view)

                if extrapolated_data:
                    for record in extrapolated_data:
                        if view:  # Only show this log if VIEW is True
                            logger.info(f"DATA: {record}")
                        insert_sql = f"""
                            MERGE INTO FOREX_PROCESSDATA.PRICESPROCESSED_{symbol} AS target
                            USING (SELECT'{record['TIMESTAMP']}' AS TIMESTAMP, {record['SERVERTIME']} AS SERVERTIME, {record['LAST']} AS LAST) AS source
                            ON target.SERVERTIME = source.SERVERTIME
                            WHEN MATCHED THEN
                                UPDATE SET TIMESTAMP = source.TIMESTAMP, LAST = source.LAST
                            WHEN NOT MATCHED THEN
                                INSERT (TIMESTAMP, SERVERTIME, LAST) VALUES (source.TIMESTAMP, source.SERVERTIME, source.LAST);
                            """
                        try:
                            response = requests.post('http://localhost:8080/SqlApi/executeSQL', data=insert_sql, timeout=timeout)
                            response.raise_for_status()
                            if view:  # Only show this log if VIEW is True
                                logger.debug(f"Inserted or updated data: {record}")
                        except requests.Timeout:
                            logger.warning(f"Server did not respond within {timeout} seconds while inserting data: {record}")
                        except requests.RequestException as e:
                            logger.error(f"Error inserting data: {e}")
            except Exception as e:
                logger.error(f"Exception processing symbol {symbol}: {e}")
            time.sleep(sleep_between_symbols)

        logger.info("Sleeping between cycles")
        time.sleep(sleep_between_cycles)

def main():
    logger.info("Rozpoczynanie działania skryptu Process Symbols")
    config = load_config()

    create_schema_if_not_exists()
    symbols = load_symbols()
    for symbol in symbols:
        create_table_pricesprocessed_if_not_exists(symbol)

    DEGREE, NUM_BARS, EXTRAPOLATED_TIMESTAMP, SLEEP_BETWEEN_SYMBOLS, SLEEP_BETWEEN_CYCLES, VIEW = get_settings(config)
    try:
        process_symbols(symbols, DEGREE, NUM_BARS, EXTRAPOLATED_TIMESTAMP, SLEEP_BETWEEN_SYMBOLS, SLEEP_BETWEEN_CYCLES, VIEW)
    except KeyboardInterrupt:
        logger.info("Process interrupted by user")

if __name__ == "__main__":
    main()