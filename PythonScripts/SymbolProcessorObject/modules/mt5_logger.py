import MetaTrader5 as mt5
import logging

logger = logging.getLogger()

class MT5_logger:
    def __init__(self, account, password, server):
        self.account = account
        self.password = password
        self.server = server

    def initialize_mt5(self):
        try:
            if not mt5.initialize():
                logger.error(f"initialize() failed, error code = {mt5.last_error()}")
                raise RuntimeError('initialize() failed')
            logger.info("MT5 initialized successfully")

            if not mt5.login(self.account, self.password, self.server):
                logger.error(f"login() failed, error code = {mt5.last_error()}")
                raise RuntimeError('login() failed')
            logger.info("Logged in to MT5 successfully")
        except Exception as e:
            logger.error(f"Exception during MT5 initialization or login: {e}")
            raise