from datetime import date, datetime

import streamlit as st

from shared.defaults_service import get_available_dates, get_record, save_record


def _to_iso(d):
    if isinstance(d, datetime):
        return d.date().isoformat()
    if hasattr(d, "isoformat"):
        return d.isoformat()
    return str(d)


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
            return existing[field["key"]]
    return field.get("default")


def render_entry_grid(module, section, section_config):
    grid_key = f"{module}_{section}_anchor_date"
    if grid_key not in st.session_state:
        st.session_state[grid_key] = date.today()

    anchor_date = st.date_input(
        "Anchor date",
        value=st.session_state[grid_key],
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
            initial = _initial_cell_value(module, section, record_date, field)
            if cell_key not in st.session_state:
                st.session_state[cell_key] = initial
            values_by_date[record_date][field["key"]] = row[idx + 1].text_input(
                label=field["label"],
                value="" if st.session_state[cell_key] is None else str(st.session_state[cell_key]),
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
