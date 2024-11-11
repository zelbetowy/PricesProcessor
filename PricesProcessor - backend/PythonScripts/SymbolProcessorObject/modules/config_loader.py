import configparser
import os
import logging

logger = logging.getLogger()

class ConfigLoader:

    def __init__(self, config_path):
        self.config_path = config_path
        self.config = self.load_config()

    def load_config(self):
        config = configparser.ConfigParser()
        logger.info(f"Loading config file from: {self.config_path}")
        if not os.path.exists(self.config_path):
            logger.error(f"Config file not found at: {self.config_path}")
            raise FileNotFoundError(f"Config file not found at: {self.config_path}")
        config.read(self.config_path)
        logger.info(f"Config file loaded successfully from: {self.config_path}")
        return config

    def get_login_info(self):
        try:
            account = self.config.getint('login', 'account')
            password = self.config.get('login', 'password')
            server = self.config.get('login', 'server')
        except configparser.NoSectionError as e:
            logger.error(f"Config file is missing section: {e.section}")
            raise
        except configparser.NoOptionError as e:
            logger.error(f"Config file is missing option: {e.option}")
            raise
        logger.info("Login configuration loaded successfully")
        return account, password, server

    def get_settings(self):
        try:
            decimal_places = self.config.getint('settings process', 'decimal_places')
            sleep_between_symbols = self.config.getfloat('settings process', 'sleep_between_symbols')
            sleep_between_cycles = self.config.getfloat('settings process', 'sleep_between_cycles')
            view = self.config.getboolean('settings process', 'view')
            time_adjustment_hours = self.config.getint('settings process', 'time_adjustment_hours')
        except configparser.NoSectionError as e:
            logger.error(f"Config file is missing section: {e.section}")
            raise
        except configparser.NoOptionError as e:
            logger.error(f"Config file is missing option: {e.option}")
            raise
        logger.info("Settings loaded successfully")
        return decimal_places, sleep_between_symbols, sleep_between_cycles, view, time_adjustment_hours