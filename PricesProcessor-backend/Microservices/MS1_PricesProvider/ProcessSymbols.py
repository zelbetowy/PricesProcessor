import time
import MetaTrader5 as mt5
import requests
import os
from datetime import datetime
import configparser
import logging
import sys
from concurrent.futures import ThreadPoolExecutor, TimeoutError


class ProcessSymbols:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    def __init__(self, config_id, symbols):
        """Inicjalizacja pól klasy"""
        self.config_id = config_id  # Wskazuje, który config użyć (np. config1, config2)
        self.symbols = symbols  # Lista symboli do przetwarzania
        self.account = None
        self.password = None
        self.server = None
        self.decimal_places = None
        self.sleep_between_symbols = None
        self.time_adjustment_hours = None
        self.logger = None  # Logger będzie zainicjalizowany w `setup_logger`

    def setup_logger(self):
        """Konfiguruje logger"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger()
        self.logger.info(f"Logger initialized for provider_{self.config_id}")

    def load_configurations(self):
        """Ładuje konfigurację z dwóch plików: logins.ini i config.ini"""
        config = configparser.ConfigParser()
        login_path = os.path.join(self.BASE_DIR, '../config/logins.ini')
        config_path = os.path.join(self.BASE_DIR, '../config/config.ini')

        # Wczytanie logins.ini
        if not os.path.exists(login_path):
            self.logger.error(f"Login config file not found at: {login_path}")
            raise FileNotFoundError(f"Login config file not found at: {login_path}")
        config.read(login_path)
        try:
            self.account = config.getint('login', f'account{self.config_id}')
            self.password = config.get('login', f'password{self.config_id}')
            self.server = config.get('login', f'server{self.config_id}')
            self.logger.info(f"Login configuration loaded successfully for account{self.config_id}")
        except (configparser.NoSectionError, configparser.NoOptionError) as e:
            self.logger.error(f"Error loading login info: {e}")
            raise

        # Wczytanie config.ini
        if not os.path.exists(config_path):
            self.logger.error(f"Config file not found at: {config_path}")
            raise FileNotFoundError(f"Config file not found at: {config_path}")
        config.read(config_path)
        try:
            self.decimal_places = config.getint('settings process', 'decimal_places')
            self.sleep_between_symbols = config.getfloat('settings process', 'sleep_between_symbols')
            self.time_adjustment_hours = config.getint('settings process', 'time_adjustment_hours')
            self.logger.info("Processing settings loaded successfully")
        except (configparser.NoSectionError, configparser.NoOptionError) as e:
            self.logger.error(f"Error loading settings: {e}")
            raise

    def initialize_mt5(self):
        """Inicjalizacja i logowanie do MetaTrader5"""
        if not mt5.initialize():
            self.logger.error(f"initialize() failed, error code = {mt5.last_error()}")
            raise RuntimeError('initialize() failed')
        self.logger.info("MT5 initialized successfully")

        if not mt5.login(self.account, self.password, self.server):
            self.logger.error(f"login() failed, error code = {mt5.last_error()}")
            raise RuntimeError('login() failed')
        self.logger.info("Logged in to MT5 successfully")

    def fetch_symbol_info(self, symbol):
        """Funkcja do pobierania informacji o symbolu"""
        if not mt5.symbol_select(symbol, True):
            raise RuntimeError(f"Failed to select symbol: {symbol}")
        symbol_info = mt5.symbol_info_tick(symbol)
        if symbol_info is None:
            raise RuntimeError(f"Symbol info for {symbol} not found")
        return symbol_info

    def process_symbols(self):
        """Główna logika przetwarzania symboli"""
        while True:
            for symbol in self.symbols:
                self.logger.info(f"Processing symbol: {symbol}")
                try:
                    # Pobierz dane o symbolu
                    symbol_info = self.fetch_symbol_info(symbol)
                    bid = round(symbol_info.bid, self.decimal_places)
                    ask = round(symbol_info.ask, self.decimal_places)
                    last = round((bid + ask) / 2, self.decimal_places)
                    server_time_with_adjustment = symbol_info.time + (self.time_adjustment_hours * 3600)
                    server_time_adjusted = datetime.utcfromtimestamp(server_time_with_adjustment)

                    # Tworzenie obiektu danych do wysłania
                    price_data = {
                        "tag": symbol,
                        "timestamp": server_time_adjusted.strftime('%Y-%m-%dT%H:%M:%S'),
                        "serverTimeRaw": int(server_time_with_adjustment),
                        "bid": bid,
                        "ask": ask,
                        "last": last,
                        "server": self.server
                    }

                    # Wysyłanie danych do endpointa Spring Boot
                    response = requests.post('http://localhost:8080/api/prices/add', json=price_data, timeout=3)
                    response.raise_for_status()
                    self.logger.info(f"Price for {symbol} sent successfully: {price_data}")
                except requests.RequestException as e:
                    self.logger.error(f"Failed to send price for {symbol}: {e}")
                except Exception as e:
                    self.logger.error(f"Error processing symbol {symbol}: {e}")

                # Odczekaj między przetwarzaniem kolejnych symboli
                time.sleep(self.sleep_between_symbols)

    def main(self):
        """Główna metoda programu"""
        self.setup_logger()
        self.load_configurations()
        self.initialize_mt5()
        try:
            self.process_symbols()
        except KeyboardInterrupt:
            self.logger.info("Process interrupted by user")
        finally:
            mt5.shutdown()


if __name__ == "__main__":
    # Parsowanie argumentów
    if len(sys.argv) < 3:
        print("Usage: script.py configX symbol1 symbol2 ...")
        sys.exit("Error: Not enough arguments provided.")

    config_arg = sys.argv[1]
    if not config_arg.startswith("config"):
        sys.exit("Error: First argument must specify the config (e.g., config1, config2).")
    config_id = config_arg.replace("config", "")

    try:
        config_id = int(config_id)
    except ValueError:
        sys.exit("Error: Config ID must be an integer after 'config'.")

    symbols = sys.argv[2:]
    processor = ProcessSymbols(config_id=config_id, symbols=symbols)
    processor.main()
