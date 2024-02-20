from __future__ import annotations
import os
import datetime
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd
import sqlite3
import seaborn as sns
from abc import ABC, abstractmethod
from matplotlib.figure import Figure, Axes


class PlotStrategy(ABC):
    """Strategy Interface for plot builder algorithms"""

    def build_plot(self, db: DataBase, sampling_rule: str) -> (Figure, Axes):
        """Execute plot builder process"""
        df = self._create_df(db, self.sql_script, sampling_rule)
        plt.close('all')
        fig, ax = self._create_plot_content(df)
        fig, ax = self._format_plot_content(fig, ax, sampling_rule)
        fig.tight_layout()
        return (fig, ax)

    @abstractmethod
    def _create_df(self, db: DataBase, sql_script: str) -> None:
        pass

    @abstractmethod
    def _create_plot_content(self, df: pd.DataFrame) -> (Figure, Axes):
        pass

    def _format_plot_content(self, fig, ax, sampling_rule) -> (Figure, Axes):
        """Format plot axes and appearance"""
        if sampling_rule == "YS":
            ax.xaxis.set_major_locator(mdates.YearLocator())
        ax.set_axisbelow(True)
        ax.yaxis.grid(color='lightgray', linestyle='dashed')
        ax.xaxis.set_major_formatter(mdates.ConciseDateFormatter(ax.xaxis.get_major_locator()))
        for label in ax.get_xticklabels():
            label.set_rotation(90)
        ax.set(ylabel=None, xlabel=None)
        return (fig, ax)


class ThreeDartAvg(PlotStrategy):
    """Strategy for three dart average plot"""

    sql_script = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
        "sql", 
        "avg.sql")
      
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
    

class NrOfSessions(PlotStrategy):
    """Strategy for bar chart showing the nr of session played"""

    sql_script = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
        "sql", 
        "nr_of_games.sql")
      
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
        sns.barplot(df, x="date", y="nr_of_games", ax=ax, 
                    native_scale=True, color="tab:blue", edgecolor="darkblue")
        ax.bar_label(ax.containers[0], fontsize=10)
        return (fig, ax)
    

class NrOfDarts(PlotStrategy):
    """Strategy for bar chart showing the nr of darts thrown"""

    sql_script = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
        "sql", 
        "nr_of_darts.sql")

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
        sns.barplot(df, x="date", y="darts_thrown", ax=ax,
                    native_scale=True, color="tab:blue", edgecolor="darkblue")
        ax.bar_label(ax.containers[0], fontsize=10)
        return (fig, ax)


class NrOf180s(PlotStrategy):
    """Strategy for bar chart showing the nr of 180s thrown"""

    sql_script = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
        "sql", 
        "nr_of_180s.sql")

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
        sns.barplot(df, x="date", y="visits_180", ax=ax,
                    native_scale=True, color="tab:blue", edgecolor="darkblue")
        ax.bar_label(ax.containers[0], fontsize=10)
        return (fig, ax)


class PercentageOfTreblelessVisits(PlotStrategy):
    """Strategy for plot showing the percentage of visits without trebles"""

    sql_script = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
        "sql", 
        "nr_of_trebleless_visits.sql")

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
        sns.scatterplot(x=df.index, y=df.trebleless / df.visits * 100, 
                        color="tab:blue", marker='o', ax=ax)
        sns.lineplot(x=df.index, y=df.trebleless / df.visits * 100, 
                        color="lightgray", ax=ax)
        ax.lines[0].set_linestyle("--")
        try:
            df_smooth = df.resample("D").interpolate(method="quadratic")
        except ValueError:
            df_smooth = df
        sns.lineplot(x=df_smooth.index, 
                        y=df_smooth.trebleless / df_smooth.visits * 100, 
                        color="tab:orange", ax=ax
                        )
        return (fig, ax)


if __name__ == "__main__":
    pass