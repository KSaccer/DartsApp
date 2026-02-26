import os
import tkinter as tk
import tkinter.ttk as ttk
import config
from pathlib import Path
from tkinter import filedialog
from ..constants import FONT_TITLE, COLOR_FONT_TITLE
from ..widgets.custom_popup import CustomPopup


class PageTitle(ttk.Frame):
    """Reusable title header for the settings page."""

    def __init__(self, parent, text: str = "Settings", *args, **kwargs) -> None:
        super().__init__(parent, *args, **kwargs)
        label = ttk.Label(
            self,
            text=text,
            font=FONT_TITLE,
            foreground=COLOR_FONT_TITLE,
            anchor="center",
        )
        label.pack(expand=True, fill="both")

class Settings(ttk.Frame):
    """Settings page for configuring database backup preferences."""

    def __init__(self, parent, *args, **kwargs) -> None:
        """Initialize the settings page and load persisted values into the form."""
        super().__init__(parent, *args, **kwargs)
        self.config = config.load_config()
        if not self.config.has_section("database"):
            self.config.add_section("database")

        self.backup_var = tk.StringVar()
        self._saved_backup_path = ""
        self._gui_created = False

        self._configure_layout()
        self.create_gui()
        self.reload_settings(show_message=False)

    def _configure_layout(self) -> None:
        """Configure the root grid layout for the settings page."""
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

    def create_gui(self) -> None:
        """Create and arrange the settings page widgets."""
        if self._gui_created:
            self._update_save_state()
            return

        self.page_title = PageTitle(self, text="Settings")
        self.page_title.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 6))

        self.database_frame = ttk.LabelFrame(self, text="Database / Backup", padding=10)
        self.database_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        self.database_frame.columnconfigure(1, weight=1)

        ttk.Label(self.database_frame, text="Backup Folder:").grid(
            row=0, column=0, sticky="w", padx=(0, 10), pady=5
        )

        self.backup_entry = ttk.Entry(self.database_frame, textvariable=self.backup_var)
        self.backup_entry.grid(row=0, column=1, sticky="ew", pady=5)
        self.backup_entry.bind("<Return>", self._on_enter_pressed)

        self.browse_btn = ttk.Button(
            self.database_frame, text="Browse...", command=self.choose_backup_dir
        )
        self.browse_btn.grid(row=0, column=2, sticky="w", padx=(8, 0), pady=5)

        actions = ttk.Frame(self)
        actions.grid(row=2, column=0, sticky="ew", padx=10, pady=(0, 10))
        actions.columnconfigure(0, weight=1)

        self.reset_btn = ttk.Button(actions, text="Reset to Default", command=self.reset_to_defaults)
        self.reset_btn.grid(row=0, column=1, padx=(0, 8))

        self.cancel_btn = ttk.Button(actions, text="Cancel", command=self.reload_settings)
        self.cancel_btn.grid(row=0, column=2, padx=(0, 8))

        self.save_btn = ttk.Button(actions, text="Save", command=self.save_settings)
        self.save_btn.grid(row=0, column=3)

        self.backup_var.trace_add("write", self._on_form_changed)
        self.bind("<Return>", self._on_enter_pressed)
        self._gui_created = True

    def _normalize_path(self, value: str) -> str:
        """Return a trimmed, normalized POSIX-style path string when possible."""
        value = (value or "").strip()
        if not value:
            return ""

        try:
            return Path(value).expanduser().as_posix()
        except (OSError, RuntimeError, ValueError):
            return value.replace("\\", "/")

    def _get_config_backup_path(self) -> str:
        """Read and normalize the backup path from the current config object."""
        raw_value = self.config.get("database", "backup_path", fallback="")
        return self._normalize_path(raw_value)

    def _load_form_values_from_config(self) -> None:
        """Populate form fields from config and refresh the save button state."""
        backup_path = self._get_config_backup_path()
        self._saved_backup_path = backup_path
        self.backup_var.set(backup_path)
        self._update_save_state()

    def _on_form_changed(self, *_: object) -> None:
        """Handle form changes by recalculating whether saving is needed."""
        self._update_save_state()

    def _update_save_state(self) -> None:
        """Enable Save only when the current form value differs from saved data."""
        current_value = self._normalize_path(self.backup_var.get())
        state = "normal" if current_value != self._saved_backup_path else "disabled"
        self.save_btn.config(state=state)

    def _on_enter_pressed(self, event: object | None = None) -> str:
        """Save settings on Enter when changes are pending and suppress default handling."""
        if str(self.save_btn.cget("state")) != "disabled":
            self.save_settings()
        return "break"

    def _validate_backup_path(self, value: str) -> tuple[str | None, str | None]:
        """Validate the backup folder path and return a normalized path or an error."""
        normalized = self._normalize_path(value)
        if not normalized:
            return None, "Backup folder path cannot be empty."

        backup_dir = Path(normalized)
        if backup_dir.exists():
            if not backup_dir.is_dir():
                return None, "Backup path must point to a folder."
            if not os.access(backup_dir, os.W_OK):
                return None, "Backup folder is not writable."
            return normalized, None

        # Allow a new folder path if it can be created under a writable parent.
        probe = backup_dir.parent
        while probe != probe.parent and not probe.exists():
            probe = probe.parent

        if not probe.exists():
            return None, "Backup folder parent does not exist."
        if not probe.is_dir():
            return None, "Backup folder parent must be a folder."
        if not os.access(probe, os.W_OK):
            return None, "Backup folder parent is not writable."

        return normalized, None

    def choose_backup_dir(self) -> None:
        """Open a folder picker and store the selected backup directory."""
        dialog_kwargs = {"title": "Select Backup Directory"}
        current_path = self._normalize_path(self.backup_var.get())
        if current_path and Path(current_path).exists():
            dialog_kwargs["initialdir"] = current_path

        path = filedialog.askdirectory(**dialog_kwargs)
        if path:
            self.backup_var.set(self._normalize_path(path))

    def reload_settings(self, show_message: bool = True) -> None:
        """Reload settings from disk, repopulate the form, and optionally notify the user."""
        self.config = config.load_config()
        if not self.config.has_section("database"):
            self.config.add_section("database")
        self._load_form_values_from_config()
        if show_message:
            CustomPopup(
                popup_type="information",
                title="Settings",
                message="Unsaved changes were discarded.",
                master=self.winfo_toplevel(),
            )

    def reset_to_defaults(self) -> None:
        """Reset form fields to application default values without saving."""
        default_backup = config.DEFAULTS.get("database", {}).get("backup_path", "")
        self.backup_var.set(self._normalize_path(default_backup))

    def save_settings(self) -> None:
        """Validate and persist the current settings, then update the form state."""
        normalized_path, error_message = self._validate_backup_path(self.backup_var.get())
        if error_message:
            CustomPopup(
                popup_type="error",
                title="Settings",
                message=error_message,
                master=self.winfo_toplevel(),
            )
            return

        if not self.config.has_section("database"):
            self.config.add_section("database")

        self.config["database"]["backup_path"] = normalized_path

        try:
            config.save_config(self.config)
        except OSError as exc:
            CustomPopup(
                popup_type="error",
                title="Settings",
                message=f"Failed to save settings:\n{exc}",
                master=self.winfo_toplevel(),
            )
            return

        self.backup_var.set(normalized_path)
        self._saved_backup_path = normalized_path
        self._update_save_state()
        CustomPopup(
            popup_type="information",
            title="Settings",
            message="Backup folder saved.",
            master=self.winfo_toplevel(),
        )

if __name__ == "__main__":
    pass
