import tkinter as tk
import tkinter.ttk as ttk
from datetime import date
from tkcalendar import DateEntry
from ..constants import *


class BestWorst(ttk.Frame):
    """Main class for Best-Worst page"""
    def __init__(self, parent, db, *args, **kwargs) -> None:
        """Construct Best-Worst page"""
        super().__init__(parent, *args, **kwargs)
        self.db = db
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=3)
        self.rowconfigure(2, weight=15)
        self.columnconfigure((0, 1), weight=1)
        
    def create_gui(self) -> None:
        """Construct widgets of Statistics page"""
        self.page_title = PageTitle(self)
        self.page_title.grid(row=0, column=0, columnspan=2, 
                             padx=10, pady=(10, 5), sticky="n")
        
        self.best_worst_settings_gui = BestWorstSettings(self, text="Settings")
        self.best_worst_settings_gui.grid(row=1, column=0, 
                                padx=(10, 5), pady=5, sticky="news")

        self.table_for_best = BestWorstTable(self, text="Best performance")
        self.table_for_best.grid(row=2, column=0,
                                 padx=(10, 5), pady=(5, 10), sticky="news")
        
        self.table_for_worst = BestWorstTable(self, text="Worst performance")
        self.table_for_worst.grid(row=2, column=1,
                                 padx=(5, 10), pady=(5, 10), sticky="news")
        

class BestWorstSettings(ttk.LabelFrame):
    """Container for settings elements"""
    def __init__(self, parent, *args, **kwargs) -> None:
        """Construct gui elements for settings"""
        super().__init__(parent, *args, **kwargs)
        self.rowconfigure((0, 1, 2, 3), weight=1)
        self.columnconfigure((0, 1), weight=1)
        self.start_date_label = ttk.Label(self, text="Start:")
        self.start_date_label.grid(row=0, column=0, sticky="w", 
                                   padx=10, pady=(10, 5))
        self.start_date_entry = DateEntry(self, width=12, background='#44546A', 
                                          foreground='white', borderwidth=1)
        self.start_date_entry.grid(row=0, column=1, sticky="ew",
                                   padx=10, pady=(10, 5))
        self.start_date_entry.set_date( date(date.today().year, 1, 1))

        self.end_date_label = ttk.Label(self, text="End:")
        self.end_date_label.grid(row=1, column=0, sticky="w", padx=10, pady=5)
        self.end_date_entry = DateEntry(self, width=12, background='#44546A', 
                                        foreground='white', borderwidth=2)
        self.end_date_entry.grid(row=1, column=1, sticky="ew", padx=10, pady=5)

        self.nr_of_visits_label = ttk.Label(self, text="Nr of visits:")
        self.nr_of_visits_label.grid(row=2, column=0, sticky="ws", 
                                     padx=10, pady=(5, 10))
        self.nr_of_visits_entry = ttk.Entry(self, )
        self.nr_of_visits_entry.grid(row=2, column=1, sticky="ews", 
                                     padx=10, pady=(5, 10))
        self.nr_of_visits_entry.insert(0, "7")

        self.analyze_button = ttk.Button(self, text="Analyze", 
                                         command=self.analyze_button_clicked)
        self.analyze_button.grid(row=3, column=1, sticky="news", 
                                 padx=10, pady=(5, 10))

    def analyze_button_clicked(self):
        # read in settings
        best_worst_settings = self.get_settings()
        # create DataFrame acc. to set date interval
        # find best and worst performance
        # fill tables

    def get_settings(self) -> tuple:
        """Read in settings into a tuple"""
        start_date = self.start_date_entry.get_date()
        end_date = self.end_date_entry.get_date()
        nr_of_visits = self.nr_of_visits_entry.get()
        return (start_date, end_date, nr_of_visits)

class PageTitle(ttk.Frame):
    """Class for page title"""
    def __init__(self, parent, *args, **kwargs) -> None:
        """Construct page title Label"""
        super().__init__(parent, *args, **kwargs)
        label = ttk.Label(self, text="Best and worst performance",
                          font=FONT_TITLE)
        label.pack(expand=True, fill="both", pady=10)      


class BestWorstTable(ttk.LabelFrame):
    
    columns = {
        "id": "ID",
        "throw_1": "1st Throw",
        "throw_2": "2nd Throw",
        "throw_3": "3rd Throw",
        "throw_sum": "SUM",
    }

    def __init__(self, parent, *args, **kwargs) -> None:
        """Construct TrowHistory table to store thrown scores"""
        super().__init__(parent, *args, **kwargs)
        self.rowconfigure(0, weight=1)
        self.columnconfigure((0, 1), weight=1)
        self.table = ttk.Treeview(self, 
                                  columns=list(BestWorstTable.columns.keys()))
        self.table.grid(row=0, column=0, 
                        padx=0, pady=10, sticky="nes")
        self.configure_table()
        self.add_table_scrollbar()

    def configure_table(self) -> None:
        """Set titles and width for table columns"""
        self.table["show"] = "headings"
        for column in BestWorstTable.columns:
            self.table.heading(column, text=BestWorstTable.columns[column])
            if column in {"id", "throw_sum"}:
                self.table.column(column, width=50, anchor=tk.CENTER)
            else:
                self.table.column(column, width=75, anchor=tk.CENTER)

    def add_table_scrollbar(self) -> None:
        scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, 
                                  command=self.table.yview)
        self.table.configure(yscroll=scrollbar.set)
        scrollbar.grid(row=0, column=1, 
                       padx=0, sticky="news")


if __name__ == "__main__":
    pass