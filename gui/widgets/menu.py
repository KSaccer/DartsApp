import tkinter as tk
import tkinter.ttk as ttk
from ..constants import *


class Menu(ttk.Frame):
    """Class for sied menu"""

    def __init__(self, parent, items: dict, *args, **kwargs) -> None:
        """Construct Menu widget, create bindings"""
        super().__init__(parent, *args, **kwargs)
        self.columnconfigure(0, weight=1)
        self.parent = parent
        self.items = items
        self.menu_structure = self._build_menu()
        for menu_item, reference in self.menu_structure.items():
            self._create_bindings(menu_item, reference)

    def _build_menu(self) -> dict:
        """Construct main- and submenu widgets. Return a dictionary,
        where the key is a menu item, the value is either a page, or
        a list of submenu items"""
        structure = {}
        spacer = tk.Label(self, text="", background=COLOR_BG_MENU, padx=20, pady=10)
        spacer.grid(row=0, column=0)
        row = 1
        for item in self.items:
            # Submenu
            if isinstance(self.items[item], dict):
                submenu_items = self.items[item]
                main_menu_label = tk.Label(self, text=item, font=FONT_MENU,
                                background=COLOR_BG_MENU, foreground=COLOR_FONT_MENU,
                                anchor="nw", padx=20, pady=10)
                main_menu_label.grid(row=row, column=0, sticky="ew")
                row += 1
                submenus = []
                for submenu_item in submenu_items:
                    submenu_label = tk.Label(self, text="  "+submenu_item, 
                                             font=FONT_MENU, 
                                             background=COLOR_BG_MENU, 
                                             foreground=COLOR_FONT_MENU, 
                                             anchor="nw", 
                                             padx=20, pady=10)
                    submenu_label.grid(row=row, column=0, sticky="ew")
                    submenu_label.grid_remove()
                    row += 1
                    submenus.append(submenu_label)
                    structure[submenu_label] = submenu_items[submenu_item]
                structure[main_menu_label] = submenus
            # Main menu
            else:
                main_menu_label = tk.Label(self, text=item, font=FONT_MENU,
                                background=COLOR_BG_MENU, foreground=COLOR_FONT_MENU,
                                anchor="nw", padx=20, pady=10)
                main_menu_label.grid(row=row, column=0, sticky="ew")
                structure[main_menu_label] = self.items[item]
                row += 1
        return structure

    def _color_config(self, widget, color: str) -> None:
        """Change widget color"""
        widget.configure(background=color)

    def _create_bindings(self, widget, reference: dict) -> None:
        """Assign callback functions for specific events of widget"""
        widget.bind("<Enter>", lambda event=None:
                    self._color_config(widget, COLOR_BG_MENU_HOVER))
        widget.bind("<Leave>", lambda event=None:
                    self._color_config(widget, COLOR_BG_MENU))
        widget.bind("<Button-1>", lambda event=None:
                    self._menu_clicked(reference))

    def _menu_clicked(self, reference: tk.Widget) -> None:
        """Assign the corresponding callback function to the widget.
        The widget is a main menu element: call go_to_page
        The widget is a submenu element: call submenu_switch"""
        if isinstance(reference, list):
            self._submenu_switch(reference)
        else:
            self._go_to_page(reference)

    def _go_to_page(self, page: ttk.Frame) -> None:
        """Show the main frame of the given page.
        If page is None (Quit button), call the close_app function"""
        if page:
            page.create_gui()
            page.tkraise()
        else:
            self.parent.close_app()

    def _submenu_switch(self, submenus: list) -> None:
        """Show/Hide Submenu elements"""
        for submenu in submenus:
            if submenu.grid_info():
                submenu.grid_remove()
            else:
                submenu.grid()


if __name__ == "__main__":
    pass