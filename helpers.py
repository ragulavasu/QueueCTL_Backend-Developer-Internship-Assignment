import json
import os
import time
from datetime import datetime

CONFIG_FILE = "config.json"


def load_config():
    """Load retry and backoff configuration."""
    if not os.path.exists(CONFIG_FILE):
        return {"max_retries": 3, "backoff_base": 2}
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)


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
