import tkinter as tk
import tkinter.ttk as ttk
from ..constants import *


class CustomPopup(tk.Toplevel):
    """Popup message to confirm to quit.
    Used instead of tk messaagebox, because that always centered on screen
    instead of application, even though parent kwarg was set"""
    def __init__(self, title, message, callback_fct, **kwargs) -> None:
        super().__init__(**kwargs)
        """Construct the QuitPopup widget and make it a modal window.
        Main window remains inactive until this one closed."""
        self.message = message
        self.title(title)
        self.callback_fct = callback_fct
        self.resizable(False, False)
        self._set_geometry()
        self._construct_widgets()
        # Hide minimize and maximize icons
        self.transient(self.master)
        # Make the popup a modal window
        self.grab_set()
        self.master.wait_window(self)

    def _set_geometry(self) -> None:
        """Determine widget target position and setup geometry"""
        width = 320
        height = 120
        pos_x = self.master.winfo_x() + GEOMETRY_W // 2 - width // 2
        pos_y = self.master.winfo_y() + GEOMETRY_H // 2 - height // 2
        # Place it in the center of the main window
        self.geometry(f"{width}x{height}+{pos_x}+{pos_y}")

    def _construct_widgets(self) -> None:
        """Construct the elements of the QuitPopup"""
        self.rowconfigure((0, 1, 2), weight=1)
        self.columnconfigure((0, 1), weight=1)
        icon = tk.Label(self, image="::tk::icons::question", background="white")
        icon.grid(row=0, column=0, rowspan=2, sticky="news")
        label = tk.Label(self, text=self.message, background="white", font=("Arial", 9))
        label.grid(row=0, column=1, rowspan=2, columnspan=2, sticky="news")
        ok = ttk.Button(self, text="OK", command=self._callback)
        ok.grid(row=2, column=1, sticky="e")
        cancel = ttk.Button(self, text="Cancel", command=self.destroy)
        cancel.grid(row=2, column=2, padx=(10, 10), sticky="e") 
        ok.focus()

    def _callback(self) -> None:
        """Callback funtcion for the yes button."""
        # Need to be destroyed first (quit is paused until destroy)
        self.destroy()
        self.callback_fct()


if __name__ == "__main__":
    pass