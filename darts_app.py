import tkinter as tk
import tkinter.ttk as ttk

from db.database import DataBase
from gui.constants import *
from gui.widgets.custom_popup import CustomPopup
from gui.widgets.menu import Menu
from gui.pages.dashboard import Dashboard
from gui.pages.scoring import Scoring
from gui.pages.settings import Settings
from gui.pages.statistics import StatPage
from gui.pages.best_worst import BestWorst


DB_PATH = os.path.join(
    os.path.dirname(__file__),
    "db",
    "darts_data.db"
)


class DartsApp(tk.Tk):
    """Main application class"""

    def __init__(self, *args, **kwargs) -> None:
        """Initialize main application class"""
        super().__init__(*args, **kwargs)
        self.config_app()
        self.setup_database()
        self.create_pages()
        self.create_sidemenu()
        # Run
        self.mainloop()

    def config_app(self) -> None:
        """Configure main application properties"""
        self.rowconfigure(0, weight=1)
        self.columnconfigure((0, 1), weight=1)
        self.title("Darts Scoring App")
        self.iconbitmap(default="pics/dartboard.ico")
        self.geometry(f"{GEOMETRY_W}x{GEOMETRY_H}")
        self.resizable(False, False)
        self.option_add("*Font", FONT_DEFAULT)
        self.protocol("WM_DELETE_WINDOW", self.close_app)

    def setup_database(self) -> None:
        """Create a DataBase instance"""
        self.db = DataBase(DB_PATH)

    def create_pages(self) -> None:
        """Construct all the pages that will be available through the sidemenu"""
        self.dashboard = Dashboard(self)
        self.dashboard.grid(row=0, column=1, sticky="news")
        self.scoring = Scoring(self, self.db)
        self.scoring.grid(row=0, column=1, sticky="news")
        self.statpage = StatPage(self, self.db)
        self.statpage.grid(row=0, column=1, sticky="news")
        self.bestworst = BestWorst(self, self.db)
        self.bestworst.grid(row=0, column=1, sticky="news")
        self.settings = Settings(self)
        self.settings.grid(row=0, column=1, sticky="news")
        self.dashboard.tkraise()

    def create_sidemenu(self) -> None:
        """Create the side menu"""
        menu_style = ttk.Style()
        menu_style.configure("Menu.TFrame", background="#44546A")
        self.menu = Menu(self,
                         items={
                               "DASHBOARD": self.dashboard,
                               "SCORING": self.scoring,
                               "STATISTICS": {
                                   "Averages": self.statpage,
                                   "Histograms": self.statpage,
                                   "Best-Worst": self.bestworst,
                               },
                               "SETTINGS": self.settings,
                               "QUIT": None,
                         },
                         style="Menu.TFrame")
        self.menu.grid(row=0, column=0, sticky="news")

    def close_app(self) -> None:
        """Show messagebox to confirm to quit, then close application"""
        CustomPopup("Confirmation", "Do you really want to close the application?", self.quit)


DartsApp()
