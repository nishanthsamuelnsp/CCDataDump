# shared/entry_grid.py

from datetime import date, datetime
from decimal import Decimal

import streamlit as st

from shared.defaults_service import get_entry_window, save_record


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
def _validated_display_value(value):
    """
    Returns a string suitable for display in the cell.
    None stays blank.
    """
    if value is None:
        return ""

    if isinstance(value, float) and value.is_integer():
        return str(int(value))

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





def _initial_cell_value(existing_records, record_date, field):

    if record_date:
        existing = existing_records.get(record_date, {})

        if field["key"] in existing:
            return _safe_scalar(existing[field["key"]])

    return _safe_scalar(field.get("default"))


def render_entry_grid(module, section, section_config):
    grid_key = f"{module}_{section}_anchor_date"

    # Fix: do NOT pre-set session_state for a widget key —
    # pass value= directly to date_input instead
    anchor_date = st.date_input(
        "Anchor date",
        value=st.session_state.get(grid_key, date.today()),
        key=grid_key,
    )
    window = get_entry_window(
        module,
        section,
        anchor_date,
    )
    
    dates = window["dates"]
    existing_records = window["records"]

    st.caption("Columns show selected date and prior available-data dates.")

    headers = st.columns([2, 1, 1, 1])
    headers[0].markdown("**Field**")
    for i in range(3):
        headers[i + 1].markdown(f"**{dates[i] or 'Empty'}**")

    values_by_date = {d: {} for d in dates if d}
    validation_errors = []
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
                initial = _initial_cell_value(
                    existing_records,
                    record_date,
                    field,
                )
                st.session_state[cell_key] = _to_display_str(initial)

            # Always convert to safe string for widget value=
            display_val = _validated_display_value(
                st.session_state[cell_key]
            )


            entered = row[idx + 1].text_input(
                "",
                value=display_val,
                key=cell_key,
                label_visibility="collapsed",
            )
            
            if entered.strip():
                try:
                    float(entered)
                except ValueError:
                    validation_errors.append(
                        f"{record_date} → {field['label']}"
                    )
            
            values_by_date[record_date][field["key"]] = entered

    if st.button(
        f"Save {section_config['title']}",
        key=f"save_{module}_{section}",
    ):
    
        for record_date, payload in values_by_date.items():
    
            cleaned = {}
    
            for field in section_config["fields"]:
    
                raw = payload.get(field["key"], "")
    
                try:
                    cleaned[field["key"]] = _coerce_number(raw)
    
                except ValueError:
    
                    st.error(
                        f"{field['label']} ({record_date}) must contain only numbers."
                    )
                    st.toast(
                        f"{field['label']} ({record_date}) must be numeric.",
                        icon="⚠️",
                    )
    
                    st.stop()
    
            save_record(
                module,
                section,
                record_date,
                cleaned,
            )
    
        st.success(f"Saved {section_config['title']} records.")
        st.toast(
            f"{section_config['title']} saved successfully.",
            icon="✅",
        )


def _coerce_number(value):

    if value is None:
        return None

    value = str(value).strip()

    if value == "":
        return None

    try:
        num = float(value)

        if num.is_integer():
            return int(num)

        return num

    except ValueError:
        raise ValueError(f"'{value}' is not numeric.")
