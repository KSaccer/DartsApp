import sqlite3
from datetime import datetime


class DataBase():
    def __init__(self, db_path):
        self.db_path = db_path
        db_conn = self.create_connection()
        with db_conn:
            self.create_tables(db_conn)
            self.last_game_id = self.get_last_game_id(db_conn)
            self.insert_game(db_conn)

    def get_last_game_id(self, db_conn):
        cursor = db_conn.cursor()
        cursor.execute("SELECT MAX(game_id) FROM games")
        game_id = cursor.fetchone()[0]
        if not game_id:
            return 0
        return game_id

    def create_connection(self):
        db_conn = sqlite3.connect(self.db_path)
        return db_conn

    def create_tables(self, db_conn):
        cursor = db_conn.cursor()
        cursor.execute('''
                       CREATE TABLE IF NOT EXISTS games (
                           game_id INT,
                           datetime DATETIME,
                           type TEXT NOT NULL,
                           PRIMARY KEY (game_id)
                       )
                       ''')
        cursor.execute('''
                       CREATE TABLE IF NOT EXISTS throws (
                           game_id INT,
                           timestamp TIMESTAMP NOT NULL,
                           throw_1 TEXT NOT NULL,
                           throw_2 TEXT NOT NULL,
                           throw_3 TEXT NOT NULL,
                           PRIMARY KEY(timestamp),
                           FOREIGN KEY(game_id) REFERENCES games(game_id)
                       );

                       ''')
        db_conn.commit()

    def insert_game(self, db_conn):
        cursor = db_conn.cursor()
        cursor.execute(
            "INSERT INTO games VALUES (?, ?, ?)",
            (self.last_game_id + 1, datetime.now(), "Scoring")
            )
        db_conn.commit()

    def insert_data(self, record):
        # 1. Open database
        db_conn = sqlite3.connect(self.db_path)
        cursor = db_conn.cursor()
        # 2. Insert data
        cursor.execute(
            "INSERT INTO throws VALUES (?, ?, ?, ?, ?)",
            (self.last_game_id, *record[1:-1])
            )
        # 3. Close database
        db_conn.commit()
        db_conn.close()


if __name__ == "__main__":
    pass
