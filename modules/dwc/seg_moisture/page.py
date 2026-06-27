import pandas as pd
import streamlit as st

from shared.defaults_service import (
    get_entry_window,
    save_record,
)

from .schema import SEGREGATION_COLUMNS
from .calculator import (
    segregation_summary,
    moisture_summary,
)


# =============================================================================
# Moisture Categories
# =============================================================================

MOISTURE_CATEGORIES = [
    "Plastic",
    "Paper & Cardboard",
    "Rubber & Leather",
    "Glass / E-waste / Metal",
    "Compostable",
    "Inert",
    "Textiles / Sanitary",
    "SCF",
]


# Internal calculator keys
MOISTURE_KEYS = {
    "Plastic": "plastic",
    "Paper & Cardboard": "paper_and_cardboard",
    "Rubber & Leather": "rubber_and_leather",
    "Glass / E-waste / Metal": "glass_ewaste_metal",
    "Compostable": "compostable_mixed_waste",
    "Inert": "inert",
    "Textiles / Sanitary": "incinerable",
    "SCF": "rdf",
}


# =============================================================================
# Empty DataFrames
# =============================================================================

def _empty_segregation_df():

    return pd.DataFrame(columns=SEGREGATION_COLUMNS)


def _empty_moisture_df():

    columns = [
        "Category",
        "Weight",
        "Fraction",
        "M1",
        "M2",
        "M3",
        "M4",
        "M5",
        "M6",
        "M7",
        "M8",
        "M9",
        "M10",
    ]

    df = pd.DataFrame(columns=columns)

    df["Category"] = MOISTURE_CATEGORIES

    return df


# =============================================================================
# Worksheet → DataFrame
# =============================================================================

def _worksheet_to_seg_df(worksheet):

    if not worksheet:
        return _empty_segregation_df()

    rows = worksheet.get("segregation", [])

    if not rows:
        return _empty_segregation_df()

    converted = []

    for row in rows:

        current = {
            "Vehicle": row.get("vehicle"),
            "Weight": row.get("weight"),
        }

        samples = row.get("samples", [])

        for i in range(10):

            current[f"S{i+1}"] = (
                samples[i]
                if i < len(samples)
                else None
            )

        converted.append(current)

    return pd.DataFrame(converted)


def _worksheet_to_moisture_df(worksheet):

    df = _empty_moisture_df()

    if not worksheet:
        return df

    moisture = worksheet.get("moisture", {})

    for idx, category in enumerate(MOISTURE_CATEGORIES):

        key = MOISTURE_KEYS[category]

        samples = moisture.get(key, [])

        for i in range(10):

            if i < len(samples):
                df.loc[idx, f"M{i+1}"] = samples[i]

    return df


# =============================================================================
# DataFrame → Worksheet
# =============================================================================

def _seg_df_to_worksheet(df):

    rows = []

    for _, row in df.iterrows():

        samples = []

        for i in range(10):

            value = row.get(f"S{i+1}")

            if pd.isna(value):
                samples.append(None)
            else:
                samples.append(value)

        rows.append({
            "vehicle": row.get("Vehicle"),
            "weight": row.get("Weight"),
            "samples": samples,
        })

    return rows


def _moisture_df_to_worksheet(df):

    moisture = {}

    for _, row in df.iterrows():

        key = MOISTURE_KEYS[row["Category"]]

        samples = []

        for i in range(10):

            value = row[f"M{i+1}"]

            if pd.isna(value):
                samples.append(None)
            else:
                samples.append(value)

        moisture[key] = samples

    return moisture
# =============================================================================
# Page
# =============================================================================

def render_seg_moisture_page():

    st.subheader("Segregation & Moisture Calculator")

    # ------------------------------------------------------------------
    # Date
    # ------------------------------------------------------------------

    anchor_date = st.date_input(
        "Record Date"
    )

    # ------------------------------------------------------------------
    # Fetch handling record
    # ------------------------------------------------------------------

    window = get_entry_window(
        "dwc",
        "handling",
        anchor_date,
        count=1,
    )

    record_date = str(anchor_date)

    existing = window["records"].get(
        record_date,
        {
            "values": {},
            "worksheet": {},
        },
    )

    values = existing["values"]
    worksheet = existing["worksheet"]

    # ------------------------------------------------------------------
    # Handling prerequisite
    # ------------------------------------------------------------------

    if not values:

        st.warning(
            "Handling entry does not exist for the selected date."
        )

        st.stop()

    if values.get("weight_received") in (None, "", 0):

        st.warning(
            "Weight received has not been entered. "
            "Complete Dry Waste Handling before using this calculator."
        )

        st.stop()

    # ------------------------------------------------------------------
    # Segregation worksheet
    # ------------------------------------------------------------------

    st.markdown("### Segregation")

    seg_df = _worksheet_to_seg_df(worksheet)

    seg_df = st.data_editor(
        seg_df,
        num_rows="dynamic",
        hide_index=True,
        use_container_width=True,
        key=f"seg_editor_{record_date}",
    )

    # ------------------------------------------------------------------
    # Build calculator payload
    # ------------------------------------------------------------------

    vehicles = []

    for _, row in seg_df.iterrows():

        samples = []

        for i in range(10):

            samples.append(
                row.get(f"S{i+1}")
            )

        vehicles.append(
            {
                "vehicle": row.get("Vehicle"),
                "weight": row.get("Weight"),
                "samples": samples,
            }
        )

    segregation = segregation_summary(
        vehicles
    )

    # ------------------------------------------------------------------
    # Results
    # ------------------------------------------------------------------

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Segregation %",
        "-"
        if segregation["overall"] is None
        else f"{segregation['overall']:.2f}"
    )

    c2.metric(
        "Vehicles Sampled",
        segregation["vehicles_sampled"],
    )

    c3.metric(
        "Sampled Weight",
        f"{segregation['sampled_weight']:.2f} kg",
    )

    st.divider()
