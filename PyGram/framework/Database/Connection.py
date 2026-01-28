import sqlite3
import pymysql

class Connection:
    def __init__(self, config):
        self.config = config

    def _create_connection(self):
        driver = self.config['driver']
        if driver == 'sqlite':
            conn = sqlite3.connect(self.config['database'])
            conn.row_factory = sqlite3.Row
            return conn
        elif driver == 'mysql':
            return pymysql.connect(
                host=self.config['host'],
                port=self.config['port'],
                user=self.config['username'],
                password=self.config['password'],
                database=self.config['database'],
                charset=self.config.get('charset', 'utf8mb4'),
                cursorclass=pymysql.cursors.DictCursor
            )
        else:
            raise ValueError(f"Unsupported database driver: {driver}")

    def execute(self, sql, params=None, fetch=False):
        conn = self._create_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(sql, params or ())
            if fetch:
                result = cursor.fetchall()
            else:
                conn.commit()
                result = cursor.rowcount
            return result
        except Exception:
            conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()