import json
from pathlib import Path
import os


def get_data_path(filename):
    p = Path(filename)
    p.parent.mkdir(parents=True, exist_ok=True)
    return p


def load_data(filename):
    """
    Loads data from the specified JSON file.
    It returns an empty list if the file does not exist or is empty/corrupted.
    """
    data_file = get_data_path(filename)
    if data_file.exists():
        try:
            with open(data_file, "r") as f:
                content = f.read()
                if content:
                    return json.loads(content)
        except json.JSONDecodeError:
            print("Warning: Corrupted data file. Starting with an empty list.")
            pass
    return []


def save_data(filename, data):
    """Saves data to the specified JSON file."""
    data_file = get_data_path(filename)
    with open(data_file, "w") as f:
        json.dump(data, f, indent=4)
    print("Data saved successfully.")
