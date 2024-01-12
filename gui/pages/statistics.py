from __future__ import annotations
import tkinter as tk
import tkinter.ttk as ttk
import os
import pandas as pd
import sqlite3
import seaborn as sns
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
from ..constants import *
from abc import ABC, abstractmethod
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure, Axes
from typing import Self


SQL_SCRIPT_AVG = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
    "sql", 
    "avg.sql")

SQL_SCRIPT_NR_OF_SESSIONS = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
    "sql", 
    "nr_of_games.sql")


class StatPage(ttk.Frame):
    """Main class for Statistics page"""
    def __init__(self, parent, db, *args, **kwargs) -> None:
        """Construct Statistics page"""
        super().__init__(parent, *args, **kwargs)
        self.db = db
        self.rowconfigure((0, 1, 2), weight=1)
        self.columnconfigure(0, weight=1)
    
    def create_gui(self) -> None:
        """Construct widgets of Statistics page"""
        self.page_title = PageTitle(self)
        self.page_title.grid(row=0, column=0, sticky="n")
        
        if self.db.last_game_id > 0:
            self.plot_selector = PlotSelector(self)
            self.plot_selector.grid(row=1, column=0, sticky="news")

            self.plot_canvas = PlotCanvas(self)
            self.plot_canvas.grid(row=2, column=0, sticky="news")
        

class PageTitle(ttk.Frame):
    """Class for page title"""
    def __init__(self, parent, *args, **kwargs) -> None:
        """Construct page title Label"""
        super().__init__(parent, *args, **kwargs)
        label = ttk.Label(self, text="Darts Practice Statistics",
                          font=FONT_TITLE)
        label.pack(expand=True, fill="both", pady=10)


class PlotStrategy(ABC):
    """Strategy Interface for plot builder algorithms"""

    @abstractmethod
    def build_plot(self, db: DataBase) -> (Figure, Axes):
        pass

    @abstractmethod
    def _create_df(self, db: DataBase, sql_script: str) -> None:
        pass

    @abstractmethod
    def _create_plot_content(self, df: pd.DataFrame) -> (Figure, Axes):
        pass

    @abstractmethod
    def _format_plot_content(self, fig: Figure, ax: Axes) -> (Figure, Axes):
        pass


class ThreeDartAvg(PlotStrategy):
    """Strategy for three dart average plot"""

    sql_script = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
        "sql", 
        "avg.sql")
    
    def build_plot(self, db: DataBase, sampling_rule: str) -> (Figure, Axes):
        """Execute plot builder process"""
        # Create DataFrame
        df = self._create_df(db, ThreeDartAvg.sql_script, sampling_rule)
        fig, ax = self._create_plot_content(df)
        fig, ax = self._format_plot_content(fig, ax)
        return (fig, ax)
      
    def _create_df(self, db: DataBase, sql_script: str, sampling_rule: str) -> pd.DataFrame:
        """Create the DataFrame by connecting to the database and running
        the SQL script"""
        conn = sqlite3.connect(db.db_path)
        with open(sql_script, "r") as query:
            df = pd.read_sql_query(query.read(), conn, 
                                   parse_dates={"date": {"format": "%Y-%m-%d"}})
        df = df.set_index("date")
        df = df.resample(sampling_rule).sum()
        conn.close()
        return df
    
    def _create_plot_content(self, df: pd.DataFrame) -> (Figure, Axes):
        """Set up plot and create curves"""
        # Figure setup
        fig, ax = plt.subplots(1, 1)
        fig.tight_layout(h_pad=5)
        # Creating plot
        sns.scatterplot(x=df.index, y=df.overall_score / df.visits, 
                        color="tab:blue", marker='o', ax=ax)
        sns.lineplot(x=df.index, y=df.overall_score / df.visits, 
                        color="lightgray", ax=ax)
        ax.lines[0].set_linestyle("--")
        try:
            df_smooth = df.resample("D").interpolate(method="quadratic")
        except ValueError:
            df_smooth = df
        sns.lineplot(x=df_smooth.index, 
                        y=df_smooth.overall_score / df_smooth.visits, 
                        color="tab:orange", ax=ax
                        )
        return (fig, ax)

    def _format_plot_content(self, fig, ax) -> (Figure, Axes):
        """Format plot axes and appearance"""
        years, months  = mdates.YearLocator(), mdates.MonthLocator()   # every year
        years_format = mdates.DateFormatter('%Y')
        months_format = mdates.DateFormatter('%m')
        ax.set_axisbelow(True)
        ax.xaxis.grid(color='lightgray', linestyle='dashed')
        ax.yaxis.grid(color='lightgray', linestyle='dashed')
        ax.xaxis.set_major_locator(years)
        ax.xaxis.set_major_formatter(years_format)
        ax.xaxis.set_minor_locator(months)
        ax.xaxis.set_minor_formatter(months_format)
        for label in ax.get_xticklabels():
            label.set_rotation(90)
        return (fig, ax)
    

class NrOfSessions(PlotStrategy):
    """Strategy for bar chart showing the nr of session played"""

    sql_script = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
        "sql", 
        "nr_of_games.sql")
    
    def build_plot(self, db: DataBase, sampling_rule: str) -> (Figure, Axes):
        """Execute plot builder process"""
        # Create DataFrame
        df = self._create_df(db, NrOfSessions.sql_script, sampling_rule)
        fig, ax = self._create_plot_content(df)
        fig, ax = self._format_plot_content(fig, ax)
        return (fig, ax)
      
    def _create_df(self, db: DataBase, sql_script: str, sampling_rule: str) -> pd.DataFrame:
        """Create the DataFrame by connecting to the database and running
        the SQL script"""
        conn = sqlite3.connect(db.db_path)
        with open(sql_script, "r") as query:
            df = pd.read_sql_query(query.read(), conn, 
                                   parse_dates={"date": {"format": "%Y-%m-%d"}})
        df = df.set_index("date")
        df = df.resample(sampling_rule).sum()
        conn.close()
        return df

    def _create_plot_content(self, df: pd.DataFrame) -> (Figure, Axes):
        """Set up plot and create curves"""
        # Figure setup
        fig, ax = plt.subplots(1, 1)
        fig.tight_layout(h_pad=5)
        # Creating plot
        ax.bar(df.index, df.nr_of_games, width=15, 
               color="tab:blue",  edgecolor='darkblue')
        return (fig, ax)

    def _format_plot_content(self, fig, ax) -> (Figure, Axes):
        """Format plot axes and appearance"""
        years, months  = mdates.YearLocator(), mdates.MonthLocator()   # every year
        years_format = mdates.DateFormatter('%Y')
        months_format = mdates.DateFormatter('%m')
        ax.set_axisbelow(True)
        ax.xaxis.grid(color='lightgray', linestyle='dashed')
        ax.yaxis.grid(color='lightgray', linestyle='dashed')
        ax.xaxis.set_major_locator(years)
        ax.xaxis.set_major_formatter(years_format)
        ax.xaxis.set_minor_locator(months)
        ax.xaxis.set_minor_formatter(months_format)
        for label in ax.get_xticklabels():
            label.set_rotation(90)
        return (fig, ax)


class PlotSelector(ttk.Frame):
    """Container for drop down menus, with which the plot can be changed"""

    plot_strategies = {
        "Averages": ThreeDartAvg(),
        "Nr of Sessions": NrOfSessions(),
    }

    sampling_rules = {
        "Monthly": "M",
        "Yearly": "Y",
    }

    def __init__(self, parent, *args, **kwargs) -> None:
        """Construct drop downs and labels for it"""
        super().__init__(parent, *args, **kwargs)
        self.parent = parent
        self.rowconfigure(0, weight=1)
        self.columnconfigure((0, 1, 2, 3), weight=1)

        plot_type_label = ttk.Label(self, text="Plot Type: ")
        plot_type_label.grid(row=0, column=0, sticky="e")

        self.plot_type = ttk.Combobox(self)
        self.plot_type["values"] = list(PlotSelector.plot_strategies.keys())
        self.plot_type["state"] = "readonly"
        self.plot_type.grid(row=0, column=1, sticky="w")
        self.plot_type.current(0)

        time_scale_label = ttk.Label(self, text="Time Scale: ")
        time_scale_label.grid(row=0, column=2, sticky="e")

        self.time_scale = ttk.Combobox(self)
        self.time_scale["values"] = list(PlotSelector.sampling_rules.keys())
        self.time_scale["state"] = "readonly"
        self.time_scale.grid(row=0, column=3, sticky="w")
        self.time_scale.current(0)

        self.create_bindings()

    def update_plot(self, event):
        """Update plot according to selected ComboBox items"""
        sampling_rule = PlotSelector.sampling_rules[self.time_scale.get()]
        plot_strategy = PlotSelector.plot_strategies[self.plot_type.get()]

        plot = Plot(self.parent.db, plot_strategy, sampling_rule)
        self.parent.plot_canvas.add_plot(plot)
        self.parent.plot_canvas.canvas.draw()

    def create_bindings(self) -> None:
        """Create key event bindings for drop downs"""
        self.time_scale.bind("<<ComboboxSelected>>", self.update_plot)
        self.plot_type.bind("<<ComboboxSelected>>", self.update_plot)


class PlotCanvas(ttk.Frame):
    """Frame for Plot"""

    default_strategy = ThreeDartAvg()

    def __init__(self, parent, *args, **kwargs) -> None:
        """Construct PlotCanvas and create default average plot"""
        super().__init__(parent, *args, **kwargs)
        self.parent = parent
        self.canvas = self._create_canvas()
        self.plot = Plot(self.parent.db, PlotCanvas.default_strategy, "M")
        if self.plot.fig:
            self.add_plot(self.plot)
        
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
        plot.fig.set_size_inches(fig_size)
        self.canvas.figure = plot.fig
        self.plot = plot


class Plot():
    """Container for plot"""
    def __init__(self, db: DataBase, strategy: PlotStrategy, sampling_rule: str) -> None:
        """Create Plot according to the set Strategy"""
        self.strategy = strategy
        self.fig = None
        self.fig, self.ax = self.strategy.build_plot(db, sampling_rule)
        self.fig_size = self.fig.get_size_inches()


if __name__ == "__main__":
    pass