import sqlite3
from datetime import datetime

SQL_SCRIPT_PATH = "db_initialize.sql"


class DataBase():
    def __init__(self, db_path: str) -> None:
        self.db_path = db_path
        db_conn = self.create_connection()
        with db_conn:
            with open(SQL_SCRIPT_PATH, "r") as sql_script_file:
                sql_script = sql_script_file.read()
                self.db_initialize(db_conn, sql_script)
            self.last_game_id = self.get_last_game_id(db_conn)

    def get_last_game_id(self, db_conn: sqlite3.Connection) -> int:
        cursor = db_conn.cursor()
        cursor.execute("SELECT MAX(game_id) FROM games")
        game_id = cursor.fetchone()[0]
        if not game_id:
            return 0
        return game_id

    def create_connection(self) -> sqlite3.Connection:
        db_conn = sqlite3.connect(self.db_path)
        return db_conn

    def db_initialize(self, db_conn: sqlite3.Connection,
                      sql_script: str) -> None:
        cursor = db_conn.cursor()
        cursor.executescript(sql_script)
        db_conn.commit()

    def insert_game(self, record: tuple) -> None:
        db_conn = sqlite3.connect(self.db_path)
        cursor = db_conn.cursor()
        cursor.execute(
            "INSERT INTO games VALUES (?, ?, ?)",
            (*record, )
            )
        db_conn.commit()
        self.last_game_id += 1

    def insert_data(self, record: tuple) -> None:
        # 1. Open database
        db_conn = sqlite3.connect(self.db_path)
        cursor = db_conn.cursor()
        # 2. Insert data
        cursor.execute(
            "INSERT INTO throws VALUES (?, ?, ?, ?, ?)",
            (self.last_game_id, *record)
            )
        # 3. Close database
        db_conn.commit()
        db_conn.close()


if __name__ == "__main__":
    pass
