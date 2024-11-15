from script1 import ProcessSymbols
import logging

# Ustawienia logowania
logger = logging.getLogger()

class ProcessSymbolsAccount2(ProcessSymbols):
    def get_login_info(self):
        try:
            # Pobieranie danych logowania dla Account2, Password2 i Server2
            account = self.config.getint('login', 'account2')
            password = self.config.get('login', 'password2')
            server = self.config.get('login', 'server2')
        except configparser.NoSectionError as e:
            logger.error(f"Config file is missing section: {e.section}")
            raise
        except configparser.NoOptionError as e:
            logger.error(f"Config file is missing option: {e.option}")
            raise
        logger.info("Login configuration for Account2 loaded successfully")
        return account, password, server

def main():
    logger.info("Rozpoczynanie działania skryptu Process Symbols dla Account2")
    process = ProcessSymbolsAccount2()
    account, password, server = process.get_login_info()
    decimal_places, sleep_between_symbols, sleep_between_cycles, view, time_adjustment_hours = process.get_settings()
    symbols = process.load_symbols()

    process.initialize_mt5(account, password, server)
    process.create_schema_if_not_exists()
    process.create_thick_table_if_not_exists()

    for symbol in symbols:
        process.create_table_prices_if_not_exists(symbol)

    try:
        process.process_symbols(symbols, time_adjustment_hours, decimal_places, sleep_between_symbols, sleep_between_cycles, view)
    except KeyboardInterrupt:
        logger.info("Process interrupted by user")
    finally:
        mt5.shutdown()

if __name__ == "__main__":
    main()