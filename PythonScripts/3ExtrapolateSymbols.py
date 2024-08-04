import time
import requests
import os
from datetime import datetime, timedelta
import logging
import numpy as np
import pandas as pd
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression

# Konfiguracja logowania
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

# Ścieżki do plików
SYMBOLS_FILE_PATH = 'D:/#SOFT/JAVA/Kutarate/Kutarate/PythonScripts/config/symbols.txt'

# Zmienne na początku programu
DEGREE = 4
NUM_BARS = 10
EXTRAPOLATED_TIMESTAMP = 5  # Example value: 5 seconds
SLEEP_BETWEEN_SYMBOLS = 1
SLEEP_BETWEEN_CYCLES = 1

def load_symbols():
    if not os.path.exists(SYMBOLS_FILE_PATH):
        logger.error(f"Symbols file not found at: {SYMBOLS_FILE_PATH}")
        raise FileNotFoundError(f"Symbols file not found at: {SYMBOLS_FILE_PATH}")

    with open(SYMBOLS_FILE_PATH, 'r') as file:
        symbols = [line.strip() for line in file.readlines()]

    logger.info(f"Symbols loaded successfully from: {SYMBOLS_FILE_PATH}")
    return symbols

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
        response = requests.post('http://localhost:8080/SqlApi/executeSQL', data=create_process_schema_sql)
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
        response = requests.post('http://localhost:8080/SqlApi/executeSQL', data=create_table_sql)
        response.raise_for_status()
        logger.info(f"Create PRICESPROCESSED table response for {symbol}: {response.text}")
    except requests.RequestException as e:
        logger.error(f"Error creating table: {e}")
        raise

def fetch_last_n_bars(symbol, num_bars):
    fetch_sql = f"""
    SELECT TIMESTAMP, BID, ASK, LAST FROM FOREX_DATA.PRICES_{symbol} ORDER BY TIMESTAMP DESC LIMIT {num_bars};
    """
    try:
        response = requests.post('http://localhost:8080/SqlApi/querySQL', data=fetch_sql)
        response.raise_for_status()
        response_data = response.json()
        return response_data
    except requests.RequestException as e:
        logger.error(f"Error fetching data from server: {e}")
        raise
    except ValueError as e:
        logger.error(f"Error parsing JSON response: {e}")
        logger.error(f"Server response: {response.text}")
        raise

def extrapolate_values(symbol, data, degree, extrapolated_timestamp):
    if len(data) < degree:
        logger.warning(f"Not enough data to fit the polynomial for {symbol}")
        return None

    df = pd.DataFrame(data)
    df['timestamp'] = pd.to_datetime(df['TIMESTAMP']).dt.tz_localize(None)  # Ensure tz-naive datetime
    df['time_seconds'] = (df['timestamp'] - df['timestamp'].min()).dt.total_seconds()

    poly = PolynomialFeatures(degree=degree)
    X_poly = poly.fit_transform(df['time_seconds'].values.reshape(-1, 1))
    model = LinearRegression()
    model.fit(X_poly, df['LAST'])

    latest_timestamp = df['timestamp'].max()
    latest_seconds = (latest_timestamp - datetime.combine(latest_timestamp.date(), datetime.min.time())).total_seconds()
    rounded_seconds = latest_seconds - (latest_seconds % extrapolated_timestamp)
    base_time = datetime.combine(latest_timestamp.date(), datetime.min.time()) + timedelta(seconds=rounded_seconds)

    future_timestamps = [base_time - timedelta(seconds=i * extrapolated_timestamp) for i in range(5)]
    future_seconds = [(ts - df['timestamp'].min()).total_seconds() for ts in future_timestamps]
    future_X_poly = poly.transform(np.array(future_seconds).reshape(-1, 1))
    future_values = model.predict(future_X_poly)

    extrapolated_data = []
    for ts, value in zip(future_timestamps, future_values):
        extrapolated_data.append({
            "symbol": symbol,
            "timestamp": ts.strftime('%Y-%m-%d %H:%M:%S'),
            "last": round(value, 3)
        })
    return extrapolated_data

def process_symbols(symbols, degree, num_bars, extrapolated_timestamp, sleep_between_symbols, sleep_between_cycles):
    for symbol in symbols:
        create_table_pricesprocessed_if_not_exists(symbol)

    while True:
        for symbol in symbols:
            logger.info(f"Processing symbol: {symbol}")
            try:
                data = fetch_last_n_bars(symbol, num_bars)
                if data:
                    extrapolated_data = extrapolate_values(symbol, data, degree, extrapolated_timestamp)
                    if extrapolated_data:
                        for record in extrapolated_data:
                            insert_sql = f"""
                            INSERT INTO FOREX_PROCESSDATA.PRICESPROCESSED_{symbol} (TIMESTAMP, LAST)
                            SELECT '{record['timestamp']}', {record['last']}
                            WHERE NOT EXISTS (
                                SELECT 1 FROM FOREX_PROCESSDATA.PRICESPROCESSED_{symbol} WHERE TIMESTAMP = '{record['timestamp']}'
                            );
                            """
                            try:
                                response = requests.post('http://localhost:8080/SqlApi/executeSQL', data=insert_sql)
                                response.raise_for_status()
                                logger.debug(f"Inserted data: {record}")
                            except requests.RequestException as e:
                                logger.error(f"Error inserting data: {e}")
            except Exception as e:
                logger.error(f"Exception processing symbol {symbol}: {e}")
            time.sleep(sleep_between_symbols)

        logger.info("Sleeping between cycles")
        time.sleep(sleep_between_cycles)

def main():
    logger.info("Rozpoczynanie działania skryptu Process Symbols")
    symbols = load_symbols()

    create_schema_if_not_exists()

    try:
        process_symbols(symbols, DEGREE, NUM_BARS, EXTRAPOLATED_TIMESTAMP, SLEEP_BETWEEN_SYMBOLS, SLEEP_BETWEEN_CYCLES)
    except KeyboardInterrupt:
        logger.info("Process interrupted by user")

if __name__ == "__main__":
    main()