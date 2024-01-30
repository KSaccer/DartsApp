import tkinter as tk
import tkinter.ttk as ttk
import re
from tkinter import messagebox
from datetime import datetime
from typing import Generator
from ..constants import *
from ..widgets.custom_popup import CustomPopup


class Game():
    """Class to contain game data"""
    def __init__(self, game_id: int, game_type: str = "Scoring") -> None:
        """Construct Game class"""
        self.game_id = game_id
        self.game_type = game_type
        self.game_started = False
        self.start = None
        self.end = None

    def initialize_game(self):
        self.start = datetime.now()
        self.game_started = True


class Scoring(ttk.Frame):
    """Main class of Scoring page"""
    def __init__(self, parent, db, *args, **kwargs) -> None:
        """Construct Scoring page"""
        # main config
        super().__init__(parent, *args, **kwargs)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=5)
        self.rowconfigure(2, weight=3)
        self.rowconfigure(3, weight=1)
        self.columnconfigure((0, 1), weight=1)
        self._created = False

        # Initialize database
        self.db = db
        # Initialize Game
        self.game = Game(self.db.last_game_id + 1)
        # populating widgets
        self.create_gui()

    def create_gui(self) -> None:
        """Construct widgets of Scoring page"""
        if self._created:
            return
        self.page_title = PageTitle(self)
        self.page_title.grid(row=0, column=0, columnspan=2)

        self.score_entry_block = ScoreEntryBlock(self, text="Enter Score")
        self.score_entry_block.grid(row=1, column=0, padx=10, pady=10,
                                    sticky="news")

        self.statistics = Statistics(self, text="Session Statistics")
        self.statistics.grid(row=2, column=0, padx=10, pady=10, sticky="news")

        self.buttons_frame = ButtonsFrame(self, relief="groove", border=2)
        self.buttons_frame.grid(row=3, column=0, padx=10, pady=10,
                                sticky="news")

        self.throw_history_table = ThrowHistoryTable(self, text="Throw History")
        self.throw_history_table.grid(row=1, column=1, padx=10, pady=10,
                                rowspan=3, sticky="news")
        
        self._created = True


class PageTitle(ttk.Frame):
    """Class for page title"""
    def __init__(self, parent, *args, **kwargs) -> None:
        """Construct page title label"""
        super().__init__(parent, *args, **kwargs)
        label = ttk.Label(self, text="Darts Scoring Practice Session",
                          font=FONT_TITLE)
        label.pack(expand=True, fill="both")


class ScoreEntryBlock(ttk.LabelFrame):
    """Class for score entry section"""
    def __init__(self, parent, *args, **kwargs) -> None:
        """Construct entry fields, labels and a button to submit data"""
        super().__init__(parent, *args, **kwargs)
        self.parent = parent
        self.rowconfigure((0, 1, 2, 3), weight=1)
        self.columnconfigure((0, 1), weight=1)
        self.throw_1 = ThrowEntry(self, "1st Throw:", 0)
        self.throw_2 = ThrowEntry(self, "2nd Throw:", 1)
        self.throw_3 = ThrowEntry(self, "3rd Throw:", 2)
        self.throw_entries = [self.throw_1, self.throw_2, self.throw_3]

        self.submit = ttk.Button(self, text="Submit",
                                 command=self.submit_button_clicked)
        self.submit.grid(row=3, column=0, columnspan=2, padx=10, pady=10,
                         sticky="news")
        self.create_bindings()
        
    def create_bindings(self) -> None:
        """Create key event bindings for the entry fields"""
        self.throw_1.value.bind("<Return>", lambda event=None:
                                self.throw_2.value.focus_set())
        self.throw_2.value.bind("<Return>", lambda event=None:
                                self.throw_3.value.focus_set())
        self.throw_3.value.bind("<Return>", self.submit_button_clicked)

    def clear_values(self) -> None:
        """Clear score entry fields"""
        self.throw_1.value.delete(0, tk.END)
        self.throw_2.value.delete(0, tk.END)
        self.throw_3.value.delete(0, tk.END)

    def get_values(self) -> list:
        """Get values from entry fields"""
        return [
            self.throw_1.value.get_and_convert(),
            self.throw_2.value.get_and_convert(),
            self.throw_3.value.get_and_convert()
            ]

    def submit_button_clicked(self, *ignore) -> None:
        """
        0. Initialize Game.start time, if it's none
        1. Get entried scores, populate table, clear entry fields
        2. Update Statistics fields
        3. Set focus to throw_1 entry field
        """
        # Release focus from last entry widget, when called by <Return>
        # This way the entry will be validated, otherwise not
        self.parent.focus()

        if not self.parent.game.game_started:
            self.parent.game.initialize_game()
        # Check if entries are all valid
        validities = [throw.value.validate(throw.value.get().strip()) 
                      for throw in self.throw_entries]
        if not all(validities):
            self.throw_entries[validities.index(False)].value.focus()
            return
        else:
            self.add_throws_into_throw_history_table()
            self.parent.statistics.update_statistics()
            self.clear_values()
            self.throw_1.value.focus_set()

    def add_throws_into_throw_history_table(self) -> None:
        """Get entried scores and populate throw history table"""
        throws = self.get_values()
        throws_sum = sum([throw[1] for throw in throws])
        # populate table with throw data
        record = tuple([throw[0].upper() for throw in throws] + [throws_sum])
        self.parent.throw_history_table.add_record(record)


class ThrowEntry():
    """Class with a Label and a ScoreEntry next to it"""
    def __init__(self, parent, label_text: str, row: int) -> None:
        """Construct Label and ScoreEntry on parent"""
        self.label = ttk.Label(parent, text=label_text)
        self.value = ScoreEntry(parent)
        self.label.grid(row=row, column=0, padx=10, pady=10)
        self.value.grid(row=row, column=1, padx=10, pady=10)


class ScoreEntry(ttk.Entry):
    """Entry field to enter thrown score with methods to 
    validate and convert the score"""

    # List of valid score entries:
    #    0 : no score
    #   25 : single bull
    #   50 : bullseye
    
    VE_SINGLES = "1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20".split()
    VE_DOUBLES = ["D" + single for single in VE_SINGLES]
    VE_TRIPLES = ["T" + single for single in VE_SINGLES]
    VE_SPECIAL = "0 25 50".split()
    VALID_ENTRIES = VE_SINGLES + VE_DOUBLES + VE_TRIPLES + VE_SPECIAL

    def __init__(self, parent: tk.Widget, *args, **kwargs) -> None:
        """Construct ScoreEntry widget on parent widget"""
        super().__init__(parent, *args, **kwargs)
        vcmd = (self.register(self.validate), "%P")
        ivcmd = (self.register(self.on_invalid), )
        self.config(validate="focus", 
                    validatecommand=vcmd, invalidcommand=ivcmd)

    def get_and_convert(self) -> tuple:
        """Get score string, convert it to int, return both as tuple,
        or an empty tuple, when entry field is empty.
        For example T20 -> ("T20", 60) or D5 -> ("D5", 10)"""
        score = super().get().strip().upper()
        if not self.validate(score):
            return ()
        
        if score[0] == "D":
            converted_score = int(score[1:]) * 2
        elif score[0] == "T":
            converted_score = int(score[1:]) * 3
        else:
            converted_score = int(score)
        return (score, 
                converted_score)
    
    def validate(self, value: str) -> bool:
        """Check if entered score is a valid darts score"""
        if value.upper() not in self.VALID_ENTRIES:
            return False
        self.config(foreground="black")
        return True
    
    def on_invalid(self) -> None:
        """Executed when entry validation returns False.
        Change text color to red"""
        if self.get():
            self.config(foreground="red")

class Statistics(ttk.LabelFrame):
    """Class for main statistics shown during a scoring session"""
    def __init__(self, parent, *args, **kwargs) -> None:
        super().__init__(parent, *args, **kwargs)
        self.rowconfigure((0, 1, 2, 3), weight=1)
        self.columnconfigure((0, 1), weight=1)
        self.avg = StatField(self, "Average:", "0.0", 0)
        self.darts_thrown = StatField(self, "Darts thrown:", "0", 1)
        self.score = StatField(self, "Score:", "0", 2)
        self.current_max = StatField(self, "Current maximum:", "0", 3)

    def get_statistics(self) -> dict:
        """Get statistic values and return them as a dictionary"""
        return {
            "avg": self.avg.value.cget("text"),
            "darts_thrown": self.darts_thrown.value.cget("text"),
            "score": self.score.value.cget("text"),
            "current_max": self.current_max.value.cget("text")
        }

    # keyword args without default values
    def set_statistics(self, *, avg: str, darts_thrown: str,
                       score: str, current_max: str) -> None:
        """Set values of statistics shown during a scoring session"""
        self.avg.value.config(text=avg)
        self.darts_thrown.value.config(text=darts_thrown)
        self.score.value.config(text=score)
        self.current_max.value.config(text=current_max)

    def calculate_statistics(self) -> dict:
        """Get throws from history table, calculate statistics then
        return them as a dictionary"""
        throws = list(self.master.throw_history_table.get_records())
        darts_thrown = len(throws) * 3
        current_max = 0
        score = 0
        for throw in throws:
            score += throw[-1]
            if throw[-1] > current_max:
                current_max = throw[-1]
            else:
                continue

        return {
            "avg": f'{score / darts_thrown * 3:.1f}',
            "darts_thrown": f'{darts_thrown}',
            "score": f'{score}',
            "current_max": f'{current_max}'
        }
        
    def update_statistics(self) -> None:
        """Reevaluate all statistics field values using the item from 
        the throw history table"""
        updated_stats = self.calculate_statistics()
        self.set_statistics(**updated_stats)

    def reset(self) -> None:
        """Reset statistics"""
        for _ in [self.avg, self.darts_thrown, self.score, self.current_max]:
            _.value.config(text=_.initial_value)


class StatField():
    """Class for a statistic value shown in Statistics"""
    def __init__(self, parent, label_text: str,
                 value_text: str, row: int) -> None:
        """Construnct StatField on parent"""
        self.initial_value = value_text
        self.label = ttk.Label(parent, text=label_text)
        self.value = ttk.Label(parent, text=value_text)
        self.label.grid(row=row, column=0, padx=10, pady=10, sticky="e")
        self.value.grid(row=row, column=1, padx=10, pady=10, sticky="w")


class ButtonsFrame(ttk.LabelFrame):
    """Frame that serves as a container for the Finish and Restart buttons"""

    def __init__(self, parent, *args, **kwargs) -> None:
        """Construct Frame that contains the Finish and Restart buttons"""
        super().__init__(parent, *args, **kwargs)
        self.parent = parent
        self.rowconfigure(0, weight=1)
        self.columnconfigure((0, 1), weight=1)
        finish_button = ttk.Button(self, text="Finish",
                                   command=self.finish)
        restart_button = ttk.Button(self, text="Restart",
                                    command=self.restart_clicked)
        finish_button.grid(row=0, column=0, padx=10, pady=10, sticky="news")
        restart_button.grid(row=0, column=1, padx=10, pady=10, sticky="news")

    def restart_clicked(self):
        CustomPopup("Confirmation", "Do you really want to restart the session?\n"
                        "Scores and statistics will be discarded!",
                        self.restart)

    def restart(self) -> None:
        """Reset session - clear statistics and table records"""
        self.parent.statistics.reset()
        self.parent.throw_history_table.clear_table()
        self.parent.game.start = None

    def finish(self) -> None:
        """Insert data into database and close application"""
        # Insert game
        if self.parent.game.start:
            self.parent.game.end = datetime.now()
            game_data = (
                self.parent.game.game_id,
                self.parent.game.start,
                self.parent.game.end,
                self.parent.game.game_type
                )
            self.parent.db.insert_game(game_data)

        # Insert throws
        for value in self.parent.throw_history_table.get_records():
            throw_data = tuple(value[1::])
            self.parent.db.insert_data(throw_data)
        
        # Start new game
        self.restart()
        self.parent.game.game_id += 1


class ThrowHistoryTable(ttk.LabelFrame):
    """Class to show thrown scores in a tabular format"""

    def __init__(self, parent, *args, **kwargs) -> None:
        """Construct TrowHistory table to store thrown scores"""
        super().__init__(parent, *args, **kwargs)
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.items = []
        self.throw_history_table = self._create_table()
        self._create_bindings()

    def _create_table(self) -> ttk.Treeview:
        """Create the table to store the thrown scores"""
        columns = {
            "id": "ID",
            "throw_1": "1st Throw",
            "throw_2": "2nd Throw",
            "throw_3": "3rd Throw",
            "throw_sum": "SUM",
        }
        table = ttk.Treeview(self, columns=list(columns.keys()))
        table.grid(row=0, column=0, padx=10, pady=10,
                                sticky="ns")
        self._configure_table_columns(table, columns)
        self._add_table_scrollbar(self, table)
        return table

    @staticmethod
    def _configure_table_columns(table: ttk.Treeview, columns: dict) -> None:
        """Set titles and width for table columns"""
        table["show"] = "headings"
        for column in columns:
            table.heading(column, text=columns[column])
            table.column(column, width=80, anchor=tk.CENTER)

    @staticmethod
    def _add_table_scrollbar(parent: tk.Widget, table: ttk.Treeview) -> None:
        """Create a scrollbar for the table"""
        scrollbar = ttk.Scrollbar(parent, orient=tk.VERTICAL,
                                  command=table.yview)
        table.configure(yscroll=scrollbar.set)
        scrollbar.grid(row=0, column=1, sticky='ns')

    def _create_bindings(self) -> None:
        """Bind callout functions to events"""
        self.throw_history_table.bind("<Double-1>", self._edit_cell)
        
    def _edit_cell(self, event, row=None, column=None) -> None:
        """Open a PopupEntry field above the TreeView cell that was 
        double-clicked on to edit the score. Header row, ID and SUM column
        will be ignored and therefore not editable."""
        
        # Destroy existing popup, if there's one
        try: 
            self.entry_popup.destroy()
        except AttributeError:
            pass
        
        if not row:
            row = self.throw_history_table.identify_row(event.y)
        if not column:
            column = self.throw_history_table.identify_column(event.x)
        column_id = int(column[1:]) - 1

        # Ignore header row and ID / SUM columns
        if not row or column in {"#1", "#5"}:
            return
        
        x, y, width, height = self.throw_history_table.bbox(row, column)
        pady = height // 2

        text = self.throw_history_table.item(row, "values")[column_id]
        self.entry_popup = EntryPopup(self.throw_history_table, row, column_id, text)
        self.entry_popup.place(x=x, y=y+pady, width=width, height=height, anchor="w")

    def add_record(self, record: tuple) -> None:
        """Add record to TreeView, update item list
          and move scroll to bottom"""
        if self.items:
            last_id = int(self.throw_history_table.item(self.items[-1])["values"][0])
        else:
            last_id = 0
        values = [last_id + 1] + [*record]
        self.throw_history_table.insert("", tk.END, values=values)
        self.items = self.throw_history_table.get_children()
        self.throw_history_table.yview_moveto(1)

    def clear_table(self) -> None:
        """Clear all entries from TreeView"""
        self.throw_history_table.delete(*self.items)
        self.items = []

    def get_records(self) -> Generator[str, None, None]:
        """Yield data from TreevView line by line"""
        for item in self.items:
            yield self.throw_history_table.item(item)["values"]


class EntryPopup(ScoreEntry):
    """Widget to be placed over a cell in ThrowHistory TreeView
    when it is selected via double click to be modified"""
    def __init__(self, parent, row: str, column_id: int, text: str, **kwargs) -> None:
        """Construct an EntryPopup widget"""
        super().__init__(parent, **kwargs)
        self.parent = parent
        self.row = row
        self.column_id = column_id
        
        self.insert(0, text) 
        self.original_score = self.get_and_convert()
        self['exportselection'] = False
        self.focus_force()
        self.selection_range(0, 'end')

        self.create_bindings()

    def create_bindings(self) -> None:
        """Bind callout functions to events"""
        self.bind("<Return>", self.on_return)
        self.bind("<Control-a>", lambda event: self.selection_range(0, 'end'))
        self.bind("<Escape>", lambda event: self.destroy())
        self.bind("<Tab>", lambda event: self.tab_pressed())
        self.bind("<FocusOut>", lambda event: self.destroy())

    def on_return(self, event) -> 1 | -1:
        """Update record in ThrowHistory with the new value.
        Return -1 if updated score is not valid"""
        updated_score = self.get_and_convert() 
        if not updated_score:
            self.config(foreground="red")
            return -1
        else:
            # Convert to list, to support item assignment
            original_th_values = list(self.parent.item(self.row, "values"))

            # Update sum field
            original_sum = original_th_values[-1]
            updated_sum = (int(original_sum) 
                        + updated_score[1] 
                        - self.original_score[1])

            # Update values        
            updated_th_values = original_th_values
            updated_th_values[self.column_id] = updated_score[0]
            updated_th_values[-1] = updated_sum

            # Update record in ThrowHistory
            self.parent.item(self.row, values=updated_th_values)

            # Update Statistics fields
            self.master.master.master.statistics.update_statistics()

            self.destroy()
        return 1
    
    def tab_pressed(self) -> None:
        """Create the next EntryPopup when tab is pressed and 
        the updated score is valid"""
        success = self.on_return(event=None)
        if success == 1:
            if self.column_id != 3:
                self.parent.master.edit_cell(event=None, row=self.row, 
                                            column=f"#{self.column_id + 2}")
        else:
            return "break"
        
            
if __name__ == "__main__":
    pass