import tkinter as tk
import tkinter.ttk as ttk


class Settings(ttk.Frame):
    def __init__(self, parent, *args, **kwargs) -> None:
        super().__init__(parent, *args, **kwargs)
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        tk.Label(self, text="SETTINGS", background="lightsteelblue").grid(
            row=0, column=0, sticky="news")
        
    def create_gui(self):
        pass
    
        
if __name__ == "__main__":
    pass