import tkinter as tk
import tkinter.ttk as ttk
import os
import pandas as pd
import seaborn as sns
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure


FONT_TITLE = ("Arial", 20, "bold")
FONT_DEFAULT = ("Arial", 10)
CSV_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), 
    "db", 
    "darts_data.csv")


class StatPage(ttk.Frame):
    def __init__(self, parent, *args, **kwargs) -> None:
        super().__init__(parent, *args, **kwargs)
        self.rowconfigure((0, 1, 2), weight=1)
        self.columnconfigure(0, weight=1)
        # tk.Label(self, text="STATISTICS", background="lightsteelblue").grid(
        #     row=0, column=0, sticky="news")
        self.create_gui()
        
    
    def create_gui(self) -> None:
        self.page_title = PageTitle(self)
        self.page_title.grid(row=0, column=0)
        
        self.plot_selector = PlotSelector(self)
        self.plot_selector.grid(row=1, column=0)

        self.plot = Plot(self)
        self.plot.grid(row=2, column=0)

        

class PageTitle(ttk.Frame):
    def __init__(self, parent, *args, **kwargs) -> None:
        super().__init__(parent, *args, **kwargs)
        label = ttk.Label(self, text="Darts Practice Statistics",
                          font=FONT_TITLE)
        label.pack(expand=True, fill="both")


class PlotSelector(ttk.Frame):
    def __init__(self, parent, *args, **kwargs) -> None:
        super().__init__(parent, *args, **kwargs)
        self.rowconfigure(0, weight=1)
        self.columnconfigure((0, 1), weight=1)

        plot_type = ttk.Combobox(self)
        plot_type["values"] = ["Averages", "Nr of Sessions"]
        plot_type["state"] = "readonly"
        plot_type.grid(row=0, column=0, sticky="n")
        
        time_scale = ttk.Combobox(self)
        time_scale["values"] = ["Monthly", "Yearly"]
        time_scale["state"] = "readonly"
        time_scale.grid(row=0, column=1, sticky="n")


class Plot(ttk.Frame):
    
    def __init__(self, parent, *args, **kwargs) -> None:
        super().__init__(parent, *args, **kwargs)
        self.fig = self.create_plot()
        canvas = FigureCanvasTkAgg(self.fig, master=self)
        canvas.draw()
        canvas.get_tk_widget().grid(row=0, column=0)



    def create_plot(self) -> Figure:
        # Read in data
        if os.path.exists(CSV_PATH):
            df = pd.read_csv(CSV_PATH, index_col="date", parse_dates=True)
            df.drop(["Unnamed: 0"], axis=1, inplace=True)
        else:
            print("Database (darts_data.csv) not found...")

        df_monthly_tr = df[["round_nr"]].resample("D").max().resample("M").sum()
        df_val_res = df[["value"]].resample("M")
        df_monthly_av = df_val_res.sum() / df_val_res.count() * 3

        # Setting up plot layout
        fig, axs = plt.subplots(2, 1, figsize=(6,5))
        fig.suptitle("Monthly statistics", fontsize=20, fontweight="normal", y=1.0)
        sns.set_theme(style="whitegrid")
        fig.tight_layout(h_pad=5)

        # Creating plots
        axs[0].bar(df_monthly_tr.index, df_monthly_tr.round_nr, width=15, color="tab:blue",  edgecolor='black')
        sns.lineplot(x=df_monthly_av.index, y=df_monthly_av.value, color="tab:blue", marker='o', ax=axs[1])

        # Formatting
        years, months  = mdates.YearLocator(), mdates.MonthLocator()   # every year
        years_format, months_format = mdates.DateFormatter('%Y'), mdates.DateFormatter('%m')

        axs[0].set(title="Nr of rounds per month", xlabel="Date", ylabel="Nr of rounds")
        axs[1].set(title="Monthly Average", xlabel="Date", ylabel="3-Dart Average")

        for ax in axs:
            ax.set_axisbelow(True)
            ax.xaxis.grid(color='gray', linestyle='dashed')
            ax.yaxis.grid(color='gray', linestyle='dashed')
            ax.xaxis.set_major_locator(years)
            ax.xaxis.set_major_formatter(years_format)
            ax.xaxis.set_minor_locator(months)
            ax.xaxis.set_minor_formatter(months_format)
            for label in ax.get_xticklabels():
                label.set_rotation(90)
        return fig
    
        
if __name__ == "__main__":
    pass