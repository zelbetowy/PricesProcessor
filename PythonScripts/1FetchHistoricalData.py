import time
import requests
import os
from datetime import datetime, timedelta
import configparser
import logging
import MetaTrader5 as mt5
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

def get_fetch_historical_data_settings(config):
    try:
        degree = config.getint('settings fetchHistoricalData', 'degree')
        num_bars = config.getint('settings fetchHistoricalData', 'num_bars')
        timeframe_str = config.get('settings fetchHistoricalData', 'timeframe')
        timeframe = getattr(mt5, timeframe_str, None)
        if timeframe is None:
            raise ValueError(f"Invalid timeframe: {timeframe_str}")
        extrapolated_timestamp = config.getint('settings fetchHistoricalData', 'extrapolated_timestamp')
        view = config.getboolean('settings fetchHistoricalData', 'view')
    except configparser.NoSectionError as e:
        logger.error(f"Config file is missing section: {e.section}")
        raise
    except configparser.NoOptionError as e:
        logger.error(f"Config file is missing option: {e.option}")
        raise
    logger.info("Settings loaded successfully from [settings fetchHistoricalData]")
    return degree, num_bars, timeframe, extrapolated_timestamp, view

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

def create_schema_if_not_exists():
    create_process_schema_sql = "CREATE SCHEMA IF NOT EXISTS FOREX_PROCESSDATA;"
    try:
        logger.debug(f"Executing SQL: {create_process_schema_sql}")
        response = requests.post('http://localhost:8080/SqlApi/executeSQL', data={'sql': create_process_schema_sql})
        response.raise_for_status()
        logger.info(f"Process schema creation response: {response.text}")
    except requests.RequestException as e:
        logger.error(f"Error creating schema: {e}")
        raise

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
        logger.debug(f"Executing SQL: {create_table_sql}")
        response = requests.post('http://localhost:8080/SqlApi/executeSQL', data={'sql': create_table_sql})
        response.raise_for_status()
        logger.info(f"Create PRICESPROCESSED table response for {symbol}: {response.text}")
    except requests.RequestException as e:
        logger.error(f"Error creating table: {e}")
        raise

def fetch_historical_data(symbol, timeframe, num_bars, time_adjustment_hours, view):
    logger.info(f"Fetching historical data for symbol: {symbol}")
    try:
        rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, num_bars)
        if rates is None:
            logger.error(f"Failed to fetch historical data for symbol: {symbol}")
            return None

        logger.info(f"Fetched {len(rates)} historical data points for symbol: {symbol}")
        data = []
        for rate in rates:
            timestamp = datetime.fromtimestamp(rate['time']) + timedelta(hours=time_adjustment_hours)
            data.append({
                "timestamp": timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                "bid": rate['open'],
                "ask": rate['close'],
                "last": (rate['open'] + rate['close']) / 2
            })
            if view:
                logger.info(f"Symbol: {symbol}, Timestamp: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}, Bid: {rate['open']}, Ask: {rate['close']}, Last: {(rate['open'] + rate['close']) / 2}")
        return data
    except Exception as e:
        logger.error(f"Exception fetching historical data for symbol {symbol}: {e}")
        return None

def extrapolate_values(symbol, data, degree, extrapolated_timestamp, view):
    if len(data) < degree:
        logger.warning(f"Not enough data to fit the polynomial for {symbol}")
        return None

    df = pd.DataFrame(data)
    df['timestamp'] = pd.to_datetime(df['timestamp']).dt.tz_localize(None)  # Ensure tz-naive datetime
    df['time_seconds'] = (df['timestamp'] - df['timestamp'].min()).dt.total_seconds()

    poly = PolynomialFeatures(degree=degree)
    X_poly = poly.fit_transform(df['time_seconds'].values.reshape(-1, 1))
    model = LinearRegression()
    model.fit(X_poly, df['last'])

    latest_timestamp = df['timestamp'].max()
    future_timestamps = []
    future_values = []

    for timestamp in df['timestamp']:
        for i in range(0, 300, extrapolated_timestamp):  # 5 minut = 300 sekund
            future_timestamp = timestamp + timedelta(seconds=i)
            future_seconds = (future_timestamp - df['timestamp'].min()).total_seconds()
            future_X_poly = poly.transform(np.array(future_seconds).reshape(-1, 1))
            future_value = model.predict(future_X_poly)
            future_timestamps.append(future_timestamp)
            future_values.append(future_value[0])

    extrapolated_data = []
    for ts, value in zip(future_timestamps, future_values):
        extrapolated_data.append({
            "symbol": symbol,
            "timestamp": ts.strftime('%Y-%m-%d %H:%M:%S'),
            "last": round(value, 3)
        })
        if view:
            logger.info(f"Symbol: {symbol}, Timestamp: {ts.strftime('%Y-%m-%d %H:%M:%S')}, Last: {round(value, 3)}")
    return extrapolated_data

def process_symbol(symbol, degree, num_bars, timeframe, extrapolated_timestamp, view):
    create_table_pricesprocessed_if_not_exists(symbol)
    data = fetch_historical_data(symbol, timeframe, num_bars, -3, view)
    if data:
        extrapolated_data = extrapolate_values(symbol, data, degree, extrapolated_timestamp, view)
        if extrapolated_data:
            # Batch insert for multiple records
            values = ", ".join([f"('{record['timestamp']}', {record['last']})" for record in extrapolated_data])
            insert_sql = f"""
            INSERT INTO FOREX_PROCESSDATA.PRICESPROCESSED_{symbol} (TIMESTAMP, LAST)
            VALUES {values}
            ON DUPLICATE KEY UPDATE LAST=VALUES(LAST);
            """
            logger.debug(f"Generated SQL: {insert_sql}")
            try:
                response = requests.post('http://localhost:8080/SqlApi/executeSQL', data={'sql': insert_sql})
                response.raise_for_status()
                logger.debug(f"Inserted data for {symbol}")
            except requests.RequestException as e:
                logger.error(f"Error inserting data for {symbol}: {e}")

def main():
    logger.info("Rozpoczynanie działania skryptu Fetch and Process Historical Data")
    config = load_config()
    account, password, server = get_login_info(config)
    degree, num_bars, timeframe, extrapolated_timestamp, view = get_fetch_historical_data_settings(config)
    symbols = load_symbols()

    initialize_mt5(account, password, server)
    create_schema_if_not_exists()

    if symbols:
        process_symbol(symbols[0], degree, num_bars, timeframe, extrapolated_timestamp, view)

    mt5.shutdown()  # Zakończenie połączenia z MetaTrader 5

if __name__ == "__main__":
    main()
