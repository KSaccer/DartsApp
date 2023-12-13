import tkinter as tk
import tkinter.ttk as ttk
from tkinter import messagebox
import os

from db.database import DataBase
from pages.dashboard import Dashboard
from pages.scoring import Scoring
from pages.settings import Settings
from pages.statistics import StatPage


GEOMETRY_W = 1000
GEOMETRY_H = 600

FONT_TITLE = ("Arial", 20, "bold")
FONT_DEFAULT = ("Arial", 10)
FONT_MENU = ("Malgun Gothic", 12)

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
        """Construct all the pages that will available through the sidemenu"""
        self.dashboard = Dashboard(self)
        self.dashboard.grid(row=0, column=1, sticky="news")
        self.scoring = Scoring(self, self.db)
        self.scoring.grid(row=0, column=1, sticky="news")
        self.statpage = StatPage(self, self.db)
        self.statpage.grid(row=0, column=1, sticky="news")
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
                               },
                               "SETTINGS": self.settings,
                               "QUIT": None,
                         },
                         style="Menu.TFrame")
        self.menu.grid(row=0, column=0, sticky="news")

    def close_app(self) -> None:
        """Show messagebox to confirm to quit, then close application"""
        QuitPopup("Confirmation", "Do you really want to close the application?")


class QuitPopup(tk.Toplevel):
    """Popup message to confirm to quit.
    Used instead of tk messaagebox, because that always centered on screen
    instead of application, even though parent kwarg was set"""
    def __init__(self, title, message, **kwargs) -> None:
        super().__init__(**kwargs)
        """Construct the QuitPopup widget and make it a modal window.
        Main window remains inactive until this one closed."""
        self.message = message
        self.title(title)
        self.resizable(False, False)
        self._set_geometry()
        self._construct_widgets()
        # Hide minimize and maximize icons
        self.transient(self.master)
        # Make the popup a modal window
        self.grab_set()
        self.master.wait_window(self)

    def _set_geometry(self) -> None:
        """Determine widget target position and setup geometry"""
        width = 320
        height = 120
        pos_x = self.master.winfo_x() + GEOMETRY_W // 2 - width // 2
        pos_y = self.master.winfo_y() + GEOMETRY_H // 2 - height // 2
        # Place it in the center of the main window
        self.geometry(f"{width}x{height}+{pos_x}+{pos_y}")

    def _construct_widgets(self) -> None:
        """Construct the elements of the QuitPopup"""
        self.rowconfigure((0, 1, 2), weight=1)
        self.columnconfigure((0, 1), weight=1)
        icon = tk.Label(self, image="::tk::icons::question", background="white")
        icon.grid(row=0, column=0, rowspan=2, sticky="news")
        label = tk.Label(self, text=self.message, background="white", font=("Arial", 9))
        label.grid(row=0, column=1, rowspan=2, columnspan=2, sticky="news")
        ok = ttk.Button(self, text="OK", command=self._close_app)
        ok.grid(row=2, column=1, sticky="e")
        cancel = ttk.Button(self, text="Cancel", command=self.destroy)
        cancel.grid(row=2, column=2, padx=(10, 10), sticky="e") 
        ok.focus()

    def _close_app(self) -> None:
        """Callback funtcion for the yes button. Close the application."""
        # Need to be destroyed first (quit is paused until destroy)
        self.destroy()
        self.master.quit()


class Menu(ttk.Frame):
    """Class for sied menu"""

    def __init__(self, parent, items: dict, *args, **kwargs) -> None:
        """Construct Menu widget, create bindings"""
        super().__init__(parent, *args, **kwargs)
        self.parent = parent
        self.items = items
        self.menu_structure = self._build_menu()
        for menu_item, reference in self.menu_structure.items():
            self._create_bindings(menu_item, reference)

    def _build_menu(self) -> dict:
        """Construct main- and submenu widgets. Return a dictionary,
        where the key is a menu item, the value is either a page, or
        a list of submenu items"""
        structure = {}
        spacer = tk.Label(self, text="", background="#44546A", padx=20, pady=10)
        spacer.grid(row=0, column=0)
        row = 1
        for item in self.items:
            # Submenu
            if isinstance(self.items[item], dict):
                submenu_items = self.items[item]
                main_menu_label = tk.Label(self, text=item, font=FONT_MENU,
                                background="#44546A", foreground="white",
                                anchor="w", padx=20, pady=10)
                main_menu_label.grid(row=row, column=0, sticky="news")
                row += 1
                submenus = []
                for submenu_item in submenu_items:
                    submenu_label = tk.Label(self, text="  "+submenu_item, 
                                             font=FONT_MENU, 
                                             background="#44546A", 
                                             foreground="white", 
                                             anchor="w", 
                                             padx=20, pady=10)
                    submenu_label.grid(row=row, column=0, sticky="news")
                    submenu_label.grid_remove()
                    row += 1
                    submenus.append(submenu_label)
                    structure[submenu_label] = submenu_items[submenu_item]
                structure[main_menu_label] = submenus
            # Main menu
            else:
                main_menu_label = tk.Label(self, text=item, font=FONT_MENU,
                                background="#44546A", foreground="white",
                                anchor="w", padx=20, pady=10)
                main_menu_label.grid(row=row, column=0, sticky="news")
                structure[main_menu_label] = self.items[item]
                row += 1
        return structure

    def _color_config(self, widget, color: str) -> None:
        """Change widget color"""
        widget.configure(background=color)

    def _create_bindings(self, widget, reference: dict) -> None:
        """Assign callback functions for specific events of widget"""
        widget.bind("<Enter>", lambda event=None:
                    self._color_config(widget, "#333F50"))
        widget.bind("<Leave>", lambda event=None:
                    self._color_config(widget, "#44546A"))
        widget.bind("<Button-1>", lambda event=None:
                    self._menu_clicked(reference))

    def _menu_clicked(self, reference: tk.Widget) -> None:
        """Assign the corresponding callback function to the widget.
        The widget is a main menu element: call go_to_page
        The widget is a submenu element: call submenu_switch"""
        if isinstance(reference, list):
            self._submenu_switch(reference)
        else:
            self._go_to_page(reference)

    def _go_to_page(self, page: ttk.Frame) -> None:
        """Show the main frame of the given page.
        If page is None (Quit button), call the close_app function"""
        if page:
            page.create_gui()
            page.tkraise()
        else:
            self.parent.close_app()

    def _submenu_switch(self, submenus: list) -> None:
        """Show/Hide Submenu elements"""
        for submenu in submenus:
            if submenu.grid_info():
                submenu.grid_remove()
            else:
                submenu.grid()


DartsApp()
