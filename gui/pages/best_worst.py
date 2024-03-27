import pandas as pd
import sqlite3
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
        
        self.best_worst_avg_display = BestWorstAvgDisplay(self, 
                                                              text="Averages")
        self.best_worst_avg_display.grid(row=1, column=1,
                                           padx=(5, 10), pady=5, sticky="news")

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
        self.start_date_entry = DateEntry(self, width=12, 
                                          background=COLOR_BG_DATE_ENTRY, 
                                          foreground='white', borderwidth=1)
        self.start_date_entry.grid(row=0, column=1, sticky="ew",
                                   padx=10, pady=(10, 5))
        self.start_date_entry.set_date( date(date.today().year, 1, 1))

        self.end_date_label = ttk.Label(self, text="End:")
        self.end_date_label.grid(row=1, column=0, sticky="w", padx=10, pady=5)
        self.end_date_entry = DateEntry(self, width=12, 
                                        background=COLOR_BG_DATE_ENTRY, 
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
        start_date, end_date, nr_of_visits = self.get_settings()
        # create DataFrame acc. to set date interval
        best_worse_dataframe = self._create_best_worst_dataframe(start_date, end_date)
        # find best and worst performance
        best, worst = self._find_best_and_worst(best_worse_dataframe, nr_of_visits)
        # update gui
        self.master.best_worst_avg_display._update_best_worst_values(best[0], worst[0])
        self.master.table_for_best.add_records(best[1])
        self.master.table_for_worst.add_records(worst[1])

    def get_settings(self) -> tuple:
        """Read in settings into a tuple"""
        start_date = self.start_date_entry.get_date()
        end_date = self.end_date_entry.get_date()
        nr_of_visits = int(self.nr_of_visits_entry.get())
        return (start_date, end_date, nr_of_visits)
    
    def _create_best_worst_dataframe(self, start_date: date, end_date: date) -> pd.DataFrame:
        """Read data from database, that are between start_date and end_date"""
        conn = sqlite3.connect(self.master.db.db_path)
        
        sql_script = f"""SELECT STRFTIME("%Y-%m-%d", games.game_start) AS date, 
                        throws.game_id, 
                        throws.throw_1, throws.throw_2, throws.throw_3, 
                        sum
                        FROM games
                        JOIN throws ON games.game_id=throws.game_id
                        WHERE date BETWEEN "{str(start_date)}" AND "{str(end_date)}";"""
        
        df = pd.read_sql_query(sql_script, conn, 
                               parse_dates={"date": {"format": "%Y-%m-%d"}})
        return df
    
    def _find_best_and_worst(self, df: pd.DataFrame, rolling_avg_window) -> tuple:
        """Find best and worst 3-dart averages using the given window
        for the rolling average"""
        best_average_overall, worst_average_overall = 0, 1000
        game_id_min, game_id_max = df.game_id.min(), df.game_id.max()
         
        for game_id in range(game_id_min, game_id_max + 1):
            
            df_one_game = df[df["game_id"] == game_id]
            df_one_game_rolled = df_one_game["sum"].rolling(rolling_avg_window).mean()
            
            best_average = df_one_game_rolled.max()
            best_average_row_id = df_one_game_rolled.idxmax() 

            worst_average = df_one_game_rolled.min()
            worst_average_row_id = df_one_game_rolled.idxmin()

            if best_average > best_average_overall:
                best_average_overall = best_average
                best_throws = df.iloc[
                    best_average_row_id - rolling_avg_window + 1 : best_average_row_id + 1
                    ]
            if worst_average < worst_average_overall:
                worst_average_overall = worst_average
                worst_throws = df.iloc[
                    worst_average_row_id - rolling_avg_window + 1 : worst_average_row_id + 1
                    ]

        return ((best_average_overall, best_throws), 
                (worst_average_overall, worst_throws))
  
    

        

class PageTitle(ttk.Frame):
    """Class for page title"""
    def __init__(self, parent, *args, **kwargs) -> None:
        """Construct page title Label"""
        super().__init__(parent, *args, **kwargs)
        page_title = ttk.Label(self, text="Best and worst performance",
                          font=FONT_TITLE, foreground=COLOR_FONT_TITLE)
        page_title.pack(expand=True, fill="both", pady=10)      


class BestWorstAvgDisplay(ttk.LabelFrame):
    """Place to show the best and worst averages"""
    def __init__(self, parent, *args, **kwargs) -> None:
        """Construct labels, that will show the results"""
        super().__init__(parent, *args, **kwargs)
        self.rowconfigure((0, 1), weight=1)
        self.columnconfigure((0, 1), weight=1)
        self.best_avg_display = ttk.Label(self, text="Best:", 
                                          font=FONT_BEST_WORST_DISPLAY,
                                          foreground=COLOR_FONT_BEST_WORST)
        self.best_avg_display.grid(row=0, column=0, 
                                padx=10, pady=10, sticky="nw")
        
        self.best_avg_value = ttk.Label(self, text="0.0", 
                                        font=FONT_BEST_WORST_DISPLAY,
                                        foreground=COLOR_FONT_BEST_WORST)
        self.best_avg_value.grid(row=0, column=1, 
                                 padx=10, pady=10, sticky="nw")

        self.worst_avg_display = ttk.Label(self, text="Worst:",
                                           font=FONT_BEST_WORST_DISPLAY, 
                                           foreground=COLOR_FONT_BEST_WORST)
        self.worst_avg_display.grid(row=1, column=0, 
                                 padx=10, pady=10, sticky="nw")

        self.worst_avg_value = ttk.Label(self, text="0.0", 
                                         font=FONT_BEST_WORST_DISPLAY,
                                         foreground=COLOR_FONT_BEST_WORST)
        self.worst_avg_value.grid(row=1, column=1, 
                                 padx=10, pady=10, sticky="nw")

    def _update_best_worst_values(self, best: float, worst: float) -> None:
        """Update the displayed best and worst averages with 
        the given values"""
        self.best_avg_value.config(text=f"{best:.1f}")
        self.worst_avg_value.config(text=f"{worst:.1f}")


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
        """Add a vertical scrollbar widget to the table"""
        scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, 
                                  command=self.table.yview)
        self.table.configure(yscroll=scrollbar.set)
        scrollbar.grid(row=0, column=1, 
                       padx=0, sticky="news")
        
    def add_records(self, df: pd.DataFrame) -> None:
        """Add records from the provided dataframe to the table"""
        self._clear_table()
        for i in range(df.shape[0]):
            self.table.insert("", tk.END, values=df.iloc[i, 1:].tolist())

    def _clear_table(self) -> None:
        """Remove items from table"""
        self.table.delete(*self.table.get_children())


if __name__ == "__main__":
    pass