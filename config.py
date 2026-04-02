import configparser
import os

CONFIG_DIR = os.path.dirname(__file__)
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.ini")

DEFAULTS = {
    "database": {
        "backup_path": os.path.join(CONFIG_DIR, "db", "backups"),
        "backup_keep_count": "20",
    }
}

def load_config() -> dict:
    """Load configuration from file, falling back to defaults."""
    config = configparser.ConfigParser()
    config.read_dict(DEFAULTS)
    if os.path.exists(CONFIG_FILE):
        config.read(CONFIG_FILE)
    return config

def save_config(config_dict: dict) -> None:
    """Save configuration to file."""
    config = configparser.ConfigParser()
    config.read_dict(config_dict)
    with open(CONFIG_FILE, "w") as f:
        config.write(f)
