import tkinter as tk
import tkinter.ttk as ttk
import sqlite3
from tkinter import messagebox
from datetime import datetime


FONT_TITLE = ("Arial", 20, "bold")
FONT_DEFAULT = ("Arial", 10)


class DartsApp(tk.Tk):
    def __init__(self, *args, **kwargs):

        # main config
        super().__init__(*args, **kwargs)
        self.title("Darts Scoring App")
        self.geometry("800x600")
        self.resizable(False, False)
        self.option_add("*Font", FONT_DEFAULT)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=5)
        self.rowconfigure(2, weight=3)
        self.rowconfigure(3, weight=1)
        self.columnconfigure((0, 1), weight=1)

        # populating widgets
        self.page_title = PageTitle(self)
        self.page_title.grid(row=0, column=0, columnspan=2)

        self.score_entry_block = ScoreEntryBlock(self, text="Enter Score")
        self.score_entry_block.grid(row=1, column=0, padx=10, pady=10, sticky="news")

        self.statistics = Statistics(self, text="Session Statistics")
        self.statistics.grid(row=2, column=0, padx=10, pady=10, sticky="news")

        self.buttons_frame = ButtonsFrame(self, relief="groove", border=2)
        self.buttons_frame.grid(row=3, column=0, padx=10, pady=10, sticky="news")

        self.throw_history = ThrowHistory(self, text="Throw History")
        self.throw_history.grid(row=1, column=1, padx=10, pady=10, rowspan=3, sticky="news")

        # run
        self.score_entry_block.throw_1.value.focus_set()
        self.mainloop()


class PageTitle(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        label = tk.Label(self, text="Darts Scoring Practice Session", font=FONT_TITLE)
        label.pack(expand=True, fill="both")


class ScoreEntryBlock(tk.LabelFrame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.parent = parent
        self.rowconfigure((0, 1, 2, 3), weight=1)
        self.columnconfigure((0, 1), weight=1)
        self.throw_1 = ThrowEntry(self, "1st Throw:", 0)
        self.throw_2 = ThrowEntry(self, "2nd Throw:", 1)
        self.throw_3 = ThrowEntry(self, "3rd Throw:", 2)
        self.submit = tk.Button(self, text="Submit", command=self.submit_data)
        self.submit.grid(row=3, column=0, columnspan=2, padx=10, pady=10, sticky="news")
        self.throw_1.value.bind("<Return>", lambda event=None: self.throw_2.value.focus_set())
        self.throw_2.value.bind("<Return>", lambda event=None: self.throw_3.value.focus_set())
        self.throw_3.value.bind("<Return>", lambda event=None: self.submit.invoke())

    def clear_values(self):
        self.throw_1.value.delete(0, tk.END)
        self.throw_2.value.delete(0, tk.END)
        self.throw_3.value.delete(0, tk.END)

    def get_values(self):
        return [
            self.throw_1.value.get(),
            self.throw_2.value.get(),
            self.throw_3.value.get()
            ]

    def submit_data(self):
        '''
        1. Get entried scores, populate table, clear entry fields
        2. Update Statistics fields
        3. Set focus to throw_1 entry field
        '''

        # 1. Get entried scores, populate table, clear entry fields
        throws = self.get_values()
        throws_sum = 0

        # check if all entry fields are filled, if so, calculate sum
        if not all(throws):
            return
        for throw in throws:
            if throw.upper()[0] == "D":
                throws_sum += int(throw[1:]) * 2
            elif throw.upper()[0] == "T":
                throws_sum += int(throw[1:]) * 3
            else:
                throws_sum += int(throw)

        # populate table with throw data
        record = [throw.upper() for throw in throws] + [throws_sum]
        self.parent.throw_history.add_record(record)
        self.clear_values()

        # 2. Update statistics
        stats = self.parent.statistics.get_statistics()
        updated_darts_thrown = int(stats["darts_thrown"]) + 3
        updated_score = int(stats["score"]) + throws_sum
        updated_current_max = int(stats["current_max"])
        if updated_current_max < throws_sum:
            updated_current_max = throws_sum

        updated_stats = {
            "avg": f'{updated_score / updated_darts_thrown * 3:.1f}',
            "darts_thrown": f'{updated_darts_thrown}',
            "score": f'{updated_score}',
            "current_max": f'{updated_current_max}'
        }

        self.parent.statistics.set_statistics(**updated_stats)

        # 3. Set focus
        self.throw_1.value.focus_set()


class ThrowEntry():
    def __init__(self, parent, label_text, row, *args, **kwargs):
        self.label = tk.Label(parent, text=label_text)
        self.value = tk.Entry(parent)
        self.label.grid(row=row, column=0, padx=10, pady=10)
        self.value.grid(row=row, column=1, padx=10, pady=10)


class Statistics(tk.LabelFrame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.rowconfigure((0, 1, 2, 3), weight=1)
        self.columnconfigure((0, 1), weight=1)
        self.avg = StatField(self, "Average:", "0.0", 0)
        self.darts_thrown = StatField(self, "Darts thrown:", "0", 1)
        self.score = StatField(self, "Score:", "0", 2)
        self.current_max = StatField(self, "Current maximum:", "0", 3)

    def get_statistics(self):
        return {
            "avg": self.avg.value.cget("text"),
            "darts_thrown": self.darts_thrown.value.cget("text"),
            "score": self.score.value.cget("text"),
            "current_max": self.current_max.value.cget("text")
        }

    def set_statistics(self, *, avg, darts_thrown, score, current_max): # keyword argus without default values
        self.avg.value.config(text=avg)
        self.darts_thrown.value.config(text=darts_thrown)
        self.score.value.config(text=score)
        self.current_max.value.config(text=current_max)

    def reset(self):
        for _ in [self.avg, self.darts_thrown, self.score, self.current_max]:
            _.value.config(text=_.initial_value)


class StatField():
    def __init__(self, parent, label_text, value_text, row, *args, **kwargs):
        self.initial_value = value_text
        self.label = tk.Label(parent, text=label_text)
        self.value = tk.Label(parent, text=value_text)
        self.label.grid(row=row, column=0, padx=10, pady=10, sticky="e")
        self.value.grid(row=row, column=1, padx=10, pady=10, sticky="w")


class ButtonsFrame(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.parent = parent
        self.rowconfigure(0, weight=1)
        self.columnconfigure((0, 1), weight=1)
        finish_button = tk.Button(self, text="Finish", command=self.finish)
        restart_button = tk.Button(self, text="Restart", command=self.restart)
        finish_button.grid(row=0, column=0, padx=10, pady=10, sticky="news")
        restart_button.grid(row=0, column=1, padx=10, pady=10, sticky="news")

    def restart(self):
        response = messagebox.askokcancel(
        "Confirmation",
        "Do you really want to restart the session? Scores and statistics will be discarded!")

        if response:    # Reset statistics and clear table
            self.parent.statistics.reset()
            self.parent.throw_history.clear_table()
        else:
            pass    # Session continues if user clicks Cancel

    def finish(self):
        # 1. Insert data into database
        db = DataBase("darts_data.db")
        for value in self.parent.throw_history.get_records():
            db.insert_data(value)

        # 2. Close application
        self.parent.destroy()


class ThrowHistory(tk.LabelFrame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.items = None

        columns = {
            "id": ("ID", True),
            "timestep": ("Timestep", False),
            "throw_1": ("1st Throw", True),
            "throw_2": ("2nd Throw", True),
            "throw_3": ("3rd Throw", True),
            "throw_sum": ("SUM", True)
        }
        self.throw_history = ttk.Treeview(self, columns=list(columns.keys()))
        self.throw_history.grid(row=0, column=0, padx=10, pady=10, sticky="ns")

        # Column config
        self.throw_history['show'] = 'headings'
        self.throw_history["displaycolumns"] = [
            column for column in columns if columns[column][1]
            ]
        for column in columns:
            self.throw_history.heading(column, text=columns[column][0])
            self.throw_history.column(column, width=80, anchor=tk.CENTER)
        # self.throw_history.column("#0", width=80, anchor=tk.CENTER)

        # Throw history Scrollbar
        scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.throw_history.yview)
        self.throw_history.configure(yscroll=scrollbar.set)
        scrollbar.grid(row=0, column=1, sticky='ns')

    def add_record(self, record):
        ts = datetime.timestamp(datetime.now())
        if self.items:
            last_id = int(self.throw_history.item(self.items[-1])["values"][0])
        else:
            last_id = 0
        self.throw_history.insert("", tk.END, values=[last_id + 1] + [ts] + record)
        self.items = self.throw_history.get_children()

    def clear_table(self):
        self.throw_history.delete(*self.items)
        self.items = None

    def get_records(self):
        for item in self.items:
            yield self.throw_history.item(item)["values"]


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


DartsApp()
