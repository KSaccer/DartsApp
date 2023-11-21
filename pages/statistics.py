import tkinter as tk
import tkinter.ttk as ttk
import os
import pandas as pd
import sqlite3
import seaborn as sns
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure


FONT_TITLE = ("Arial", 20, "bold")
FONT_DEFAULT = ("Arial", 10)

SQL_SCRIPT = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), 
    "sql", 
    "avg.sql")


class StatPage(ttk.Frame):
    def __init__(self, parent, db, *args, **kwargs) -> None:
        super().__init__(parent, *args, **kwargs)
        self.db = db
        self.rowconfigure((0, 1, 2), weight=1)
        self.columnconfigure(0, weight=1)
        self.create_gui()
    
    def create_gui(self) -> None:
        self.page_title = PageTitle(self)
        self.page_title.grid(row=0, column=0)
        
        self.plot_selector = PlotSelector(self)
        self.plot_selector.grid(row=1, column=0, sticky="news")

        self.plot = Plot(self)
        self.plot.grid(row=2, column=0, sticky="news")
        

class PageTitle(ttk.Frame):
    def __init__(self, parent, *args, **kwargs) -> None:
        super().__init__(parent, *args, **kwargs)
        label = ttk.Label(self, text="Darts Practice Statistics",
                          font=FONT_TITLE)
        label.pack(expand=True, fill="both")


class PlotSelector(ttk.Frame):
    def __init__(self, parent, *args, **kwargs) -> None:
        super().__init__(parent, *args, **kwargs)
        self.parent = parent
        self.rowconfigure(0, weight=1)
        self.columnconfigure((0, 1, 2, 3), weight=1)

        plot_type_label = ttk.Label(self, text="Plot Type: ")
        plot_type_label.grid(row=0, column=0, sticky="e")

        self.plot_type = ttk.Combobox(self)
        self.plot_type["values"] = ["Averages", "Nr of Sessions"]
        self.plot_type["state"] = "readonly"
        self.plot_type.grid(row=0, column=1, sticky="w")
        self.plot_type.current(0)

        time_scale_label = ttk.Label(self, text="Time Scale: ")
        time_scale_label.grid(row=0, column=2, sticky="e")

        self.time_scale = ttk.Combobox(self)
        self.time_scale["values"] = ["Monthly", "Yearly"]
        self.time_scale["state"] = "readonly"
        self.time_scale.grid(row=0, column=3, sticky="w")
        self.time_scale.current(0)

        self.create_bindings()

    def create_bindings(self) -> None:
        self.time_scale.bind("<<ComboboxSelected>>", lambda event=None: 
                             self.parent.plot.update_plot(self.time_scale.get()))

    


class Plot(ttk.Frame):
    
    def __init__(self, parent, *args, **kwargs) -> None:
        super().__init__(parent, *args, **kwargs)
        self.parent = parent
        self.df = self.create_df(self.parent.db, SQL_SCRIPT)
        self.fig, self.ax = self.create_plot(self.df)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(padx=10, pady=10, 
                                    side=tk.TOP, fill=tk.BOTH, expand=True)

    def create_df(self, db: "Database", sql_script: str) -> pd.DataFrame:
        """Connect to database and run SQL query"""
        conn = sqlite3.connect(db.db_path)
        with open(sql_script, "r") as query:
            df = pd.read_sql_query(query.read(), conn, 
                                   parse_dates={"date": {"format": "%Y-%m-%d"}})
        df = df.set_index("date")
        df = df.resample("M").sum()
        conn.close()
        return df
    
    def create_plot(self, df: pd.DataFrame) -> Figure:
        """Create plot"""
        # Figure setup
        fig, ax = plt.subplots(1, 1)
        fig.tight_layout(h_pad=5)
        # Creating plots
        sns.lineplot(x=df.index, y=df.overall_score / df.visits, 
                          color="tab:blue", marker='o', ax=ax)
        # Formatting
        years, months  = mdates.YearLocator(), mdates.MonthLocator()   # every year
        years_format = mdates.DateFormatter('%Y')
        months_format = mdates.DateFormatter('%m')
        ax.set_axisbelow(True)
        ax.xaxis.grid(color='gray', linestyle='dashed')
        ax.yaxis.grid(color='gray', linestyle='dashed')
        ax.xaxis.set_major_locator(years)
        ax.xaxis.set_major_formatter(years_format)
        ax.xaxis.set_minor_locator(months)
        ax.xaxis.set_minor_formatter(months_format)
        for label in ax.get_xticklabels():
            label.set_rotation(90)

        return fig, ax
    
    def update_plot(self, settings: str) -> None: 
        # resample df
        df = self.parent.plot.df.resample(settings[0]).sum() # Yearly -> Y / Monthly -> M
        new_fig, new_ax = self.create_plot(df)
        new_fig.set_size_inches(self.fig.get_size_inches())
        self.canvas.figure = new_fig
        self.canvas.draw()

        
if __name__ == "__main__":
    pass