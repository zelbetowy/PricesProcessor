import os
import time
import MetaTrader5 as mt5
import requests
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
    # Inicjalizacja i metody wczytywania pozostają bez zmian

    def process_symbols(self, symbols, time_adjustment_hours, decimal_places, sleep_between_symbols, sleep_between_cycles, view):
        url = "http://localhost:8080/symbols/add"
        logger.info("Rozpoczynanie procesu symboli")
        
        while True:
            for symbol in symbols:
                logger.info(f"Przetwarzanie symbolu: {symbol}")
                if not mt5.symbol_select(symbol, True):
                    logger.error(f"Failed to select symbol: {symbol}")
                    continue

                symbol_info = mt5.symbol_info_tick(symbol)
                if symbol_info is None:
                    logger.error(f"{symbol} not found, cannot call symbol_info_tick()")
                    continue

                # Logowanie pobranych danych
                logger.info(f"Pobrano dane symbolu {symbol}: bid={symbol_info.bid}, ask={symbol_info.ask}")

                bid = round(symbol_info.bid, decimal_places)
                ask = round(symbol_info.ask, decimal_places)
                last = round((bid + ask) / 2, decimal_places)

                server_time_with_adjustment = symbol_info.time + (time_adjustment_hours * 3600)
                server_time_adjusted = datetime.utcfromtimestamp(server_time_with_adjustment)

                # Logowanie przetworzonych danych
                logger.info(f"Przetworzone dane dla {symbol}: bid={bid}, ask={ask}, last={last}")

                data = {
                    "symbol": {"id": symbol},  # Zakładam, że `symbol` odnosi się do identyfikatora Symbolu
                    "timestamp": server_time_adjusted.isoformat(),
                    "server_time_raw": int(server_time_with_adjustment),
                    "bid": str(bid),  # Konwersja do stringa, jeśli BigDecimal wymaga
                    "ask": str(ask),  # Konwersja do stringa, jeśli BigDecimal wymaga
                    "last": str(last)  # Konwersja do stringa, jeśli BigDecimal wymaga
                }

                if view:
                    logger.info(f"Symbol: {symbol}, Time: {server_time_adjusted.strftime('%Y-%m-%d %H:%M:%S')}, "
                                f"Server Time Adjusted: {server_time_with_adjustment}, Bid: {bid}, Ask: {ask}, Last: {last}")

                # Logowanie wysyłanego żądania
                logger.info(f"Wysyłanie danych do API: {data}")
                try:
                    response = requests.post(url, json=data, headers={"Content-Type": "application/json"})
                    response.raise_for_status()
                    logger.info(f"Symbol {symbol} dodany pomyślnie.")
                except requests.RequestException as e:
                    logger.error(f"Error sending data to server for symbol {symbol}: {e}")
                    continue

                time.sleep(sleep_between_symbols)
            logger.info(f"Zakończono cykl przetwarzania symboli, oczekiwanie {sleep_between_cycles} sekund.")
            time.sleep(sleep_between_cycles)