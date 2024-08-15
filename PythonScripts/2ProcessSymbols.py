import time
import MetaTrader5 as mt5
import requests
import os
from datetime import datetime
import configparser
import logging

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
        decimal_places = config.getint('settings process', 'decimal_places')
        sleep_between_symbols = config.getfloat('settings process', 'sleep_between_symbols')
        sleep_between_cycles = config.getfloat('settings process', 'sleep_between_cycles')
        view = config.getboolean('settings process', 'view')
        time_adjustment_hours = config.getint('settings process', 'time_adjustment_hours')
    except configparser.NoSectionError as e:
        logger.error(f"Config file is missing section: {e.section}")
        raise
    except configparser.NoOptionError as e:
        logger.error(f"Config file is missing option: {e.option}")
        raise
    logger.info("Settings loaded successfully")
    return decimal_places, sleep_between_symbols, sleep_between_cycles, view, time_adjustment_hours

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

def send_data_to_server(url, data, timeout=4):
    try:
        response = requests.post(url, json=data, timeout=timeout)
        response.raise_for_status()
    except requests.RequestException as e:
        logger.error(f"Error sending data to server: {e}")
        raise

def create_schema_if_not_exists():
    create_schema_sql = "CREATE SCHEMA IF NOT EXISTS FOREX_DATA;"
    try:
        response = requests.post('http://localhost:8080/SqlApi/executeSQL', data=create_schema_sql, timeout=4)
        response.raise_for_status()
    except requests.RequestException as e:
        logger.error(f"Error creating schema: {e}")
        raise

def create_table_prices_if_not_exists(symbol):
    table_name = symbol.replace(".","")
    create_table_sql = f"""
    CREATE TABLE IF NOT EXISTS FOREX_DATA.PRICES_{table_name} (
        ID IDENTITY PRIMARY KEY,
        TIMESTAMP TIMESTAMP,
        SERVERTIME BIGINT,
        BID DECIMAL(20, 3),
        ASK DECIMAL(20, 3),
        LAST DECIMAL(20, 3)
    );
    """
    try:
        response = requests.post('http://localhost:8080/SqlApi/executeSQL', data=create_table_sql, timeout=4)
        response.raise_for_status()
    except requests.RequestException as e:
        logger.error(f"Error creating table: {e}")
        raise

def create_thick_table_if_not_exists():
    create_thick_table_sql = """
    CREATE TABLE IF NOT EXISTS FOREX_DATA.THICK (
        SYMBOL VARCHAR(50) PRIMARY KEY,
        TIMESTAMP TIMESTAMP,
        SERVERTIME BIGINT,
        BID DECIMAL(20, 3),
        ASK DECIMAL(20, 3),
        LAST DECIMAL(20, 3)
    );
    """
    try:
        response = requests.post('http://localhost:8080/SqlApi/executeSQL', data=create_thick_table_sql, timeout=4)
        response.raise_for_status()
    except requests.RequestException as e:
        logger.error(f"Error creating THICK table: {e}")
        raise

def process_symbols(symbols, time_adjustment_hours, decimal_places, sleep_between_symbols, sleep_between_cycles, view):
    while True:
        for symbol in symbols:
            if not mt5.symbol_select(symbol, True):
                logger.error(f"Failed to select symbol: {symbol}")
                continue

            symbol_info = mt5.symbol_info_tick(symbol)
            if symbol_info is None:
                logger.error(f"{symbol} not found, cannot call symbol_info_tick()")
                continue

            bid = round(symbol_info.bid, decimal_places)
            ask = round(symbol_info.ask, decimal_places)
            last = round((bid + ask) / 2, decimal_places)

            # Pobranie serwera czasu i dostosowanie
            server_time_raw = symbol_info.time
            # print(server_time_raw)
            server_time_with_adjustment = server_time_raw + (time_adjustment_hours * 3600)  # Dodanie przesunięcia w sekundach
            # print(server_time_with_adjustment)

            # Generowanie timestampu na podstawie już dostosowanego serwera czasu
            server_time_adjusted = datetime.utcfromtimestamp(server_time_with_adjustment)

            data = {
                "symbol": symbol,
                "timestamp": server_time_adjusted.strftime('%Y-%m-%d %H:%M:%S'),
                "server_time_raw": int(server_time_with_adjustment),
                "bid": bid,
                "ask": ask,
                "last": last
            }

            if view:
                logger.info(f"Symbol: {symbol}, Time: {server_time_adjusted.strftime('%Y-%m-%d %H:%M:%S')}, Server Time Adjusted: {server_time_with_adjustment}, Bid: {bid}, Ask: {ask}, Last: {last}")

            # Wstawianie danych do tabeli PRICES
            merge_sql_prices = f"""
            MERGE INTO FOREX_DATA.PRICES_{(symbol.replace(".",""))} (TIMESTAMP, SERVERTIME, BID, ASK, LAST)
            KEY(TIMESTAMP)
            VALUES (PARSEDATETIME('{data['timestamp']}', 'yyyy-MM-dd HH:mm:ss'), {data['server_time_raw']}, {data['bid']}, {data['ask']}, {data['last']});
            """
            try:
                response = requests.post('http://localhost:8080/SqlApi/executeSQL', data=merge_sql_prices, timeout=4)
                response.raise_for_status()
            except requests.RequestException as e:
                logger.error(f"Server time out: {e}")
                continue  # Przejście do następnego symbolu

            # Wstawianie danych do tabeli THICK
            merge_sql_thick = f"""
            MERGE INTO FOREX_DATA.THICK (SYMBOL, TIMESTAMP, SERVERTIME, BID, ASK, LAST)
            KEY(SYMBOL)
            VALUES ('{data['symbol']}', PARSEDATETIME('{data['timestamp']}', 'yyyy-MM-dd HH:mm:ss'), {data['server_time_raw']}, {data['bid']}, {data['ask']}, {data['last']});
            """
            try:
                response = requests.post('http://localhost:8080/SqlApi/executeSQL', data=merge_sql_thick, timeout=4)
                response.raise_for_status()
            except requests.RequestException as e:
                logger.error(f"Server time out: {e}")
                continue  # Przejście do następnego symbolu

            time.sleep(sleep_between_symbols)  # Opóźnienie między każdym symbolem
        time.sleep(sleep_between_cycles)  # Opóźnienie po przetworzeniu wszystkich symboli

def main():
    logger.info("Rozpoczynanie działania skryptu Process Symbols")
    config = load_config()
    account, password, server = get_login_info(config)
    decimal_places, sleep_between_symbols, sleep_between_cycles, view, time_adjustment_hours = get_settings(config)
    symbols = load_symbols()

    initialize_mt5(account, password, server)

    create_schema_if_not_exists()
    create_thick_table_if_not_exists()

    for symbol in symbols:
        create_table_prices_if_not_exists(symbol)

    try:
        process_symbols(symbols, time_adjustment_hours, decimal_places, sleep_between_symbols, sleep_between_cycles, view)
    except KeyboardInterrupt:
        logger.info("Process interrupted by user")
    finally:
        mt5.shutdown()  # Zakończenie połączenia z MetaTrader 5

if __name__ == "__main__":
    main()
