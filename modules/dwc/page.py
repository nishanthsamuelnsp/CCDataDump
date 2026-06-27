import streamlit as st

from modules.dwc.entry.schema import get_dwc_entry_sections
from shared.entry_grid import render_entry_grid
from shared.defaults_service import load_defaults, save_defaults
from modules.dwc.seg_moisture.page import (
    render_seg_moisture_page,
)


MODULE_KEY = "dwc"


def render_dwc_entry_page():
    st.subheader("DWC Data Entry")
    sections = get_dwc_entry_sections()

    tab1, tab2, tab3, tab4 = st.tabs([
        "Dry Waste Handling",
        "Dry Waste Dispatch",
        "Segregation & Moisture",
        "Edit Defaults",
    ])

    with tab1:
        render_entry_grid(MODULE_KEY, "handling", sections["handling"])

    with tab2:
        render_entry_grid(MODULE_KEY, "dispatch", sections["dispatch"])
    with tab3:

    render_seg_moisture_page()

    with tab4:
        render_defaults_editor()


def render_defaults_editor():
    defaults = load_defaults()
    st.caption("Single defaults source with DWC/WWC/Rural sections.")

    dwc_sections = {
        "handling": defaults["dwc"]["handling"],
        "dispatch": defaults["dwc"]["dispatch"],
    }

    for section_key, section in dwc_sections.items():
        with st.expander(section["title"], expanded=(section_key == "handling")):
            for field in section["fields"]:
                k1 = f"defaults_label_{section_key}_{field['key']}"
                k2 = f"defaults_unit_{section_key}_{field['key']}"
                k3 = f"defaults_value_{section_key}_{field['key']}"
                c1, c2, c3 = st.columns([2, 1, 1])
                field["label"] = c1.text_input("Label", value=field["label"], key=k1, label_visibility="collapsed")
                field["unit"] = c2.text_input("Unit", value=field.get("unit", ""), key=k2, label_visibility="collapsed")
                raw_default = "" if field.get("default") is None else str(field.get("default"))
                entered = c3.text_input("Default", value=raw_default, key=k3, label_visibility="collapsed")
                field["default"] = None if entered == "" else _coerce_default(entered)

    if st.button("Save defaults", key="save_dwc_defaults"):
        save_defaults(defaults)
        st.success("Defaults updated.")


def _coerce_default(value):
    try:
        num = float(value)
        return int(num) if num.is_integer() else num
    except Exception:
        return value
