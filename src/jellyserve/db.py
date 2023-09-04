import sqlite3
import functools


# DB stuff
class BaseDBConnector:
    def __init__(self) -> None:
        self.query = functools.partial(Query, self)

    def connect(self):
        pass

    def execute(self):
        pass

    def close(self):
        pass


class SQLite(BaseDBConnector):
    def __init__(self, db_location: str) -> None:
        self.db_location = db_location
        super().__init__()

    def connect(self):
        self.db_connection = sqlite3.connect(self.db_location)

        def dict_factory(cursor, row):
            d = {}
            for idx, col in enumerate(cursor.description):
                d[col[0]] = row[idx]
            return d

        self.db_connection.row_factory = dict_factory
        self.db_cursor = self.db_connection.cursor()

    def execute(self, _query: str, _query_params: tuple = ()):
        with self.db_connection:
            self.db_cursor.execute(_query, _query_params)
        _result = self.db_cursor.fetchall()
        self.db_cursor.close()
        return _result

    def close(self):
        if self.db_connection:
            self.db_connection.close()


class Query:
    def __init__(
        self, connector: sqlite3.Connection, query: str, query_params: tuple = ()
    ) -> None:
        self.connector = connector
        self._query = query
        self._query_params = query_params

    def __enter__(self):
        self.connector.connect()
        return self.connector.execute(self._query, self._query_params)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.connector.close()
