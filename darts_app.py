import tkinter as tk
import tkinter.ttk as ttk
from tkinter import messagebox
from datetime import datetime
from typing import Generator
from functools import partial

from database import DataBase


FONT_TITLE = ("Arial", 20, "bold")
FONT_DEFAULT = ("Arial", 10)
FONT_MENU = ("Malgun Gothic", 12)


class Game():
    def __init__(self, game_id: int, game_type: str = "Scoring") -> None:
        self.game_id = game_id
        self.game_type = game_type
        self.start = None
        self.end = None


class DartsApp(tk.Tk):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.title("Darts Scoring App")
        self.iconbitmap(default="pics/dartboard.ico")
        self.geometry("1000x600")
        self.resizable(False, False)
        self.option_add("*Font", FONT_DEFAULT)

        menu_style = ttk.Style()
        menu_style.configure("Menu.TFrame", background="#44546A")
        self.menu = Menu(self, style="Menu.TFrame")
        self.menu.pack(ipadx=20, side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.scoring = Scoring(self)
        self.scoring.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.mainloop()


class Menu(ttk.Frame):
    def __init__(self, parent, *args, **kwargs) -> None:
        super().__init__(parent, *args, **kwargs)

        menuitems = {
            "DASHBOARD": None,
            "SCORING": None,
            "STATISTICS": None,
            "SETTINGS": None,
        }
        for menuitem in menuitems:
            MenuItem(self, menuitem)

    def color_config(self, widget, color, event):
        widget.configure(background=color)


class MenuItem():
    def __init__(self, parent, label_text: str) -> None:
        self.label = tk.Label(parent, text=label_text, font=FONT_MENU,
                              background="#44546A", foreground="white",
                              anchor="w", padx=20, pady=10)
        self.label.pack(side=tk.TOP, fill=tk.BOTH,  anchor=tk.NW)
        self.label.bind("<Enter>", lambda event=None:
                        self.color_config(self.label, "#333F50"))
        self.label.bind("<Leave>", lambda event=None:
                        self.color_config(self.label, "#44546A"))
        self.label.bind("<Button-1>", lambda event=None:
                        self.go_to_page())

    def color_config(self, widget, color: str) -> None:
        widget.configure(background=color)

    def go_to_page(self):
        print("Go to page")
        pass


class Scoring(ttk.Frame):
    def __init__(self, parent, *args, **kwargs) -> None:

        # main config
        super().__init__(parent, *args, **kwargs)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=5)
        self.rowconfigure(2, weight=3)
        self.rowconfigure(3, weight=1)
        self.columnconfigure((0, 1), weight=1)

        # Initialize database
        self.db = DataBase("darts_data.db")
        # Initialize Game
        self.game = Game(self.db.last_game_id + 1)
        # populating widgets
        self.create_gui()
        # run
        self.score_entry_block.throw_1.value.focus_set()

    def create_gui(self) -> None:
        self.page_title = PageTitle(self)
        self.page_title.grid(row=0, column=0, columnspan=2)

        self.score_entry_block = ScoreEntryBlock(self, text="Enter Score")
        self.score_entry_block.grid(row=1, column=0, padx=10, pady=10,
                                    sticky="news")

        self.statistics = Statistics(self, text="Session Statistics")
        self.statistics.grid(row=2, column=0, padx=10, pady=10, sticky="news")

        self.buttons_frame = ButtonsFrame(self, relief="groove", border=2)
        self.buttons_frame.grid(row=3, column=0, padx=10, pady=10,
                                sticky="news")

        self.throw_history = ThrowHistory(self, text="Throw History")
        self.throw_history.grid(row=1, column=1, padx=10, pady=10,
                                rowspan=3, sticky="news")


class PageTitle(ttk.Frame):
    def __init__(self, parent, *args, **kwargs) -> None:
        super().__init__(parent, *args, **kwargs)
        label = ttk.Label(self, text="Darts Scoring Practice Session",
                          font=FONT_TITLE)
        label.pack(expand=True, fill="both")


class ScoreEntryBlock(ttk.LabelFrame):
    def __init__(self, parent, *args, **kwargs) -> None:
        super().__init__(parent, *args, **kwargs)
        self.parent = parent
        self.rowconfigure((0, 1, 2, 3), weight=1)
        self.columnconfigure((0, 1), weight=1)
        self.throw_1 = ThrowEntry(self, "1st Throw:", 0)
        self.throw_2 = ThrowEntry(self, "2nd Throw:", 1)
        self.throw_3 = ThrowEntry(self, "3rd Throw:", 2)
        self.submit = ttk.Button(self, text="Submit",
                                 command=self.submit_data)
        self.submit.grid(row=3, column=0, columnspan=2, padx=10, pady=10,
                         sticky="news")
        self.throw_1.value.bind("<Return>", lambda event=None:
                                self.throw_2.value.focus_set())
        self.throw_2.value.bind("<Return>", lambda event=None:
                                self.throw_3.value.focus_set())
        self.throw_3.value.bind("<Return>", lambda event=None:
                                self.submit.invoke())

    def clear_values(self) -> None:
        self.throw_1.value.delete(0, tk.END)
        self.throw_2.value.delete(0, tk.END)
        self.throw_3.value.delete(0, tk.END)

    def get_values(self) -> list:
        return [
            self.throw_1.value.get(),
            self.throw_2.value.get(),
            self.throw_3.value.get()
            ]

    def submit_data(self) -> None:
        """
        0. Initialize Game.start time, if it's none
        1. Get entried scores, populate table, clear entry fields
        2. Update Statistics fields
        3. Set focus to throw_1 entry field
        """

        # 0. Initialize Game.start time, if it's none
        if not self.parent.game.start:
            self.parent.game.start = datetime.now()

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
        record = tuple([throw.upper() for throw in throws] + [throws_sum])
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
    def __init__(self, parent, label_text: str, row: int) -> None:
        self.label = ttk.Label(parent, text=label_text)
        self.value = ttk.Entry(parent)
        self.label.grid(row=row, column=0, padx=10, pady=10)
        self.value.grid(row=row, column=1, padx=10, pady=10)


class Statistics(ttk.LabelFrame):
    def __init__(self, parent, *args, **kwargs) -> None:
        super().__init__(parent, *args, **kwargs)
        self.rowconfigure((0, 1, 2, 3), weight=1)
        self.columnconfigure((0, 1), weight=1)
        self.avg = StatField(self, "Average:", "0.0", 0)
        self.darts_thrown = StatField(self, "Darts thrown:", "0", 1)
        self.score = StatField(self, "Score:", "0", 2)
        self.current_max = StatField(self, "Current maximum:", "0", 3)

    def get_statistics(self) -> dict:
        return {
            "avg": self.avg.value.cget("text"),
            "darts_thrown": self.darts_thrown.value.cget("text"),
            "score": self.score.value.cget("text"),
            "current_max": self.current_max.value.cget("text")
        }

    # keyword args without default values
    def set_statistics(self, *, avg: str, darts_thrown: str,
                       score: str, current_max: str) -> None:
        self.avg.value.config(text=avg)
        self.darts_thrown.value.config(text=darts_thrown)
        self.score.value.config(text=score)
        self.current_max.value.config(text=current_max)

    def reset(self) -> None:
        for _ in [self.avg, self.darts_thrown, self.score, self.current_max]:
            _.value.config(text=_.initial_value)


class StatField():
    def __init__(self, parent, label_text: str,
                 value_text: str, row: int) -> None:
        self.initial_value = value_text
        self.label = ttk.Label(parent, text=label_text)
        self.value = ttk.Label(parent, text=value_text)
        self.label.grid(row=row, column=0, padx=10, pady=10, sticky="e")
        self.value.grid(row=row, column=1, padx=10, pady=10, sticky="w")


class ButtonsFrame(ttk.LabelFrame):
    def __init__(self, parent, *args, **kwargs) -> None:
        super().__init__(parent, *args, **kwargs)
        self.parent = parent
        self.rowconfigure(0, weight=1)
        self.columnconfigure((0, 1), weight=1)
        finish_button = ttk.Button(self, text="Finish",
                                   command=self.finish)
        restart_button = ttk.Button(self, text="Restart",
                                    command=self.restart)
        finish_button.grid(row=0, column=0, padx=10, pady=10, sticky="news")
        restart_button.grid(row=0, column=1, padx=10, pady=10, sticky="news")

    def restart(self) -> None:
        """Reset session - clear statistics and table records"""

        response = messagebox.askokcancel(
            "Confirmation",
            "Do you really want to restart the session?\n"
            "Scores and statistics will be discarded!")

        if response:
            self.parent.statistics.reset()
            self.parent.throw_history.clear_table()
            self.parent.game.start = None
        else:
            pass    # Session continues if user clicks Cancel

    def finish(self) -> None:
        """Insert data into database and close application"""

        # Insert game
        if self.parent.game.start:
            self.parent.game.end = datetime.now()
            game_data = (
                self.parent.game.game_id,
                self.parent.game.start,
                self.parent.game.game_type
                )
            self.parent.db.insert_game(game_data)

        # Insert throws
        for value in self.parent.throw_history.get_records():
            throw_data = tuple(value[1:-1])
            self.parent.db.insert_data(throw_data)
        self.parent.destroy()


class ThrowHistory(ttk.LabelFrame):
    def __init__(self, parent, *args, **kwargs) -> None:
        super().__init__(parent, *args, **kwargs)
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.items = []

        columns = {
            "id": ("ID", True),
            "timestep": ("Timestep", False),
            "throw_1": ("1st Throw", True),
            "throw_2": ("2nd Throw", True),
            "throw_3": ("3rd Throw", True),
            "throw_sum": ("SUM", True)
        }
        self.throw_history = ttk.Treeview(self, columns=list(columns.keys()))
        self.throw_history.grid(row=0, column=0, padx=10, pady=10,
                                sticky="ns")

        # Column config
        self.throw_history['show'] = 'headings'
        self.throw_history["displaycolumns"] = [
            column for column in columns if columns[column][1]
            ]
        for column in columns:
            self.throw_history.heading(column, text=columns[column][0])
            self.throw_history.column(column, width=80, anchor=tk.CENTER)

        # Throw history Scrollbar
        scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL,
                                  command=self.throw_history.yview)
        self.throw_history.configure(yscroll=scrollbar.set)
        scrollbar.grid(row=0, column=1, sticky='ns')

    def add_record(self, record: tuple) -> None:
        ts = datetime.timestamp(datetime.now())
        if self.items:
            last_id = int(self.throw_history.item(self.items[-1])["values"][0])
        else:
            last_id = 0
        values = [last_id + 1] + [ts] + [*record]
        self.throw_history.insert("", tk.END, values=values)
        self.items = self.throw_history.get_children()

    def clear_table(self) -> None:
        self.throw_history.delete(*self.items)
        self.items = []

    def get_records(self) -> Generator[str, None, None]:
        for item in self.items:
            yield self.throw_history.item(item)["values"]


DartsApp()
