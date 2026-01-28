class QueryBuilder:
    def __init__(self, connection, table):
        self._connection = connection
        self._table = table
        self._wheres = []
        self._selects = ['*']
        self._limit = None
        self._offset = None
        self._orders = []

    def select(self, *columns):
        self._selects = list(columns) if columns else ['*']
        return self

    def where(self, column, value=None, operator='='):
        if value is None:
            value = operator
            operator = '='
        self._wheres.append((column, operator, value))
        return self

    def limit(self, n):
        self._limit = n
        return self

    def offset(self, n):
        self._offset = n
        return self

    def order_by(self, column, direction='ASC'):
        self._orders.append((column, direction.upper()))
        return self

    def _build_where_clause(self):
        if not self._wheres:
            return "", []
        clauses = []
        params = []
        for col, op, val in self._wheres:
            placeholder = '?' if self._connection.config['driver'] == 'sqlite' else '%s'
            clauses.append(f"{col} {op} {placeholder}")
            params.append(val)
        return " WHERE " + " AND ".join(clauses), params

    def _build_order_clause(self):
        if not self._orders:
            return ""
        orders = [f"{col} {dir}" for col, dir in self._orders]
        return " ORDER BY " + ", ".join(orders)

    def first(self):
        sql = f"SELECT {', '.join(self._selects)} FROM {self._table}"
        where_clause, params = self._build_where_clause()
        sql += where_clause + self._build_order_clause() + " LIMIT 1"
        rows = self._connection.execute(sql, params, fetch=True)
        return rows[0] if rows else None

    def get(self):
        sql = f"SELECT {', '.join(self._selects)} FROM {self._table}"
        where_clause, params = self._build_where_clause()
        sql += where_clause + self._build_order_clause()
        if self._limit is not None:
            sql += f" LIMIT {self._limit}"
        if self._offset is not None:
            sql += f" OFFSET {self._offset}"
        return self._connection.execute(sql, params, fetch=True)

    def insert(self, data):
        columns = ', '.join(data.keys())
        driver = self._connection.config['driver']
        placeholder = '?' if driver == 'sqlite' else '%s'
        placeholders = ', '.join([placeholder] * len(data))
        sql = f"INSERT INTO {self._table} ({columns}) VALUES ({placeholders})"
        self._connection.execute(sql, list(data.values()), fetch=False)
        return True

    def update(self, data):
        driver = self._connection.config['driver']
        placeholder = '?' if driver == 'sqlite' else '%s'
        set_clause = ', '.join([f"{k} = {placeholder}" for k in data.keys()])
        sql = f"UPDATE {self._table} SET {set_clause}"
        where_clause, params = self._build_where_clause()
        sql += where_clause
        self._connection.execute(sql, list(data.values()) + params, fetch=False)
        return True

    def delete(self):
        sql = f"DELETE FROM {self._table}"
        where_clause, params = self._build_where_clause()
        sql += where_clause
        self._connection.execute(sql, params, fetch=False)
        return True