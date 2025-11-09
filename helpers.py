import json
import os
import time
from datetime import datetime

CONFIG_FILE = "config.json"


def load_config():
    """Load retry and backoff configuration."""
    if not os.path.exists(CONFIG_FILE):
        default_config = {"max_retries": 3, "backoff_base": 2}
        save_config(default_config)
        return default_config
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)


def save_config(config):
    """Save retry and backoff configuration."""
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)


def set_config(key, value):
    """Set a configuration value."""
    config = load_config()
    if key == "max-retries":
        config["max_retries"] = int(value)
    elif key == "backoff-base":
        config["backoff_base"] = int(value)
    else:
        return False
    save_config(config)
    return True


def get_config(key=None):
    """Get configuration value(s)."""
    config = load_config()
    if key is None:
        return config
    if key == "max-retries":
        return config.get("max_retries", 3)
    elif key == "backoff-base":
        return config.get("backoff_base", 2)
    return None


def exponential_backoff(base, attempt):
    """Calculate delay time using exponential backoff."""
    return base ** attempt


def log(message):
    """Simple timestamped console logger."""
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{now}] {message}")


def sleep_for_delay(seconds):
    """Sleep for a delay with a message."""
    log(f"Retrying in {seconds} seconds...")
    time.sleep(seconds)
