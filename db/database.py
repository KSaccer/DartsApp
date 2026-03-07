import sqlite3
import os
from datetime import datetime
from pathlib import Path
from shutil import copy
from typing import Optional

import pandas as pd
import config

SQL_SCRIPT_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), 
    "sql", 
    "db_initialize.sql")

def _get_backup_path() -> str:
    """Return the configured backup path, falling back to a portable default."""
    cfg = config.load_config()
    return cfg.get(
        "database",
        "backup_path",
        fallback=config.DEFAULTS["database"]["backup_path"],
    )

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
        folder defined in configuration
        Return True if backup was successful, False otherwise"""
        try:
            backup_path = _get_backup_path()

            # Ensure backup directory exists
            os.makedirs(backup_path, exist_ok=True)

            # Create backup filename with timestamp            
            current_datetime = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = f"{Path(self.db_path).stem}_{current_datetime}.db"
            backup_full_path = os.path.join(backup_path, backup_file)
            copy(self.db_path, backup_full_path)
            return True

        except OSError as e:
            print(f"Error during backup: {e}")
            return False

    def query_to_dataframe_raw(
        self,
        sql: str,
        params: Optional[tuple] = None,
        parse_dates: Optional[dict] = None,
    ) -> pd.DataFrame:
        """Execute a raw SQL query and return the result as a DataFrame."""
        return pd.read_sql_query(
            sql,
            self.db_conn,
            params=params,
            parse_dates=parse_dates,
        )

    def query_to_dataframe(
        self,
        sql_path: str,
        params: Optional[tuple] = None,
        parse_dates: Optional[dict] = None,
    ) -> pd.DataFrame:
        """Execute a SQL script file and return the result as a DataFrame."""
        with open(sql_path, "r") as query_file:
            sql = query_file.read()
        return self.query_to_dataframe_raw(sql, params=params, parse_dates=parse_dates)


if __name__ == "__main__":
    pass
