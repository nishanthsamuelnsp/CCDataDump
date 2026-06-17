import json
from pathlib import Path
from copy import deepcopy

from shared.defaults import get_defaults

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data" / "dummy"
DEFAULTS_PATH = DATA_DIR / "defaults.json"
RECORDS_PATH = DATA_DIR / "entry_records.json"


def _ensure_dir():
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def load_defaults():
    _ensure_dir()
    base = get_defaults()
    if not DEFAULTS_PATH.exists():
        return base
    saved = json.loads(DEFAULTS_PATH.read_text())
    return _deep_merge(base, saved)


def save_defaults(payload):
    _ensure_dir()
    DEFAULTS_PATH.write_text(json.dumps(payload, indent=2))


def _deep_merge(base, override):
    merged = deepcopy(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def load_records():
    _ensure_dir()
    if not RECORDS_PATH.exists():
        return []
    return json.loads(RECORDS_PATH.read_text())


def save_record(module, section, record_date, values):
    records = load_records()
    updated = False
    for row in records:
        if row["module"] == module and row["section"] == section and row["date"] == record_date:
            row["values"] = values
            updated = True
            break
    if not updated:
        records.append({
            "module": module,
            "section": section,
            "date": record_date,
            "values": values,
        })
    records.sort(key=lambda x: (x["module"], x["section"], x["date"]), reverse=True)
    _ensure_dir()
    RECORDS_PATH.write_text(json.dumps(records, indent=2))


def get_record(module, section, record_date):
    for row in load_records():
        if row["module"] == module and row["section"] == section and row["date"] == record_date:
            return row["values"]
    return None


def get_available_dates(module, section):
    dates = {
        row["date"]
        for row in load_records()
        if row["module"] == module and row["section"] == section
    }
    return sorted(dates, reverse=True)
