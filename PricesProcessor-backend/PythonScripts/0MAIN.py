import time
import MetaTrader5 as mt5
import requests
import os
from datetime import datetime, timedelta
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
        timeframe_str = config.get('settings', 'timeframe')
        timeframe = getattr(mt5, timeframe_str, None)
        if timeframe is None:
            raise ValueError(f"Invalid timeframe: {timeframe_str}")

        num_bars = config.getint('settings', 'num_bars')
        decimal_places = config.getint('settings', 'decimal_places')
        home_timeframe = config.getint('settings', 'home_timeframe')
        sleep_between_symbols = config.getfloat('settings', 'sleep_between_symbols')
        sleep_between_cycles = config.getfloat('settings', 'sleep_between_cycles')
        view = config.getboolean('settings', 'view')
        time_adjustment_hours = config.getint('settings', 'time_adjustment_hours')
    except configparser.NoSectionError as e:
        logger.error(f"Config file is missing section: {e.section}")
        raise
    except configparser.NoOptionError as e:
        logger.error(f"Config file is missing option: {e.option}")
        raise
    logger.info("Settings loaded successfully")
    return timeframe, num_bars, decimal_places, home_timeframe, sleep_between_symbols, sleep_between_cycles, view, time_adjustment_hours

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
    try:
        response = requests.post(url, json=data)
        response.raise_for_status()
    except requests.RequestException as e:
        logger.error(f"Error sending data to server: {e}")
        raise

def create_table_if_not_exists(symbol):
    create_table_sql = f"""
    CREATE TABLE IF NOT EXISTS FOREX_DATA.PRICES_{symbol} (
        ID IDENTITY PRIMARY KEY,
        TIMESTAMP TIMESTAMP,
        SYMBOL VARCHAR(50),
        BID DECIMAL(20, 10),
        ASK DECIMAL(20, 10),
        LAST DECIMAL(20, 10)
    );
    """
    try:
        response = requests.post('http://localhost:8080/SqlApi/executeSQL', data=create_table_sql)
        response.raise_for_status()
    except requests.RequestException as e:
        logger.error(f"Error sending data to server: {e}")
        raise

def fetch_historical_data(symbols, timeframe, num_bars, time_adjustment_hours):
    for symbol in symbols:
        logger.info(f"Fetching historical data for symbol: {symbol}")
        create_table_if_not_exists(symbol)
        try:
            rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, num_bars)
            if rates is None:
                logger.error(f"Failed to fetch historical data for symbol: {symbol}")
                continue

            logger.info(f"Fetched {len(rates)} historical data points for symbol: {symbol}")
            data = []
            for rate in rates:
                timestamp = datetime.fromtimestamp(rate['time']) + timedelta(hours=time_adjustment_hours)
                data.append({
                    "timestamp": timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                    "symbol": symbol,
                    "bid": rate['open'],
                    "ask": rate['close'],
                    "last": (rate['open'] + rate['close']) / 2
                })
            send_data_to_server('http://localhost:8080/api/saveHistoricalData', {"data": data})
        except Exception as e:
            logger.error(f"Exception fetching historical data for symbol {symbol}: {e}")
            time.sleep(2)  # Opóźnienie przed kontynuacją

def process_symbols(symbols, startProcessingTime, home_timeframe, time_adjustment_hours, decimal_places, sleep_between_symbols, sleep_between_cycles, view):
    next_save_times = {symbol: startProcessingTime + timedelta(seconds=home_timeframe) for symbol in symbols}

    while True:
        logger.info("Starting a new cycle of symbol processing")
        thick_data = []
        for symbol in symbols:
            logger.info(f"Processing symbol: {symbol}")
            create_table_if_not_exists(symbol)
            if not mt5.symbol_select(symbol, True):
                logger.error(f"Failed to select symbol: {symbol}")
                continue

            attempts = 0
            while attempts < 5:  # Maksymalnie 5 prób
                symbol_info = mt5.symbol_info_tick(symbol)
                if symbol_info is not None:
                    break
                attempts += 1
                logger.warning(f"Server not responding for {symbol}, attempt {attempts}")
                time.sleep(2)  # Czekanie 2 sekundy przed ponowną próbą

            if symbol_info is None:
                logger.error(f"{symbol} not found, cannot call symbol_info_tick() after {attempts} attempts")
                continue

            bid = round(symbol_info.bid, decimal_places)
            ask = round(symbol_info.ask, decimal_places)
            last = round((bid + ask) / 2, decimal_places)

            server_time = datetime.fromtimestamp(symbol_info.time) + timedelta(hours=time_adjustment_hours)
            thick_data.append({
                "symbol": symbol,
                "timestamp": server_time.strftime('%Y-%m-%d %H:%M:%S'),
                "bid": bid,
                "ask": ask,
                "last": last
            })

            if view:
                logger.info(f"Symbol: {symbol}, Time: {server_time.strftime('%Y-%m-%d %H:%M:%S')}, Bid: {bid}, Ask: {ask}, Last: {last}")

            time.sleep(sleep_between_symbols)  # Opóźnienie między każdym symbolem

        try:
            send_data_to_server('http://localhost:8080/api/saveThickData', {"data": thick_data})
        except Exception as e:
            logger.error(f"Exception sending thick data to server: {e}")
            time.sleep(1)  # Opóźnienie przed kontynuacją

        logger.info("Sleeping between cycles")
        time.sleep(sleep_between_cycles)  # Opóźnienie po przetworzeniu wszystkich symboli

def check_divisor(home_timeframe):
    if 60 % home_timeframe != 0:
        raise ValueError("home_timeframe must be a divisor of 60")


def main():
    logger.info("Rozpoczynanie działania skryptu 1MAIN")
    config = load_config()
    account, password, server = get_login_info(config)
    timeframe, num_bars, decimal_places, home_timeframe, sleep_between_symbols, sleep_between_cycles, view, time_adjustment_hours = get_settings(config)
    symbols = load_symbols()

    initialize_mt5(account, password, server)
    check_divisor(home_timeframe)
    # fetch_historical_data(symbols, timeframe, num_bars, time_adjustment_hours)

    startProcessingTime = datetime.now()
    startProcessingTime -= timedelta(seconds=startProcessingTime.second % home_timeframe, microseconds=startProcessingTime.microsecond)

    try:
        process_symbols(symbols, startProcessingTime, home_timeframe, time_adjustment_hours, decimal_places, sleep_between_symbols, sleep_between_cycles, view)
    except KeyboardInterrupt:
        logger.info("Process interrupted by user")
    finally:
        mt5.shutdown()  # Zakończenie połączenia z MetaTrader 5






if __name__ == "__main__":
    main()