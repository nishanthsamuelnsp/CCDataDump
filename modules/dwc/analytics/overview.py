import streamlit as st
import pandas as pd

from .service import load_daily_history, METRICS


def render_overview():

    st.subheader("Overview")

    df = load_daily_history()

    if df.empty:
        st.info("No historical data available.")
        return

    st.write(df)
