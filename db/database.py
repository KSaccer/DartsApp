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
        self.db_conn = self.create_connection()
        with self.db_conn:
            with open(SQL_SCRIPT_PATH, "r") as sql_script_file:
                sql_script = sql_script_file.read()
                self.db_initialize(sql_script)

    def __del__(self) -> None:
        """Ensure connection is closed if object is garbage collected"""
        self.close_connection()

    def get_last_game_id(self) -> int:
        """Get last game id from database"""
        cursor = self.db_conn.cursor()
        cursor.execute("SELECT MAX(game_id) FROM games")
        game_id = cursor.fetchone()[0]
        if not game_id:
            return 0
        return game_id

    def create_connection(self) -> sqlite3.Connection:
        """Create an sqlite3 connection with the database"""
        db_conn = sqlite3.connect(self.db_path)
        return db_conn
    
    def close_connection(self) -> None:
        """Close the database connection"""
        if self.db_conn:
            self.db_conn.close()
            self.db_conn = None

    def db_initialize(self, sql_script: str) -> None:
        """Initialize the database using the provided sql script"""
        cursor = self.db_conn.cursor()
        cursor.executescript(sql_script)
        self.db_conn.commit()

    def insert_game(self, record: tuple) -> None:
        """Insert game into games table"""
        # TODO: document how the record tuple should look like
        cursor = self.db_conn.cursor()
        cursor.execute(
            "INSERT INTO games VALUES (?, ?, ?, ?)",
            (*record, )
            )
        self.db_conn.commit()

    def insert_data(self, record: tuple) -> None:
        """Insert scoring data into throws table.
        record = (game_id, throw_1, throw_2, throw_3, sum)"""
        cursor = self.db_conn.cursor()
        cursor.execute(
            "INSERT INTO throws VALUES (?, ?, ?, ?, ?)",
            (*record, )
            )
        self.db_conn.commit()

    def backup_database(self) -> bool:
        """Create a copy of the db with a timestamp in the filename in the 
        folder defined by the BACKUP_PATH constant
        Return True if backup was successful, False otherwise"""
        try:
            # Ensure backup directory exists
            os.makedirs(BACKUP_PATH, exist_ok=True)

            # Create backup filename with timestamp            
            current_datetime = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = f"{Path(self.db_path).stem}_{current_datetime}.db"
            backup_full_path = os.path.join(BACKUP_PATH, backup_file)
            copy(self.db_path, backup_full_path)
            return True

        except OSError as e:
            print(f"Error during backup: {e}")
            return False


if __name__ == "__main__":
    pass
