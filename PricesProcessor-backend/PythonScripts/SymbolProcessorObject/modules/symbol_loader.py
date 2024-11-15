import os
import logging

logger = logging.getLogger()

class SymbolLoader:
    def __init__(self, symbols_path):
        self.symbols_path = symbols_path
        self.symbols = self.load_symbols()

    def load_symbols(self):
        if not os.path.exists(self.symbols_path):
            logger.error(f"Symbols file not found at: {self.symbols_path}")
            raise FileNotFoundError(f"Symbols file not found at: {self.symbols_path}")

        with open(self.symbols_path, 'r') as file:
            symbols = [line.strip() for line in file.readlines()]

        logger.info(f"Symbols loaded successfully from: {self.symbols_path}")
        return symbols