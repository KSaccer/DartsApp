from __future__ import annotations
import os
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd
import sqlite3
import seaborn as sns
from abc import ABC, abstractmethod
from matplotlib.figure import Figure, Axes


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
        fig, ax = self._format_plot_content(fig, ax, sampling_rule)
        fig.tight_layout()
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
        plot= sns.lineplot(x=df.index, y=df.overall_score / df.visits, 
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

    def _format_plot_content(self, fig, ax, sampling_rule) -> (Figure, Axes):
        """Format plot axes and appearance"""
        if sampling_rule == "YS":
            ax.xaxis.set_major_locator(mdates.YearLocator())
        ax.set_axisbelow(True)
        ax.xaxis.grid(color='lightgray', linestyle='dashed')
        ax.yaxis.grid(color='lightgray', linestyle='dashed')
        ax.xaxis.set_major_formatter(mdates.ConciseDateFormatter(ax.xaxis.get_major_locator()))
        for label in ax.get_xticklabels():
            label.set_rotation(90)
        ax.set(ylabel=None, xlabel=None)
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
        fig.tight_layout()
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
        ax.set(ylabel=None, xlabel=None)
        return (fig, ax)
    

class NrOfDarts(PlotStrategy):
    """Strategy for bar chart showing the nr of darts thrown"""

    sql_script = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
        "sql", 
        "nr_of_darts.sql")

    def build_plot(self, db: DataBase, sampling_rule: str) -> (Figure, Axes):
        """Execute plot builder process"""
        # Create DataFrame
        df = self._create_df(db, NrOfDarts.sql_script, sampling_rule)
        fig, ax = self._create_plot_content(df)
        fig, ax = self._format_plot_content(fig, ax)
        fig.tight_layout()
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
        ax.bar(df.index, df.darts_thrown, width=15, 
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
        ax.set(ylabel=None, xlabel=None)
        return (fig, ax)
    

class NrOf180s(PlotStrategy):
    """Strategy for bar chart showing the nr of 180s thrown"""

    sql_script = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
        "sql", 
        "nr_of_180s.sql")

    def build_plot(self, db: DataBase, sampling_rule: str) -> (Figure, Axes):
        """Execute plot builder process"""
        # Create DataFrame
        df = self._create_df(db, NrOf180s.sql_script, sampling_rule)
        fig, ax = self._create_plot_content(df)
        fig, ax = self._format_plot_content(fig, ax)
        fig.tight_layout()
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
        ax.bar(df.index, df.visits_180, width=15, 
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
        ax.set(ylabel=None, xlabel=None)
        return (fig, ax)
    

class PercentageOfTreblelessVisits(PlotStrategy):
    """Strategy for bar chart showing the nr of 180s thrown"""

    sql_script = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
        "sql", 
        "nr_of_trebleless_visits.sql")

    def build_plot(self, db: DataBase, sampling_rule: str) -> (Figure, Axes):
        """Execute plot builder process"""
        # Create DataFrame
        df = self._create_df(db, PercentageOfTreblelessVisits.sql_script, sampling_rule)
        fig, ax = self._create_plot_content(df)
        fig, ax = self._format_plot_content(fig, ax)
        fig.tight_layout()
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
        sns.scatterplot(x=df.index, y=df.visits / df.trebleless, 
                        color="tab:blue", marker='o', ax=ax)
        sns.lineplot(x=df.index, y=df.visits / df.trebleless, 
                        color="lightgray", ax=ax)
        ax.lines[0].set_linestyle("--")
        try:
            df_smooth = df.resample("D").interpolate(method="quadratic")
        except ValueError:
            df_smooth = df
        sns.lineplot(x=df_smooth.index, 
                        y=df_smooth.visits / df_smooth.trebleless, 
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
        ax.set(ylabel=None, xlabel=None)
        return (fig, ax)
    

if __name__ == "__main__":
    pass