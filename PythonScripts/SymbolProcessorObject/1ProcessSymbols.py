import logging
import MetaTrader5 as mt5
from modules.config_loader import ConfigLoader
from modules.symbol_loader import SymbolLoader
from modules.mt5_logger import MT5_logger
from modules.db_manager import DatabaseManager
from modules.mt5_processor import MT5Processor


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

CONFIG_FILE_PATH = '/config/config.ini'
SYMBOLS_FILE_PATH = '/config/symbols.txt'

def main():
    logger.info("Rozpoczynanie działania skryptu Process Symbols")

    config_loader = ConfigLoader('/config/config.ini')
    account, password, server = config_loader.get_login_info()
    decimal_places, sleep_between_symbols, sleep_between_cycles, view, time_adjustment_hours = config_loader.get_settings()

    symbol_loader = SymbolLoader('/config/symbols.txt')
    symbols = symbol_loader.symbols

    mt5_login = MT5_logger(account, password, server)
    mt5_login.initialize_mt5()

    db_manager = DatabaseManager()
    db_manager.create_schema_if_not_exists()
    db_manager.create_thick_table_if_not_exists()

    for symbol in symbols:
        db_manager.create_table_prices_if_not_exists(symbol)

    try:
        processor = MT5Processor(symbols, time_adjustment_hours, decimal_places, sleep_between_symbols, sleep_between_cycles, view)
        processor.process_symbols()
    except KeyboardInterrupt:
        logger.info("Process interrupted by user")
    finally:
        mt5.shutdown()

if __name__ == "__main__":
    main()