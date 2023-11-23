import tkinter as tk
import tkinter.ttk as ttk
import os
import pandas as pd
import sqlite3
import seaborn as sns
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure, Axes
from typing import Self


FONT_TITLE = ("Arial", 20, "bold")
FONT_DEFAULT = ("Arial", 10)

SQL_SCRIPT_AVG = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), 
    "sql", 
    "avg.sql")

SQL_SCRIPT_NR_OF_SESSIONS = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), 
    "sql", 
    "nr_of_games.sql")


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

        self.plot_canvas = PlotCanvas(self)
        self.plot_canvas.grid(row=2, column=0, sticky="news")
        

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

    def update_time_scale(self, event) -> None:
        """Resample plot and update the canvas"""
        sampling_rule = self.time_scale.get()[0]
        new_plot = self.parent.plot_canvas.plot.resample_plot(sampling_rule)
        self.parent.plot_canvas.add_plot(new_plot)

    def update_plot_type(self, event) -> None:
        plot_type = self.plot_type.get()
        sampling_rule = self.time_scale.get()[0]
        if plot_type == "Averages":
            sql_script = SQL_SCRIPT_AVG
        else:
            sql_script = SQL_SCRIPT_NR_OF_SESSIONS
        new_plot = Plot(self.parent.db, sql_script, plot_type)
        new_plot.resample_plot(sampling_rule)
        self.parent.plot_canvas.add_plot(new_plot)

    def create_bindings(self) -> None:
        self.time_scale.bind("<<ComboboxSelected>>", self.update_time_scale)
        self.plot_type.bind("<<ComboboxSelected>>", self.update_plot_type)


class PlotCanvas(ttk.Frame):
    
    def __init__(self, parent, *args, **kwargs) -> None:
        super().__init__(parent, *args, **kwargs)
        self.parent = parent
        self.canvas = self._create_canvas()
        self.plot = Plot(self.parent.db, SQL_SCRIPT_AVG, "Averages")
        self.add_plot(self.plot)
        # self.plot_size = self.plot.fig.get_size_inches()
        
    def _create_canvas(self) -> FigureCanvasTkAgg:
        """Create canvas widget with matplotlib backend"""
        canvas = FigureCanvasTkAgg(None, master=self)
        canvas.get_tk_widget().pack(padx=10, pady=10, 
                                    side=tk.TOP, fill=tk.BOTH, expand=True)
        return canvas
        
    def add_plot(self, plot: "Plot") -> None:
        """Add Figure to canvas"""
        fig_size = self.canvas.figure.get_size_inches()
        self.canvas.figure.clear()
        self.canvas.draw()
        plot.fig.set_size_inches(fig_size)
        self.canvas.figure = plot.fig
        self.canvas.draw()
        self.plot = plot
        

class Plot():

    def __init__(self, db: "Database", sql_script: str, plot_type: str) -> None:
        self._df = self._create_df(db, sql_script)
        self.plot_type = plot_type
        self.fig, self.ax = self._create_plot(self._df)
        self.fig_size = self.fig.get_size_inches()

    def _create_df(self, db: "Database", sql_script: str) -> pd.DataFrame:
        """Connect to database and run SQL query"""
        conn = sqlite3.connect(db.db_path)
        with open(sql_script, "r") as query:
            df = pd.read_sql_query(query.read(), conn, 
                                   parse_dates={"date": {"format": "%Y-%m-%d"}})
        df = df.set_index("date")
        df = df.resample("M").sum()
        conn.close()
        return df
    
    def _create_plot(self, df: pd.DataFrame) -> (Figure, Axes):
        """Create plot"""
        # Figure setup
        fig, ax = plt.subplots(1, 1)
        fig.tight_layout(h_pad=5)
        # Creating plots
        if self.plot_type == "Averages":
            sns.lineplot(x=df.index, y=df.overall_score / df.visits, 
                            color="tab:blue", marker='o', ax=ax)
        elif self.plot_type == "Nr of Sessions":
            ax.bar(df.index, df.nr_of_games, width=15, 
                   color="tab:blue",  edgecolor='black')
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
    
    def resample_plot(self, sampling_rule: str) -> Self: 
        """Resample time axis of plot (yearly / monthly)"""
        df = self._df.resample(sampling_rule).sum()
        self.fig, self.ax = self._create_plot(df)
        self.fig.set_size_inches(self.fig_size)
        return self

        
if __name__ == "__main__":
    pass