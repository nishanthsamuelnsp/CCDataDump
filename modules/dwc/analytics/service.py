from collections import OrderedDict
from datetime import date, timedelta

import pandas as pd
import streamlit as st

from shared.defaults_service import get_supabase


METRICS = OrderedDict({

    # ---------- Daily Metrics ----------

    "total_delivered": {
        "label": "Total Delivery",
        "aggregate": "sum",
        "baseline": None,
        "direction": None,
    },

    "total_handled": {
        "label": "Total Handled",
        "aggregate": "sum",
        "baseline": None,
        "direction": None,
    },

    "accumulated_balance": {
        "label": "Accumulated Balance",
        "aggregate": "last",
        "baseline": None,
        "direction": None,
    },

    "absenteeism_pct": {
        "label": "Absenteeism (%)",
        "aggregate": "avg",
        "baseline": None,
        "direction": None,
    },

    "power_outage_pct": {
        "label": "Power Outage (%)",
        "aggregate": "avg",
        "baseline": None,
        "direction": None,
    },

    "total_recovery": {
        "label": "Total Recovery",
        "aggregate": "sum",
        "baseline": None,
        "direction": None,
    },

    "total_incinerated": {
        "label": "Total Incinerated",
        "aggregate": "sum",
        "baseline": None,
        "direction": None,
    },

    "soiling_incineration_pct": {
        "label": "Soiling Incineration (%)",
        "aggregate": "avg",
        "baseline": None,
        "direction": None,
    },

    # ---------- KPIs ----------

    "delivery_pct": {
        "label": "Dry Waste Delivery (%)",
        "aggregate": "avg",
        "baseline": 90,
        "direction": "min",
    },

    "unit_utilization_pct": {
        "label": "Unit Utilization (%)",
        "aggregate": "avg",
        "baseline": 90,
        "direction": "min",
    },

    "segregation_rate": {
        "label": "Visual Segregation Rate (%)",
        "aggregate": "avg",
        "baseline": 80,
        "direction": "min",
    },

    "moisture": {
        "label": "Moisture (%)",
        "aggregate": "avg",
        "baseline": 15,
        "direction": "max",
    },

    "waste_handling_rate_pct": {
        "label": "Waste Handling Rate (%)",
        "aggregate": "avg",
        "baseline": 90,
        "direction": "min",
    },

    "total_productivity": {
        "label": "Total Productivity",
        "aggregate": "avg",
        "baseline": None,
        "direction": None,
    },
  
    "resorting_rate": {
        "label": "Resorting Rate (kg/person-hr)",
        "aggregate": "derived",
        "baseline": 60,
        "direction": "min",
    },
    
  

    "total_recovery_pct": {
        "label": "Total Recovery (%)",
        "aggregate": "avg",
        "baseline": 40,
        "direction": "min",
    },

    "recyclables_pct": {
        "label": "Recyclables (%)",
        "aggregate": "avg",
        "baseline": 40,
        "direction": "min",
    },

    "compostables_pct": {
        "label": "Compostables (%)",
        "aggregate": "avg",
        "baseline": 15,
        "direction": "max",
    },

    "incineration_rate_pct": {
        "label": "Incinerates (%)",
        "aggregate": "avg",
        "baseline": 20,
        "direction": "min",
    },

    "productivity": {
        "label": "Sorter Productivity",
        "aggregate": "avg",
        "baseline": None,
        "direction": None,
    },

})

@st.cache_data(show_spinner=False)
def load_daily_history():

    sb = get_supabase()

    start_date = date.today() - timedelta(days=90)

    response = (
        sb.table("dwc4db")
        .select("*")
        .gte(
            "record_date",
            start_date.isoformat(),
        )
        .order(
            "record_date"
        )
        .execute()
    )

    df = pd.DataFrame(response.data)

    if df.empty:
        return df

    df["record_date"] = pd.to_datetime(
        df["record_date"]
    )
    # Expand the values JSON into columns
    values_df = pd.json_normalize(df["metrics"])
    
    df = pd.concat(
        [
            df.drop(columns=["metrics"]),
            values_df,
        ],
        axis=1,
    )

    df["resorting_rate"] = (
        df["total_productivity"] / 60
    )

    return df

def get_overview_dataframe(df):

    import pandas as pd

    if df.empty:
        return pd.DataFrame()

    df = df.sort_values("record_date")

    today = df.iloc[-1]

    yesterday = (
        df.iloc[-2]
        if len(df) > 1
        else None
    )

    rows = []

    for key, meta in METRICS.items():

        today_value = today.get(key)

        yesterday_value = (
            yesterday.get(key)
            if yesterday is not None
            else None
        )

        change = None

        if (
            yesterday_value is not None
            and yesterday_value != 0
            and pd.notna(yesterday_value)
            and pd.notna(today_value)
        ):

            change = (
                (today_value - yesterday_value)
                / yesterday_value
            ) * 100

        rows.append(
            {
                "Parameter": meta["label"],
                "Yesterday": yesterday_value,
                "Today": today_value,
                "Change (%)": change,
            }
        )

    return pd.DataFrame(rows)
