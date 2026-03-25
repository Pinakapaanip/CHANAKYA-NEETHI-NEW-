import json
from pathlib import Path


def load_json(path, default=None):
    file_path = Path(path)
    if not file_path.exists():
        return {} if default is None else default

    try:
        with file_path.open("r", encoding="utf-8") as file_obj:
            return json.load(file_obj)
    except (json.JSONDecodeError, OSError):
        return {} if default is None else default


def save_json(path, data):
    file_path = Path(path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with file_path.open("w", encoding="utf-8") as file_obj:
        json.dump(data, file_obj, indent=2)
