import sqlite3


class DB:
    def __init__(self, db_location: str) -> None:
        self.db = db_location


class Query:
    def __init__(self, orm: DB, query: str) -> None:
        self.orm = orm
        self._query = query
            
    def __enter__(self):
        print("Entering!")
        self.db_connection = sqlite3.connect(self.orm.db)
        self.db_cursor = self.db_connection.cursor()
        self.db_cursor.execute(self._query)
        _result = self.db_cursor.fetchall()
        self.db_cursor.close()
        return _result

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.db_connection:
            print("Closing!")
            self.db_connection.close()
            
