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
        "Average",
        "Contribution",
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
# Computed View
# =============================================================================

from supabase import create_client


def _get_supabase():

    return create_client(
        st.secrets["SUPABASE_URL"],
        st.secrets["SUPABASE_KEY"],
    )


def get_computed_row(record_date):

    sb = _get_supabase()

    resp = (
        sb.table("dwc_computed")
        .select("*")
        .eq("record_date", str(record_date))
        .limit(1)
        .execute()
    )

    rows = resp.data or []

    if not rows:
        return None

    return rows[0]


def get_category_weights(row):

    if row is None:
        return None

    return {

        "plastic":
            (row.get("high_value_plastic") or 0)
            + (row.get("low_value_plastic") or 0),

        "paper_and_cardboard":
            (row.get("paper") or 0)
            + (row.get("cardboard") or 0),

        "rubber_and_leather":
            row.get("leather_and_rubber") or 0,

        "glass_ewaste_metal":
            (row.get("ewaste_and_metal") or 0)
            + (row.get("recyclable_glass") or 0)
            + (row.get("reusable_glass") or 0),

        "compostable_mixed_waste":
            row.get("compostable_mixed_waste") or 0,

        "inert":
            row.get("inert") or 0,

        "incinerable":
            (row.get("incinerable_ss") or 0)
            + (row.get("incinerable_ds") or 0),

        "rdf":
            row.get("rdf") or 0,
    }


# =============================================================================
# Page
# =============================================================================

def render_seg_moisture_page():

    st.subheader("Segregation & Moisture Calculator")

    anchor_date = st.date_input(
        "Record Date"
    )

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

    computed = get_computed_row(
        record_date
    )

    if computed is None:

        st.warning(
            "Computed handling data is unavailable for this date."
        )

        st.stop()

    category_weights = get_category_weights(
        computed
    )

    if sum(category_weights.values()) == 0:

        st.warning(
            "Handling has not yet been completed for this date."
        )

        st.info(
            "Complete Dry Waste Handling before using the Segregation & Moisture calculator."
        )

        st.stop()

    # ================================================================
    # Segregation
    # ================================================================

    st.markdown("## Segregation")

    seg_df = _worksheet_to_seg_df(
        worksheet
    )

    seg_df = st.data_editor(
        seg_df,
        num_rows="dynamic",
        use_container_width=True,
        hide_index=True,
        key=f"seg_{record_date}",
    )

    vehicles = []

    for _, row in seg_df.iterrows():

        vehicles.append({

            "vehicle":
                row.get("Vehicle"),

            "weight":
                row.get("Weight"),

            "samples": [

                row.get(f"S{i}")

                for i in range(1, 11)

            ]

        })

    segregation = segregation_summary(
        vehicles
    )

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Segregation %",
        "-"
        if segregation["overall"] is None
        else f"{segregation['overall']:.2f}"
    )

    c2.metric(
        "Vehicles",
        segregation["vehicles_sampled"]
    )

    c3.metric(
        "Sampled Weight",
        f"{segregation['sampled_weight']:.2f} kg"
    )

    st.divider()
    # ================================================================
    # Moisture
    # ================================================================

    st.markdown("## Moisture")

    moisture_df = _worksheet_to_moisture_df(
        worksheet
    )

    # ----------------------------------------------------------
    # Populate calculated weights
    # ----------------------------------------------------------

    total_weight = sum(category_weights.values())

    for idx, category in enumerate(MOISTURE_CATEGORIES):

        key = MOISTURE_KEYS[category]

        weight = category_weights.get(key, 0)

        moisture_df.loc[idx, "Weight"] = round(weight, 2)

        moisture_df.loc[idx, "Fraction"] = (
            round(weight / total_weight, 4)
            if total_weight
            else 0
        )

    moisture_df = st.data_editor(
        moisture_df,
        hide_index=True,
        use_container_width=True,
        disabled=[
            "Category",
            "Weight",
            "Fraction",
            "Average",
            "Contribution",
        ],
        key=f"moisture_{record_date}",
    )

    # ----------------------------------------------------------
    # Build calculator payload
    # ----------------------------------------------------------

    moisture_samples = {}

    for _, row in moisture_df.iterrows():

        key = MOISTURE_KEYS[
            row["Category"]
        ]

        moisture_samples[key] = [

            row.get(f"M{i}")

            for i in range(1, 11)

        ]

    moisture = moisture_summary(
        category_weights,
        moisture_samples,
    )
    for row in moisture["rows"]:

    category = row["category"]

    display = {
        "plastic": "Plastic",
        "paper_and_cardboard": "Paper & Cardboard",
        "rubber_and_leather": "Rubber & Leather",
        "glass_ewaste_metal": "Glass / E-waste / Metal",
        "compostable_mixed_waste": "Compostable",
        "inert": "Inert",
        "incinerable": "Textiles / Sanitary",
        "rdf": "SCF",
    }[category]

    idx = moisture_df.index[
        moisture_df["Category"] == display
    ][0]

    moisture_df.loc[idx, "Average"] = row["average"]

    moisture_df.loc[idx, "Contribution"] = row["contribution"]

    st.metric(

        "Overall Moisture",

        "-"
        if moisture["overall"] is None
        else f"{moisture['overall']:.2f} %",

    )

    st.divider()
        # ================================================================
    # Save
    # ================================================================

    if st.button(
        "Save Segregation & Moisture",
        use_container_width=True,
    ):

        # ---------------------------------------------
        # Build worksheet JSON
        # ---------------------------------------------

        worksheet = {

            "segregation":
                _seg_df_to_worksheet(
                    seg_df
                ),

            "moisture":
                _moisture_df_to_worksheet(
                    moisture_df
                ),

        }

        # ---------------------------------------------
        # Update handling values
        # ---------------------------------------------

        values["segregation_rate"] = (
            segregation["overall"]
        )

        values["moisture"] = (
            moisture["overall"]
        )

        # ---------------------------------------------
        # Save
        # ---------------------------------------------

        save_record(

            module="dwc",

            section="handling",

            record_date=record_date,

            values=values,

            worksheet=worksheet,

        )

        st.success(
            "Segregation & Moisture saved successfully."
        )

        st.rerun()
