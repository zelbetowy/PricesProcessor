import time
import MetaTrader5 as mt5
import requests
import os
from datetime import datetime
import configparser
import logging
import sys

# Konfiguracja logowania
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

# Pobranie ścieżki do katalogu, w którym znajduje się skrypt
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Ścieżka do pliku konfiguracyjnego
CONFIG_FILE_PATH = os.path.join(BASE_DIR, '../config/config.ini')

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

    def process_symbols(self, symbols, time_adjustment_hours, decimal_places, sleep_between_symbols, sleep_between_cycles, view):
        while True:
            for symbol in symbols:
                logger.info(f"Processing symbol: {symbol}")
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
            logger.info(f"Cycle completed. Sleeping for {sleep_between_cycles} seconds.")
            time.sleep(sleep_between_cycles)

def main():
    logger.info("Starting Process Symbols script")

    # Sprawdzenie argumentów i ustawienie symboli
    if len(sys.argv) > 1:
        symbols = sys.argv[1:]  # Pobranie symboli z argumentów uruchomieniowych
        logger.info(f"Symbols received from arguments: {symbols}")
    else:
        logger.error("No symbols provided. Exiting...")
        sys.exit("No symbols provided. Exiting...")

    process = ProcessSymbols()
    account, password, server = process.get_login_info()
    decimal_places, sleep_between_symbols, sleep_between_cycles, view, time_adjustment_hours = process.get_settings()

    # Inicjalizacja MT5 i uruchomienie przetwarzania
    process.initialize_mt5(account, password, server)
    process.create_thick_table_if_not_exists()

    try:
        process.process_symbols(symbols, time_adjustment_hours, decimal_places, sleep_between_symbols, sleep_between_cycles, view)
    except KeyboardInterrupt:
        logger.info("Process interrupted by user")
    finally:
        mt5.shutdown()

if __name__ == "__main__":
    main()
