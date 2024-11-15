import time
import MetaTrader5 as mt5
import logging
from datetime import datetime

import requests

logger = logging.getLogger()

class MT5Processor:
    def __init__(self, symbols, time_adjustment_hours, decimal_places, sleep_between_symbols, sleep_between_cycles, view):
        self.symbols = symbols
        self.time_adjustment_hours = time_adjustment_hours
        self.decimal_places = decimal_places
        self.sleep_between_symbols = sleep_between_symbols
        self.sleep_between_cycles = sleep_between_cycles
        self.view = view

    def process_symbols(self):
        while True:
            for symbol in self.symbols:
                if not mt5.symbol_select(symbol, True):
                    logger.error(f"Failed to select symbol: {symbol}")
                    continue

                symbol_info = mt5.symbol_info_tick(symbol)
                if symbol_info is None:
                    logger.error(f"{symbol} not found, cannot call symbol_info_tick()")
                    continue

                bid = round(symbol_info.bid, self.decimal_places)
                ask = round(symbol_info.ask, self.decimal_places)
                last = round((bid + ask) / 2, self.decimal_places)

                server_time_raw = symbol_info.time
                server_time_with_adjustment = server_time_raw + (self.time_adjustment_hours * 3600)
                server_time_adjusted = datetime.utcfromtimestamp(server_time_with_adjustment)

                data = {
                    "symbol": symbol,
                    "timestamp": server_time_adjusted.strftime('%Y-%m-%d %H:%M:%S'),
                    "server_time_raw": int(server_time_with_adjustment),
                    "bid": bid,
                    "ask": ask,
                    "last": last
                }

                if self.view:
                    logger.info(f"Symbol: {symbol}, Time: {server_time_adjusted.strftime('%Y-%m-%d %H:%M:%S')}, Server Time Adjusted: {server_time_with_adjustment}, Bid: {bid}, Ask: {ask}, Last: {last}")

                self.insert_data_to_db(symbol, data)
                time.sleep(self.sleep_between_symbols)

            time.sleep(self.sleep_between_cycles)

    def insert_data_to_db(self, symbol, data):
        table_name = symbol.replace(".", "")
        merge_sql_prices = f"""
        MERGE INTO FOREX_DATA.PRICES_{table_name} (TIMESTAMP, SERVERTIME, BID, ASK, LAST)
        KEY(TIMESTAMP)
        VALUES (PARSEDATETIME('{data['timestamp']}', 'yyyy-MM-dd HH:mm:ss'), {data['server_time_raw']}, {data['bid']}, {data['ask']}, {data['last']});
        """
        merge_sql_thick = f"""
        MERGE INTO FOREX_DATA.THICK (SYMBOL, TIMESTAMP, SERVERTIME, BID, ASK, LAST)
        KEY(SYMBOL)
        VALUES ('{data['symbol']}', PARSEDATETIME('{data['timestamp']}', 'yyyy-MM-dd HH:mm:ss'), {data['server_time_raw']}, {data['bid']}, {data['ask']}, {data['last']});
        """
        try:
            response = requests.post('http://localhost:8080/SqlApi/executeSQL', data=merge_sql_prices, timeout=4)
            response.raise_for_status()
        except requests.RequestException as e:
            logger.error(f"Server time out: {e}")