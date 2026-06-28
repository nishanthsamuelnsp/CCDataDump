import streamlit as st
from .service import (
    load_history,
    METRICS,
)
from .charts import render_metric_chart

def render_historical():

    daily_df = load_history("daily")
    monthly_df = load_history("monthly")
    yearly_df = load_history("yearly")
    
    past_tab, monthly_tab, yearly_tab = st.tabs(
        [
            "Past 3 Months",
            "Monthly",
            "Yearly",
        ]
    )
    with past_tab:
        for key, meta in METRICS.items():
            render_metric_chart(
                daily_df,
                key,
                meta["label"],
                meta["baseline"],
            )
    
    with monthly_tab:
        for key, meta in METRICS.items():
            render_metric_chart(
                monthly_df,
                key,
                meta["label"],
                meta["baseline"],
            )
    
    with yearly_tab:
        for key, meta in METRICS.items():
            render_metric_chart(
                yearly_df,
                key,
                meta["label"],
                meta["baseline"],
            )
