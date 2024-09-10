import MetaTrader5 as mt5
import logging
from datetime import datetime, timedelta

# Konfiguracja logowania
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

def initialize_mt5():
    if not mt5.initialize():
        logger.error(f"initialize() failed, error code = {mt5.last_error()}")
        raise RuntimeError('initialize() failed')
    logger.info("MT5 initialized successfully")

def fetch_and_display_data(symbol, timeframe, num_bars):
    logger.info(f"Fetching historical data for symbol: {symbol}")
    rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, num_bars)

    if rates is None:
        logger.error(f"Failed to fetch historical data for symbol: {symbol}, error code = {mt5.last_error()}")
        return

    logger.info(f"Fetched {len(rates)} historical data points for symbol: {symbol}")

    # Wyświetlanie danych
    for rate in rates:
        timestamp = datetime.fromtimestamp(rate['time'])
        logger.info(f"Time: {timestamp}, Open: {rate['open']}, High: {rate['high']}, Low: {rate['low']}, Close: {rate['close']}, Volume: {rate['tick_volume']}")

def main():
    initialize_mt5()

    symbol = "BTCUSD"  # Możesz zmienić na dowolny symbol
    timeframe = mt5.TIMEFRAME_M5  # Interwał czasowy
    num_bars = 10  # Liczba świec do pobrania

    fetch_and_display_data(symbol, timeframe, num_bars)

    mt5.shutdown()  # Zakończenie połączenia z MetaTrader 5

if __name__ == "__main__":
    main()