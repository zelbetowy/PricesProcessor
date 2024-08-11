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
        SLEEP_BETWEEN_SYMBOLS = config.getint('settings ExtrapolateSymbols', 'sleep_between_symbols')
        SLEEP_BETWEEN_CYCLES = config.getint('settings ExtrapolateSymbols', 'sleep_between_cycles')
        VIEW = config.getboolean('settings ExtrapolateSymbols', 'view')

    except configparser.NoSectionError as e:
        logger.error(f"Config file is missing section: {e.section}")
        raise
    except configparser.NoOptionError as e:
        logger.error(f"Config file is missing option: {e.option}")
        raise
    logger.info("Settings loaded successfully from [settings fetchHistoricalData]")
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

    timeout=2
    try:
        response = requests.post(url, json=data, timeout=timeout)  # Timeouty - wiadomo
        response.raise_for_status()
    except requests.Timeout:
        logger.warning("Server did not respond in time ." + " " + timeout + " s")
    except requests.RequestException as e:
        logger.error(f"Error sending data to server: {e}")

def create_schema_if_not_exists():
    create_process_schema_sql = "CREATE SCHEMA IF NOT EXISTS FOREX_PROCESSDATA;"
    timeout=2
    try:
        response = requests.post('http://localhost:8080/SqlApi/executeSQL', data=create_process_schema_sql, timeout=timeout)
        response.raise_for_status()
        logger.info(f"Process schema creation response: {response.text}")
    except requests.Timeout:
        logger.warning("Server did not respond within " + timeout + " seconds while creating schema.")
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
    timeout=2
    try:
        response = requests.post('http://localhost:8080/SqlApi/executeSQL', data=create_table_sql, timeout=timeout)
        response.raise_for_status()
        logger.info(f"Create PRICESPROCESSED table response for {symbol}: {response.text}")
    except requests.Timeout:
        logger.warning("Server did not respond within " + timeout + " seconds while creating table.")
    except requests.RequestException as e:
        logger.error(f"Error creating table: {e}")

def fetch_Data(symbol, num_bars):
    logger.info(f"Fetching historical data for symbol: {symbol}")
    timeout=2
    resultData = []

    try:
        fetch_sql = f"""
        SELECT TIMESTAMP LAST FROM FOREX_DATA.PRICES_{symbol} ORDER BY TIMESTAMP DESC LIMIT {num_bars}; """
        response = requests.post('http://localhost:8080/SqlApi/querySQL', data=fetch_sql, timeout=timeout)
        response.raise_for_status()
        response_data = response.json()
        resultData=response_data
        return resultData
    except requests.Timeout:
        logger.warning("Server did not respond within " + timeout  + " seconds while fetching data.")
        return None
    except requests.RequestException as e:
        logger.error(f"Error fetching data from server: {e}")
        return None

def extrapolate_values(symbol, data, degree, extrapolated_timestamp, num_bars, view):
    if len(data) < num_bars:
        logger.warning(f"Nie ma wystarczającej ilości danych, aby dopasować wielomian dla {symbol}")
        return None

    # Tworzenie DataFrame z danych
    df = pd.DataFrame(data)
    df['TIMESTAMP'] = pd.to_datetime(df['TIMESTAMP']).dt.tz_localize(None)
    df['TIME_SECONDS'] = (df['TIMESTAMP'] - df['TIMESTAMP'].min()).dt.total_seconds()

    # Wybieranie ostatnich num_bars kroków czasowych
    last_bars = df.tail(num_bars)

    # Sprawdzanie, czy w kolumnie 'LAST' nie ma wartości NaN
    if last_bars['LAST'].isna().any():
        logger.warning(f"Brakujące wartości w kolumnie 'LAST' dla {symbol}")
        return None

    # Dopasowanie wielomianu o określonym stopniu do danych
    poly = PolynomialFeatures(degree=degree)

    # Przekształcenie TIME_SECONDS do odpowiedniego kształtu
    X_poly = poly.fit_transform(last_bars['TIME_SECONDS'].values.reshape(-1, 1))

    model = LinearRegression()

    try:
        model.fit(X_poly, last_bars['LAST'])
    except ValueError as e:
        logger.error(f"Błąd podczas dopasowywania modelu dla {symbol}: {e}")
        return None

    # Określenie zakresu czasu
    start_time = last_bars['TIMESTAMP'].min()
    end_time = last_bars['TIMESTAMP'].max()

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
    extrapolated_output = []
    for ts, value in zip(equal_intervals, predicted_values):
        if (ts.second % extrapolated_timestamp) == 0:
            record = {
                "SYMBOL": symbol,
                "TIMESTAMP": ts.strftime('%Y-%m-%d %H:%M:%S'),
                "LAST": round(value, 3)
            }
            extrapolated_output.append(record)
            logger.info(f"Extrapolated data: {record}")  # Wyświetlanie w konsoli
    return extrapolated_output

def process_symbols(symbols, degree, num_bars, extrapolated_timestamp, sleep_between_symbols, sleep_between_cycles, view):
    timeout = 6

    while True:
        for symbol in symbols:
            logger.info(f"Processing symbol: {symbol}")
            try:
                data = fetch_Data(symbol, num_bars)
                extrapolated_data = []
                extrapolated_data = extrapolate_values(symbol, data, degree, extrapolated_timestamp, num_bars, view)

                if extrapolated_data:
                    for record in extrapolated_data:
                            # Wyświetlenie danych ekstrapolowanych przed wstawieniem do bazy danych
                            logger.info(f"DATA: {record}")
                            insert_sql = f"""
                            INSERT INTO FOREX_PROCESSDATA.PRICESPROCESSED_{symbol} (TIMESTAMP, LAST)
                            SELECT '{record['TIMESTAMP']}', {record['LAST']}
                            WHERE NOT EXISTS (
                                SELECT 1 FROM FOREX_PROCESSDATA.PRICESPROCESSED_{symbol} WHERE TIMESTAMP = '{record['TIMESTAMP']}'
                            );
                            """
                            try:
                                response = requests.post('http://localhost:8080/SqlApi/executeSQL', data=insert_sql, timeout=timeout)
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
    config = load_config()
    # account, password, server = get_login_info(config)
    # initialize_mt5(account, password, server)

    create_schema_if_not_exists()
    symbols = load_symbols()
    for symbol in symbols:
        create_table_pricesprocessed_if_not_exists(symbol)


    DEGREE, NUM_BARS, EXTRAPOLATED_TIMESTAMP, SLEEP_BETWEEN_SYMBOLS, SLEEP_BETWEEN_CYCLES, VIEW = get_settings(config)
    try:
        process_symbols(symbols, DEGREE, NUM_BARS, EXTRAPOLATED_TIMESTAMP, SLEEP_BETWEEN_SYMBOLS, SLEEP_BETWEEN_CYCLES, VIEW)
    except KeyboardInterrupt:
        logger.info("Process interrupted by user")

    # mt5.shutdown()  # Zakończenie połączenia z MetaTrader 5

if __name__ == "__main__":
    main()