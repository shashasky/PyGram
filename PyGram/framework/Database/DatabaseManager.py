from framework.Database.Connection import Connection
from config.database import DATABASES

class DatabaseManager:
    def table(self, table_name, connection_name=None):
        if connection_name is None:
            connection_name = DATABASES['default']
        config = DATABASES['connections'][connection_name]
        conn = Connection(config)
        from framework.Database.QueryBuilder import QueryBuilder
        return QueryBuilder(conn, table_name)