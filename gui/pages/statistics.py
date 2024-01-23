from __future__ import annotations
import tkinter as tk
import tkinter.ttk as ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from ..constants import *
from .plot_strategies import *


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


class PlotSelector(ttk.Frame):
    """Container for drop down menus, with which the plot can be changed"""

    plot_strategies = {
        "Averages": ThreeDartAvg(),
        "Nr of Sessions": NrOfSessions(),
        "Nr of darts thrown": NrOfDarts(),
        "Nr of 180s": NrOf180s(),
        "Trebleless ratio": PercentageOfTreblelessVisits(),
    }

    sampling_rules = {
        "Monthly": "MS",
        "Yearly": "YS",
        "Daily": "D",
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
        self.plot = Plot(self.parent.db, PlotCanvas.default_strategy, "MS")
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