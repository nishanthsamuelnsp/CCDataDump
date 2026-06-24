# shared/entry_grid.py

from datetime import date, datetime
from decimal import Decimal

import streamlit as st

from shared.defaults_service import get_available_dates, get_record, save_record


def _to_iso(d):
    if isinstance(d, datetime):
        return d.date().isoformat()
    if hasattr(d, "isoformat"):
        return d.isoformat()
    return str(d)


def _safe_scalar(value):
    """Coerce any DB/numpy/Decimal value to a plain Python str-safe type."""
    if value is None:
        return None
    if isinstance(value, Decimal):
        f = float(value)
        return int(f) if f == int(f) else f
    if hasattr(value, "item"):          # numpy scalar (int64, float64, etc.)
        return value.item()
    if isinstance(value, (int, float, str, bool)):
        return value
    # fallback — cast to float if it looks numeric, else str
    try:
        return float(value)
    except (TypeError, ValueError):
        return str(value)


def _to_display_str(value):
    if value is None:
        return ""
    try:
        return str(value)
    except Exception:
        return ""


def get_display_label(field):
    unit = field.get("unit")
    return f"{field['label']} ({unit})" if unit else field["label"]


def get_prior_available_dates(module, section, anchor_date, count):
    available = get_available_dates(module, section)
    anchor_iso = _to_iso(anchor_date)
    return [d for d in available if d < anchor_iso][:count]


def resolve_dates(module, section, anchor_date, num_columns=3):
    dates = [_to_iso(anchor_date)]
    dates.extend(get_prior_available_dates(module, section, anchor_date, num_columns - 1))
    while len(dates) < num_columns:
        dates.append(None)
    return dates


def _initial_cell_value(module, section, record_date, field):
    if record_date:
        existing = get_record(module, section, record_date)
        if existing and field["key"] in existing:
            # Always coerce DB value to plain Python type on the way out
            return _safe_scalar(existing[field["key"]])
    default = field.get("default")
    return _safe_scalar(default)


def render_entry_grid(module, section, section_config):
    grid_key = f"{module}_{section}_anchor_date"

    # Fix: do NOT pre-set session_state for a widget key —
    # pass value= directly to date_input instead
    anchor_date = st.date_input(
        "Anchor date",
        value=st.session_state.get(grid_key, date.today()),
        key=grid_key,
    )
    dates = resolve_dates(module, section, anchor_date)

    st.caption("Columns show selected date and prior available-data dates.")

    headers = st.columns([2, 1, 1, 1])
    headers[0].markdown("**Field**")
    for i in range(3):
        headers[i + 1].markdown(f"**{dates[i] or 'Empty'}**")

    values_by_date = {d: {} for d in dates if d}

    for field in section_config["fields"]:
        row = st.columns([2, 1, 1, 1])
        row[0].write(get_display_label(field))
        for idx, record_date in enumerate(dates):
            if record_date is None:
                row[idx + 1].write("-")
                continue
            cell_key = f"{module}_{section}_{record_date}_{field['key']}"

            # Only fetch initial value if not already in session state
            if cell_key not in st.session_state:
                st.session_state[cell_key] = _initial_cell_value(
                    module, section, record_date, field
                )

            # Always convert to safe string for widget value=
            display_val = _to_display_str(st.session_state[cell_key])
            st.write("DEBUG", field["key"], type(display_val), repr(display_val))

            values_by_date[record_date][field["key"]] = row[idx + 1].text_input(
                label=field["label"],
                value=display_val,
                key=cell_key,
                label_visibility="collapsed",
            )

    if st.button(f"Save {section_config['title']}", key=f"save_{module}_{section}"):
        for record_date, payload in values_by_date.items():
            cleaned = {}
            for field in section_config["fields"]:
                raw = payload.get(field["key"], "")
                cleaned[field["key"]] = None if raw == "" else _coerce_number(raw)
            save_record(module, section, record_date, cleaned)
        st.success(f"Saved {section_config['title']} records.")


def _coerce_number(value):
    try:
        num = float(value)
        return int(num) if num.is_integer() else num
    except Exception:
        return value
