import streamlit as st

from .overview import render_overview
from .historical import render_historical


def render_analytics_page():

    st.header("Analytics")

    overview_tab, historical_tab = st.tabs(
        [
            "Overview",
            "Historical",
        ]
    )

    with overview_tab:
        render_overview()

    with historical_tab:
        render_historical()
