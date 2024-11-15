import requests
import logging

logger = logging.getLogger()

class DatabaseManager:
    def create_schema_if_not_exists(self):
        create_schema_sql = "CREATE SCHEMA IF NOT EXISTS FOREX_DATA;"
        try:
            response = requests.post('http://localhost:8080/SqlApi/executeSQL', data=create_schema_sql, timeout=4)
            response.raise_for_status()
        except requests.RequestException as e:
            logger.error(f"Error creating schema: {e}")
            raise

    def create_table_prices_if_not_exists(self, symbol):
        table_name = symbol.replace(".","")
        create_table_sql = f"""
        CREATE TABLE IF NOT EXISTS FOREX_DATA.PRICES_{table_name} (
            ID IDENTITY PRIMARY KEY,
            TIMESTAMP TIMESTAMP,
            SERVERTIME BIGINT,
            BID DECIMAL(20, 3),
            ASK DECIMAL(20, 3),
            LAST DECIMAL(20, 3)
        );
        """
        try:
            response = requests.post('http://localhost:8080/SqlApi/executeSQL', data=create_table_sql, timeout=4)
            response.raise_for_status()
        except requests.RequestException as e:
            logger.error(f"Error creating table: {e}")
            raise

    def create_thick_table_if_not_exists(self):
        create_thick_table_sql = """
        CREATE TABLE IF NOT EXISTS FOREX_DATA.THICK (
            SYMBOL VARCHAR(50) PRIMARY KEY,
            TIMESTAMP TIMESTAMP,
            SERVERTIME BIGINT,
            BID DECIMAL(20, 3),
            ASK DECIMAL(20, 3),
            LAST DECIMAL(20, 3)
        );
        """
        try:
            response = requests.post('http://localhost:8080/SqlApi/executeSQL', data=create_thick_table_sql, timeout=4)
            response.raise_for_status()
        except requests.RequestException as e:
            logger.error(f"Error creating THICK table: {e}")
            raise