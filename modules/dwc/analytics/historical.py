import streamlit as st
from .service import (
    load_history,
    METRICS,
)

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
        st.write("Daily graphs")
    
    with monthly_tab:
        st.write("Monthly graphs")
    
    with yearly_tab:
        st.write("Yearly graphs")
