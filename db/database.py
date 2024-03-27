import sqlite3
import os
from datetime import datetime
from pathlib import Path
from shutil import copy

SQL_SCRIPT_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), 
    "sql", 
    "db_initialize.sql")

BACKUP_PATH = os.path.join("D:", os.sep, "Dolgok", "Darts")

class DataBase():
    """Class for handling darts score database"""

    def __init__(self, db_path: str) -> None:
        """Initialize database and get last game id"""
        self.db_path = db_path
        db_conn = self.create_connection()
        with db_conn:
            with open(SQL_SCRIPT_PATH, "r") as sql_script_file:
                sql_script = sql_script_file.read()
                self.db_initialize(db_conn, sql_script)
            self.last_game_id = self.get_last_game_id(db_conn)

    def get_last_game_id(self, db_conn: sqlite3.Connection) -> int:
        """Get last game id from database"""
        cursor = db_conn.cursor()
        cursor.execute("SELECT MAX(game_id) FROM games")
        game_id = cursor.fetchone()[0]
        if not game_id:
            return 0
        return game_id

    def create_connection(self) -> sqlite3.Connection:
        """Create an sqlite3 connection with the database"""
        db_conn = sqlite3.connect(self.db_path)
        return db_conn

    def db_initialize(self, db_conn: sqlite3.Connection,
                      sql_script: str) -> None:
        """Initialize the database using the provided sql script"""
        cursor = db_conn.cursor()
        cursor.executescript(sql_script)
        db_conn.commit()

    def insert_game(self, record: tuple) -> None:
        """Insert game into games table"""
        db_conn = sqlite3.connect(self.db_path)
        cursor = db_conn.cursor()
        cursor.execute(
            "INSERT INTO games VALUES (?, ?, ?, ?)",
            (*record, )
            )
        db_conn.commit()
        self.last_game_id += 1

    def insert_data(self, record: tuple) -> None:
        """Insert scoring data into throws table.
        record = (game_id, throw_1, throw_2, throw_3, sum)"""
        db_conn = sqlite3.connect(self.db_path)
        cursor = db_conn.cursor()
        cursor.execute(
            "INSERT INTO throws VALUES (?, ?, ?, ?, ?)",
            (self.last_game_id, *record)
            )
        db_conn.commit()
        db_conn.close()

    def backup_database(self) -> None:
        """Create a copy of the db with a timestamp in the filename in the 
        folder defined by the BACKUP_PATH constant"""
        current_datetime = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = f"{Path(self.db_path).stem}_{current_datetime}.db"
        copy(self.db_path, os.path.join(BACKUP_PATH, backup_file))



if __name__ == "__main__":
    pass
