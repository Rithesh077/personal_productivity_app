import json
from pathlib import Path

DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "tasks.json"


def load_data():
    if DATA_FILE.exists():
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return []


def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)
