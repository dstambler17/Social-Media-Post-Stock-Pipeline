import psycopg2
import logging

logger = logging.getLogger(__name__)

class PostgreSQLClient():
    def __init__(self, db_name, host, port, user="postgres", password=""):
        self.conn = psycopg2.connect(database = db_name, user = user,
             password = password, host = host, port = port)
        self.cur = self.conn.cursor()
    
    def __del__(self):
        #logger.info('Closing Client.')
        self.cur.close()
        self.conn.close()
    
    def execute_write_sql(self, sql, data):
        self.cur.execute(sql, data)
        self.conn.commit()
    
    def execute_many_writes_sql(self, sql, data):
        self.cur.executemany(sql, data)
        self.conn.commit()
    
    def execute_query(self, sql):
        self.cur.execute(sql)
        return self.cur.fetchall()
            

