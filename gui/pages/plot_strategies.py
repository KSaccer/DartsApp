from __future__ import annotations
import os
from typing import TYPE_CHECKING, Tuple
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import pandas as pd
import seaborn as sns
from abc import ABC, abstractmethod
from matplotlib.figure import Figure, Axes

if TYPE_CHECKING:
    from db.database import DataBase


class PlotStrategy(ABC):
    """Strategy Interface for plot builder algorithms"""

    COLOR_POINT = "#2A6FBB"
    COLOR_RAW_LINE = "#B0B8C5"
    COLOR_TREND = "#F28E2B"
    COLOR_BAR = "#5A9E6F"
    COLOR_BAR_EDGE = "#356D4A"

    def build_plot(self, db: DataBase, sampling_rule: str) -> Tuple[Figure, Axes]:
        """Execute plot builder process"""
        df = self._create_df(db, self.sql_script, sampling_rule)
        sns.set_theme(style="whitegrid", context="notebook")
        plt.close('all')
        fig, ax = self._create_plot_content(df)
        fig, ax = self._format_plot_content(fig, ax, sampling_rule)
        fig.tight_layout()
        return (fig, ax)

    @abstractmethod
    def _create_df(self, db: DataBase, sql_script: str, sampling_rule: str) -> None:
        pass

    @abstractmethod
    def _create_plot_content(self, df: pd.DataFrame) -> Tuple[Figure, Axes]:
        pass

    def _format_plot_content(self, fig, ax, sampling_rule) -> Tuple[Figure, Axes]:
        """Format plot axes and appearance"""
        if sampling_rule == "MS":
            ax.xaxis.set_major_locator(mdates.MonthLocator(bymonth=(1, 4, 7, 10)))
        if sampling_rule == "YS":
            ax.xaxis.set_major_locator(mdates.YearLocator())
        if sampling_rule == "D":
            ax.xaxis.set_major_locator(mdates.AutoDateLocator(minticks=5, maxticks=8))

        fig.patch.set_facecolor("white")
        ax.set_facecolor("white")
        ax.set_axisbelow(True)
        ax.yaxis.grid(color="#DCE1E8", linestyle="-", linewidth=0.8)
        ax.xaxis.grid(False)
        ax.xaxis.set_major_formatter(mdates.ConciseDateFormatter(ax.xaxis.get_major_locator()))
        ax.tick_params(axis="x", labelrotation=0, labelsize=9, pad=4)
        ax.tick_params(axis="y", labelsize=9)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["left"].set_color("#CAD2DE")
        ax.spines["bottom"].set_color("#CAD2DE")
        ax.set(ylabel=None, xlabel=None)
        return (fig, ax)

    @staticmethod
    def _smooth_daily_series(series: pd.Series) -> pd.Series:
        """Create a daily, smooth curve without spline overshoot artifacts."""
        s = series.replace([float("inf"), -float("inf")], pd.NA).dropna()
        if s.empty:
            return s

        s = s[~s.index.duplicated(keep="first")].sort_index()
        s_daily = s.resample("D").asfreq()

        try:
            return s_daily.interpolate(method="pchip")
        except (ValueError, ImportError):
            try:
                return s_daily.interpolate(method="time")
            except ValueError:
                return s

    @staticmethod
    def _label_nonzero_bars(ax: Axes, values: pd.Series) -> None:
        """Label bars sparsely to reduce visual clutter."""
        if not ax.containers:
            return

        n = len(values)
        step = 1 if n <= 14 else 2 if n <= 28 else 3
        labels = []
        for i, value in enumerate(values.fillna(0)):
            if value <= 0 or i % step != 0:
                labels.append("")
            else:
                labels.append(f"{int(round(value))}")
        ax.bar_label(ax.containers[0], labels=labels, fontsize=9, padding=2, color="#28313C")

    @staticmethod
    def _set_range_subtitle(ax: Axes, df: pd.DataFrame) -> None:
        """Set compact subtitle with covered date range."""
        if df.empty:
            return
        start = df.index.min().strftime("%Y-%m-%d")
        end = df.index.max().strftime("%Y-%m-%d")
        ax.set_title(f"{start} to {end}", fontsize=9, color="#6D7785", pad=6)


class ThreeDartAvg(PlotStrategy):
    """Strategy for three dart average plot"""

    sql_script = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
        "sql", 
        "avg.sql")
      
    def _create_df(self, db: DataBase, sql_script: str, sampling_rule: str) -> pd.DataFrame:
        """Create the DataFrame by running the SQL script via DataBase."""
        df = db.query_to_dataframe(
            sql_script,
            parse_dates={"date": {"format": "%Y-%m-%d"}},
        )
        df = df.set_index("date")
        df = df.resample(sampling_rule).sum()
        return df
    
    def _create_plot_content(self, df: pd.DataFrame) -> Tuple[Figure, Axes]:
        """Set up plot and create curves"""
        # Figure setup
        fig, ax = plt.subplots(1, 1)
        fig.tight_layout(h_pad=5)
        # Creating plot
        avg = df.overall_score.div(df.visits.where(df.visits != 0))
        sns.scatterplot(x=df.index, y=avg,
                        color=self.COLOR_POINT, marker='o', s=28, edgecolor="white", linewidth=0.5, ax=ax)
        sns.lineplot(x=df.index, y=avg,
                        color=self.COLOR_RAW_LINE, linewidth=1.4, alpha=0.9, label="Observed", ax=ax)
        if ax.lines:
            ax.lines[0].set_linestyle("--")
        avg_smooth = self._smooth_daily_series(avg)
        sns.lineplot(x=avg_smooth.index, y=avg_smooth,
                     color=self.COLOR_TREND, linewidth=2.4, label="Trend", ax=ax)
        ax.legend(loc="upper left", frameon=False, fontsize=9)
        self._set_range_subtitle(ax, df)
        return (fig, ax)
    

class NrOfSessions(PlotStrategy):
    """Strategy for bar chart showing the nr of session played"""

    sql_script = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
        "sql", 
        "nr_of_games.sql")
      
    def _create_df(self, db: DataBase, sql_script: str, sampling_rule: str) -> pd.DataFrame:
        """Create the DataFrame by running the SQL script via DataBase."""
        df = db.query_to_dataframe(
            sql_script,
            parse_dates={"date": {"format": "%Y-%m-%d"}},
        )
        df = df.set_index("date")
        df = df.resample(sampling_rule).sum()
        return df

    def _create_plot_content(self, df: pd.DataFrame) -> Tuple[Figure, Axes]:
        """Set up plot and create curves"""
        # Figure setup
        fig, ax = plt.subplots(1, 1)
        fig.tight_layout(h_pad=5)
        # Creating plot
        df_plot = df.reset_index()
        sns.barplot(df_plot, x="date", y="nr_of_games", ax=ax,
                    native_scale=True, color=self.COLOR_BAR, edgecolor=self.COLOR_BAR_EDGE, alpha=0.45)
        ax.yaxis.set_major_locator(mticker.MaxNLocator(integer=True))
        self._label_nonzero_bars(ax, df_plot["nr_of_games"])
        self._set_range_subtitle(ax, df)
        return (fig, ax)
    

class NrOfDarts(PlotStrategy):
    """Strategy for bar chart showing the nr of darts thrown"""

    sql_script = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
        "sql", 
        "nr_of_darts.sql")

    def _create_df(self, db: DataBase, sql_script: str, sampling_rule: str) -> pd.DataFrame:
        """Create the DataFrame by running the SQL script via DataBase."""
        df = db.query_to_dataframe(
            sql_script,
            parse_dates={"date": {"format": "%Y-%m-%d"}},
        )
        df = df.set_index("date")
        df = df.resample(sampling_rule).sum()
        return df

    def _create_plot_content(self, df: pd.DataFrame) -> Tuple[Figure, Axes]:
        """Set up plot and create curves"""
        # Figure setup
        fig, ax = plt.subplots(1, 1)
        fig.tight_layout(h_pad=5)
        # Creating plot
        df_plot = df.reset_index()
        sns.barplot(df_plot, x="date", y="darts_thrown", ax=ax,
                    native_scale=True, color=self.COLOR_BAR, edgecolor=self.COLOR_BAR_EDGE, alpha=0.45)
        ax.yaxis.set_major_locator(mticker.MaxNLocator(integer=True))
        self._label_nonzero_bars(ax, df_plot["darts_thrown"])
        self._set_range_subtitle(ax, df)
        return (fig, ax)


class NrOf180s(PlotStrategy):
    """Strategy for bar chart showing the nr of 180s/171s thrown"""

    sql_script = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
        "sql", 
        "nr_of_180s.sql")

    def _create_df(self, db: DataBase, sql_script: str, sampling_rule: str) -> pd.DataFrame:
        """Create the DataFrame by running the SQL script via DataBase."""
        df = db.query_to_dataframe(
            sql_script,
            parse_dates={"date": {"format": "%Y-%m-%d"}},
        )
        df = df.set_index("date")
        df = df.resample(sampling_rule).sum()
        return df

    def _create_plot_content(self, df: pd.DataFrame) -> Tuple[Figure, Axes]:
        """Set up plot and create curves"""
        # Figure setup
        fig, ax = plt.subplots(1, 1)
        fig.tight_layout(h_pad=5)
        # Creating plot
        df_plot = df.reset_index()
        sns.barplot(df_plot, x="date", y="visits_180", ax=ax,
                    native_scale=True, color=self.COLOR_BAR, edgecolor=self.COLOR_BAR_EDGE, alpha=0.45)
        ax.yaxis.set_major_locator(mticker.MaxNLocator(integer=True))
        self._label_nonzero_bars(ax, df_plot["visits_180"])
        self._set_range_subtitle(ax, df)
        return (fig, ax)


class PercentageOfTreblelessVisits(PlotStrategy):
    """Strategy for plot showing the percentage of visits without trebles"""

    sql_script = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
        "sql", 
        "nr_of_trebleless_visits.sql")

    def _create_df(self, db: DataBase, sql_script: str, sampling_rule: str) -> pd.DataFrame:
        """Create the DataFrame by running the SQL script via DataBase."""
        df = db.query_to_dataframe(
            sql_script,
            parse_dates={"date": {"format": "%Y-%m-%d"}},
        )
        df = df.set_index("date")
        df = df.resample(sampling_rule).sum()
        return df

    def _create_plot_content(self, df: pd.DataFrame) -> Tuple[Figure, Axes]:
        """Set up plot and create curves"""
        # Figure setup
        fig, ax = plt.subplots(1, 1)
        fig.tight_layout(h_pad=5)
        # Creating plot
        no_treble_pct = df.trebleless.mul(100).div(df.visits.where(df.visits != 0))
        sns.scatterplot(x=df.index, y=no_treble_pct,
                        color=self.COLOR_POINT, marker='o', s=28, edgecolor="white", linewidth=0.5, ax=ax)
        sns.lineplot(x=df.index, y=no_treble_pct,
                        color=self.COLOR_RAW_LINE, linewidth=1.4, alpha=0.9, label="Observed", ax=ax)
        if ax.lines:
            ax.lines[0].set_linestyle("--")
        no_treble_smooth = self._smooth_daily_series(no_treble_pct)
        sns.lineplot(x=no_treble_smooth.index, y=no_treble_smooth,
                     color=self.COLOR_TREND, linewidth=2.4, label="Trend", ax=ax)
        ax.legend(loc="upper left", frameon=False, fontsize=9)
        self._set_range_subtitle(ax, df)
        return (fig, ax)


class AveragesAndSessions(PlotStrategy):
    """Strategy for combined plot of averages and nr of sessions"""

    sql_avg_script = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
        "sql", 
        "avg.sql")
    
    sql_sessions_script = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
        "sql", 
        "nr_of_games.sql")

    def build_plot(self, db: "DataBase", sampling_rule: str) -> "Tuple[Figure, Axes]":
        """Execute plot builder process"""
        df = self._create_df(db, "", sampling_rule)  # sql_script is not used
        sns.set_theme(style="whitegrid", context="notebook")
        plt.close('all')
        fig, (ax_top, ax_bottom) = self._create_plot_content(df)
        fig, ax_top = self._format_plot_content(fig, ax_top, sampling_rule)
        fig, ax_bottom = self._format_plot_content(fig, ax_bottom, sampling_rule)
        ax_top.tick_params(axis="x", labelbottom=False)
        return (fig, ax_top)

    def _create_df(self, db: "DataBase", sql_script: str, sampling_rule: str) -> pd.DataFrame:
        """Create the DataFrame by running SQL scripts via DataBase."""
        df_avg = db.query_to_dataframe(
            self.sql_avg_script,
            parse_dates={"date": {"format": "%Y-%m-%d"}},
        )
        df_avg = df_avg.set_index("date")

        df_sessions = db.query_to_dataframe(
            self.sql_sessions_script,
            parse_dates={"date": {"format": "%Y-%m-%d"}},
        )
        df_sessions = df_sessions.set_index("date")

        df = pd.merge(df_avg, df_sessions, on="date", how="outer").fillna(0)
        df = df.resample(sampling_rule).sum()
        
        return df
    
    def _create_plot_content(self, df: pd.DataFrame) -> "Tuple[Figure, Tuple[Axes, Axes]]":
        """Set up plot and create curves"""
        # Figure setup
        fig, (ax_top, ax_bottom) = plt.subplots(
            2, 1, sharex=True, gridspec_kw={"height_ratios": [2, 1], "hspace": 0.04}
        )
        fig.subplots_adjust(left=0.07, right=0.985, top=0.95, bottom=0.10, hspace=0.06)
        # Creating plot
        avg = df.overall_score.div(df.visits.where(df.visits != 0))
        sns.scatterplot(x=df.index, y=avg,
                        color=self.COLOR_POINT, marker='o', s=28, edgecolor="white", linewidth=0.5, ax=ax_top)
        sns.lineplot(x=df.index, y=avg,
                        color=self.COLOR_RAW_LINE, linewidth=1.4, alpha=0.9, label="Observed", ax=ax_top)
        if ax_top.lines:
            ax_top.lines[0].set_linestyle("--")
        avg_smooth = self._smooth_daily_series(avg)
        sns.lineplot(x=avg_smooth.index, y=avg_smooth,
                     color=self.COLOR_TREND, linewidth=2.4, label="Trend", ax=ax_top)
        ax_top.set_ylabel("Three Dart Average")
        ax_top.legend(loc="upper left", frameon=False, fontsize=9)

        df_plot = df.reset_index()
        sns.barplot(data=df_plot, x="date", y="nr_of_games", ax=ax_bottom,
                    native_scale=True, color=self.COLOR_BAR, edgecolor=self.COLOR_BAR_EDGE, alpha=0.45)
        ax_bottom.yaxis.set_major_locator(mticker.MaxNLocator(integer=True))
        self._label_nonzero_bars(ax_bottom, df_plot["nr_of_games"])
        ax_bottom.set_ylabel("Number of Sessions")
        ax_top.margins(x=0.01)
        ax_bottom.margins(x=0.01)
        self._set_range_subtitle(ax_top, df)
        return (fig, (ax_top, ax_bottom))


if __name__ == "__main__":
    pass
