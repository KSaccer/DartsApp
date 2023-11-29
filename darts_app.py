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
        self.statpage = StatPage(self, self.db)
        self.statpage.grid(row=0, column=1, sticky="news")
        self.settings = Settings(self)
        self.settings.grid(row=0, column=1, sticky="news")
        self.dashboard.tkraise()

        # Side Menu
        menu_style = ttk.Style()
        menu_style.configure("Menu.TFrame", background="#44546A")
        self.menu = Menu(self,
                         items={
                               "DASHBOARD": self.dashboard,
                               "SCORING": self.scoring,
                            #    "STATISTICS": self.statpage,
                               "STATISTICS": {
                                   "Averages": self.statpage,
                                   "Histograms": self.statpage,
                               },
                               "SETTINGS": self.settings,
                               "QUIT": None,
                         },
                         style="Menu.TFrame")
        self.menu.grid(row=0, column=0, sticky="news")

        # Run
        self.mainloop()

    def close_app(self) -> None:
        really_quit = messagebox.askokcancel(
            "Confirmation",
            "Do you really want to close the application?",
            )

        if really_quit:
            self.quit()
        else:
            pass


class Sidebar(ttk.Frame):
    """Sidebar is the main ttk.Frame widget, that serves as a container
    for Menu elements"""

    def __init__(self, parent, *args, **kwargs) -> None:
        """Construct Sidebar widget"""
        super().__init__(parent, *args, **kwargs)
        self.parent = parent

    def color_config(self, widget, color: str) -> None:
        """Change widget color"""
        widget.configure(background=color)

    def create_bindings(self, widget: tk.Widget, reference: ttk.Frame) -> None:
        """Assign callback functions for specific events of widget"""
        widget.bind("<Enter>", lambda event=None:
                    self.color_config(widget, "#333F50"))
        widget.bind("<Leave>", lambda event=None:
                    self.color_config(widget, "#44546A"))
        widget.bind("<Button-1>", lambda event=None:
                    self.menu_clicked(reference))

    def go_to_page(self, page: ttk.Frame) -> None:
        """Show the main frame of the given page.
        If page is None (Quit button), call the close_app function"""
        if page:
            page.create_gui()
            page.tkraise()
        else:
            self.parent.close_app()

    def submenu_switch(self, submenu) -> None:
        """Show/Hide Submenu elements"""
        if submenu.visible:
            submenu.grid_remove()
            submenu.visible = False
        else:
            submenu.grid()
            submenu.visible = True


    def menu_clicked(self, reference: tk.Widget) -> None:
        """Assign the corresponding callback function to the widget.
        The widget is a main menu element: call go_to_page
        The widget is a submenu element: call submenu_switch"""
        if isinstance(reference, Submenu):
            self.submenu_switch(reference)
        else:
            self.go_to_page(reference)


class Menu(Sidebar):
    def __init__(self, parent, items: dict, *args, **kwargs) -> None:
        """Construct Menu widget"""
        super().__init__(parent, *args, **kwargs)
        self.parent = parent
        self.items = items
        self._build_menu()

    def _build_menu(self) -> None:
        """Construct main- and submenu widgets, create bindings"""
        self.columnconfigure(0, weight=1)
        space = tk.Label(self, text="", background="#44546A", padx=20, pady=10)
        space.grid(row=0, column=0)
        row = 1
        for item in self.items:
            if isinstance(self.items[item], dict):
                label = tk.Label(self, text=item, font=FONT_MENU,
                                background="#44546A", foreground="white",
                                anchor="w", padx=20, pady=10)
                label.grid(row=row, column=0, sticky="news")
                row += 1
                submenu = Submenu(self, self.items[item])
                submenu.grid(row=row, column=0, sticky="news")
                submenu.grid_remove()
                row += 1
                self.create_bindings(label, submenu)
            else:
                label = tk.Label(self, text=item, font=FONT_MENU,
                                background="#44546A", foreground="white",
                                anchor="w", padx=20, pady=10)
                label.grid(row=row, column=0, sticky="news")
                row += 1
                self.create_bindings(label, self.items[item])




class Submenu(Sidebar):
    def __init__(self, parent, items: dict, *args, **kwargs) -> None:
        """Construct Submenu widget"""
        super().__init__(parent, *args, **kwargs)
        self.items = items
        self._build_menu()
        self.visible = False


    def _build_menu(self) -> None:
        """Construct submenu widgets, create bindings"""
        for item in self.items:
            label = tk.Label(self, text="  "+item, font=FONT_MENU,
                            background="#44546A", foreground="white",
                            anchor="w", padx=20, pady=10)
            label.pack(side=tk.TOP, fill=tk.BOTH, anchor=tk.NW)
            self.create_bindings(label, self.items[item])

DartsApp()
