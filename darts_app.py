import tkinter as tk
import tkinter.ttk as ttk
from tkinter import messagebox
import os

from db.database import DataBase
from pages.dashboard import Dashboard
from pages.scoring import Scoring
from pages.settings import Settings
from pages.statistics import StatPage



FONT_TITLE = ("Arial", 20, "bold")
FONT_DEFAULT = ("Arial", 10)
FONT_MENU = ("Malgun Gothic", 12)

DB_PATH = os.path.join(
    os.path.dirname(__file__),
    "db",
    "darts_data.db"
)


class DartsApp(tk.Tk):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        # Main Congif
        self.rowconfigure(0, weight=1)
        self.columnconfigure((0, 1), weight=1)
        self.title("Darts Scoring App")
        self.iconbitmap(default="pics/dartboard.ico")
        self.geometry("1000x600")
        self.resizable(False, False)
        self.option_add("*Font", FONT_DEFAULT)
        self.protocol("WM_DELETE_WINDOW", self.close_app)

        # Database
        self.db = DataBase(DB_PATH)

        # Pages
        self.dashboard = Dashboard(self)
        self.dashboard.grid(row=0, column=1, sticky="news")
        self.scoring = Scoring(self, self.db)
        self.scoring.grid(row=0, column=1, sticky="news")
        self.statpage = StatPage(self)
        self.statpage.grid(row=0, column=1, sticky="news")
        self.settings = Settings(self)
        self.settings.grid(row=0, column=1, sticky="news")

        # Side Menu
        menu_style = ttk.Style()
        menu_style.configure("Menu.TFrame", background="#44546A")
        self.menu = Menu(self, style="Menu.TFrame")
        self.menu.grid(row=0, column=0, sticky="news")

        # Run
        self.mainloop()

    def close_app(self) -> None:
        really_quit = messagebox.askokcancel(
            "Confirmation",
            "Do you really want to close the application?",
            )

        if really_quit:
            self.destroy()
        else:
            pass


class Menu(ttk.Frame):
    def __init__(self, parent, *args, **kwargs) -> None:
        super().__init__(parent, *args, **kwargs)
        self.parent = parent

        menuitems = {
            "DASHBOARD": self.parent.dashboard,
            "SCORING": self.parent.scoring,
            "STATISTICS": self.parent.statpage,
            "SETTINGS": self.parent.settings,
            "QUIT": None,
        }
        tk.Label(self, text="", background="#44546A", padx=20, pady=10).pack()
        for item in menuitems:
            label = tk.Label(self, text=item, font=FONT_MENU,
                             background="#44546A", foreground="white",
                             anchor="w", padx=20, pady=10)
            label.pack(side=tk.TOP, fill=tk.BOTH, anchor=tk.NW)
            self.create_bindings(label, menuitems[item])

    def color_config(self, widget, color: str) -> None:
        widget.configure(background=color)

    def create_bindings(self, widget, page: ttk.Frame) -> None:
        widget.bind("<Enter>", lambda event=None:
                    self.color_config(widget, "#333F50"))
        widget.bind("<Leave>", lambda event=None:
                    self.color_config(widget, "#44546A"))
        widget.bind("<Button-1>", lambda event=None:
                    self.go_to_page(page))

    def go_to_page(self, page: ttk.Frame) -> None:
        if page:
            page.tkraise()
        else:
            self.parent.close_app()


DartsApp()
