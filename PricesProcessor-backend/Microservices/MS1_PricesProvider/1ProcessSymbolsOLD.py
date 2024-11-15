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

# Pobranie ścieżki do katalogu, w którym znajduje się skrypt
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Ścieżki do plików
CONFIG_FILE_PATH = os.path.join(BASE_DIR, '../config/config.ini')
SYMBOLS_FILE_PATH = os.path.join(BASE_DIR, '../config/symbols.txt')

class ProcessSymbols:
    def __init__(self):
        self.config = self.load_config()
    
    def load_config(self):
        config = configparser.ConfigParser()
        logger.info(f"Loading config file from: {CONFIG_FILE_PATH}")
        if not os.path.exists(CONFIG_FILE_PATH):
            logger.error(f"Config file not found at: {CONFIG_FILE_PATH}")
            raise FileNotFoundError(f"Config file not found at: {CONFIG_FILE_PATH}")
        config.read(CONFIG_FILE_PATH)
        logger.info(f"Config file loaded successfully from: {CONFIG_FILE_PATH}")
        return config

    def get_login_info(self):
        try:
            account = self.config.getint('login', 'account')
            password = self.config.get('login', 'password')
            server = self.config.get('login', 'server')
        except configparser.NoSectionError as e:
            logger.error(f"Config file is missing section: {e.section}")
            raise
        except configparser.NoOptionError as e:
            logger.error(f"Config file is missing option: {e.option}")
            raise
        logger.info("Login configuration loaded successfully")
        return account, password, server

    def get_settings(self):
        try:
            decimal_places = self.config.getint('settings process', 'decimal_places')
            sleep_between_symbols = self.config.getfloat('settings process', 'sleep_between_symbols')
            sleep_between_cycles = self.config.getfloat('settings process', 'sleep_between_cycles')
            view = self.config.getboolean('settings process', 'view')
            time_adjustment_hours = self.config.getint('settings process', 'time_adjustment_hours')
        except configparser.NoSectionError as e:
            logger.error(f"Config file is missing section: {e.section}")
            raise
        except configparser.NoOptionError as e:
            logger.error(f"Config file is missing option: {e.option}")
            raise
        logger.info("Settings loaded successfully")
        return decimal_places, sleep_between_symbols, sleep_between_cycles, view, time_adjustment_hours

    def load_symbols(self):
        if not os.path.exists(SYMBOLS_FILE_PATH):
            logger.error(f"Symbols file not found at: {SYMBOLS_FILE_PATH}")
            raise FileNotFoundError(f"Symbols file not found at: {SYMBOLS_FILE_PATH}")

        with open(SYMBOLS_FILE_PATH, 'r') as file:
            symbols = [line.strip() for line in file.readlines()]

        logger.info(f"Symbols loaded successfully from: {SYMBOLS_FILE_PATH}")
        return symbols

    def initialize_mt5(self, account, password, server):
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

    def send_data_to_server(self, url, data, timeout=4):
        try:
            response = requests.post(url, json=data, timeout=timeout)
            response.raise_for_status()
        except requests.RequestException as e:
            logger.error(f"Error sending data to server: {e}")
            raise

    def create_schema_if_not_exists(self):
        create_schema_sql = "CREATE SCHEMA IF NOT EXISTS FOREX_DATA;"
        try:
            response = requests.post('http://localhost:8080/SqlApi/executeSQL', data=create_schema_sql, timeout=4)
            response.raise_for_status()
        except requests.RequestException as e:
            logger.error(f"Error creating schema: {e}")
            raise

    def create_table_prices_if_not_exists(self, symbol):
        table_name = symbol.replace(".", "")
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

    def create_thick_table_if_not_exists(self):
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

    def process_symbols(self, symbols, time_adjustment_hours, decimal_places, sleep_between_symbols, sleep_between_cycles, view):
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

                server_time_with_adjustment = symbol_info.time + (time_adjustment_hours * 3600)
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
                    logger.info(f"Symbol: {symbol}, Time: {server_time_adjusted.strftime('%Y-%m-%d %H:%M:%S')}, "
                                f"Server Time Adjusted: {server_time_with_adjustment}, Bid: {bid}, Ask: {ask}, Last: {last}")

                merge_sql_prices = f"""
                MERGE INTO FOREX_DATA.PRICES_{symbol.replace(".", "")} (TIMESTAMP, SERVERTIME, BID, ASK, LAST)
                KEY(TIMESTAMP)
                VALUES (PARSEDATETIME('{data['timestamp']}', 'yyyy-MM-dd HH:mm:ss'), {data['server_time_raw']}, {data['bid']}, {data['ask']}, {data['last']});
                """
                try:
                    response = requests.post('http://localhost:8080/SqlApi/executeSQL', data=merge_sql_prices, timeout=4)
                    response.raise_for_status()
                except requests.RequestException as e:
                    logger.error(f"Server time out: {e}")
                    continue

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
                    continue

                time.sleep(sleep_between_symbols)
            time.sleep(sleep_between_cycles)

def main():
    logger.info("Rozpoczynanie działania skryptu Process Symbols")
    process = ProcessSymbols()
    account, password, server = process.get_login_info()
    decimal_places, sleep_between_symbols, sleep_between_cycles, view, time_adjustment_hours = process.get_settings()
    symbols = process.load_symbols()

    process.initialize_mt5(account, password, server)
    process.create_schema_if_not_exists()
    process.create_thick_table_if_not_exists()

    for symbol in symbols:
        process.create_table_prices_if_not_exists(symbol)

    try:
        process.process_symbols(symbols, time_adjustment_hours, decimal_places, sleep_between_symbols, sleep_between_cycles, view)
    except KeyboardInterrupt:
        logger.info("Process interrupted by user")
    finally:
        mt5.shutdown()

if __name__ == "__main__":
    main()