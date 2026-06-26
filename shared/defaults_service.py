import json
from copy import deepcopy
from pathlib import Path

import streamlit as st
from supabase import create_client

from shared.defaults import get_defaults

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data" / "dummy"
DEFAULTS_PATH = DATA_DIR / "defaults.json"


# ──────────────────────────────────────────────────────────────────────────────
# Local defaults JSON
# ──────────────────────────────────────────────────────────────────────────────

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


# ──────────────────────────────────────────────────────────────────────────────
# Supabase records
# Table: dwc_entry
# Columns expected:
#   module text
#   section text
#   record_date date
#   values jsonb
#   updated_by text (optional)
# Unique key:
#   (module, section, record_date)
# ──────────────────────────────────────────────────────────────────────────────

def _get_supabase():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)


def _current_user_email():
    return st.session_state.get("username")


def load_records():
    """
    Optional helper: fetch all dwc_entry.
    Not used by the DWC entry grid directly, but kept for compatibility.
    """
    sb = _get_supabase()
    resp = (
        sb.table("dwc_entry")
        .select("module, section, record_date, values, updated_by, created_at, updated_at")
        .order("record_date", desc=True)
        .execute()
    )
    return resp.data or []


def save_record(module, section, record_date, values):
    """
    Upsert one row into dwc_entry using (module, section, record_date).
    record_date should be a YYYY-MM-DD string.
    values should be a plain dict.
    """
    sb = _get_supabase()

    payload = {
        "module": module,
        "section": section,
        "record_date": str(record_date),
        "values": values,
        "updated_by": _current_user_email(),
    }

    (
        sb.table("dwc_entry")
        .upsert(
            payload,
            on_conflict="module,section,record_date",
        )
        .execute()
    )


def get_record(module, section, record_date):
    """
    Return the values dict for one module+section+date row, or None if missing.
    """
    sb = _get_supabase()
    resp = (
        sb.table("dwc_entry")
        .select("values")
        .eq("module", module)
        .eq("section", section)
        .eq("record_date", str(record_date))
        .limit(1)
        .execute()
    )

    rows = resp.data or []
    

    if not rows:
        return None

    return rows[0].get("values")


def get_available_dates(module, section):
    """
    Return available record_date values for a module+section as descending YYYY-MM-DD strings.
    """
    sb = _get_supabase()

    resp = (
        sb.table("dwc_entry")
        .select("record_date")
        .eq("module", module)
        .eq("section", section)
        .order("record_date", desc=True)
        .execute()
    )

    rows = resp.data or []
    return [row["record_date"] for row in rows if row.get("record_date")]
