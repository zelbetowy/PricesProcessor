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
    # Statyczna konfiguracja logowania i podstawowe ścieżki
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logger = logging.getLogger()
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    def __init__(self):
        """Inicjalizacja pól klasy"""
        self.account = None
        self.password = None
        self.server = None
        self.decimal_places = None
        self.sleep_between_symbols = None
        self.time_adjustment_hours = None
        self.symbols = []

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
            self.account = config.getint('login', 'account')
            self.password = config.get('login', 'password')
            self.server = config.get('login', 'server')
            self.logger.info("Login configuration loaded successfully")
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
        try:
            if not mt5.initialize():
                self.logger.error(f"initialize() failed, error code = {mt5.last_error()}")
                raise RuntimeError('initialize() failed')
            self.logger.info("MT5 initialized successfully")

            if not mt5.login(self.account, self.password, self.server):
                self.logger.error(f"login() failed, error code = {mt5.last_error()}")
                raise RuntimeError('login() failed')
            self.logger.info("Logged in to MT5 successfully")
        except Exception as e:
            self.logger.error(f"Exception during MT5 initialization or login: {e}")
            raise

    def fetch_symbol_info(self, symbol):
        """Funkcja do pobierania informacji o symbolu"""
        if not mt5.symbol_select(symbol, True):
            raise RuntimeError(f"Failed to select symbol: {symbol}")
        symbol_info = mt5.symbol_info_tick(symbol)
        if symbol_info is None:
            raise RuntimeError(f"Symbol info for {symbol} not found")
        return symbol_info

    def process_symbol_with_timeout(self, symbol, timeout=3):
        """Przetwarza symbol z mechanizmem timeoutu"""
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(self.fetch_symbol_info, symbol)
            try:
                return future.result(timeout=timeout)  # Zwraca wynik lub podnosi TimeoutError
            except TimeoutError:
                self.logger.warning(f"Timeout while processing symbol: {symbol}")
            except Exception as e:
                self.logger.error(f"Error while processing symbol {symbol}: {e}")
            return None

    def process_symbols(self):
        """Główna logika przetwarzania symboli"""
        while True:
            for symbol in self.symbols:
                self.logger.info(f"Processing symbol: {symbol}")

                # Pobierz dane z timeoutem
                symbol_info = self.process_symbol_with_timeout(symbol, timeout=3)
                if symbol_info is None:
                    self.logger.warning(f"Timeout or error for symbol {symbol}, skipping to next...")
                    continue  # Przejdź do kolejnego symbolu w razie błędu

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
                try:
                    response = requests.post('http://localhost:8080/api/prices/add', json=price_data, timeout=3)
                    response.raise_for_status()
                    self.logger.info(f"Price for {symbol} sent successfully: {price_data}")
                except requests.RequestException as e:
                    self.logger.error(f"Failed to send price for {symbol}: {e}")

                time.sleep(self.sleep_between_symbols)

    def main(self):
        """Główna metoda programu"""
        # Ładowanie konfiguracji i ustawień
        self.load_configurations()

        # Pobranie symboli z argumentów uruchomienia
        if len(sys.argv) > 1:
            self.symbols = sys.argv[1:]
            self.logger.info(f"Symbols received from arguments: {self.symbols}")
        else:
            self.logger.error("No symbols provided. Exiting...")
            sys.exit("No symbols provided. Exiting...")

        # Inicjalizacja MetaTrader5
        self.initialize_mt5()

        # Rozpoczęcie przetwarzania symboli
        try:
            self.process_symbols()
        except KeyboardInterrupt:
            self.logger.info("Process interrupted by user")
        finally:
            mt5.shutdown()


if __name__ == "__main__":
    processor = ProcessSymbols()
    processor.main()
