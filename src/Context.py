import json
import logging
from src.clients.postgresql_client import PostgreSQLClient
from src.clients.redis_client import RedisClient
logger = logging.getLogger(__name__)

class Context:
    def __init__(self, config_path):
        with open(config_path, 'r') as conf:
            self.config_file = json.load(conf)
            logger.info("LOADED CONFIG FILE")
            logger.info(self.config_file)
        if self.config_file is None:
            raise "ERROR LOADING CONFIG FILE"
    
        self.redis_client = self.__get_redis_client()
        self.sql_client = self.__get_sql_client()
        self.account_names = self.config_file['account_names']

    def __get_sql_client(self):
        sql_data = self.config_file['sql_config']
        return PostgreSQLClient(sql_data['database_name'], sql_data['host'], sql_data['port'])

    def __get_redis_client(self):
        return RedisClient(**self.config_file['redis_config'])
    
