import streamlit as st

from .service import (
    load_history,
    get_overview_dataframe,
)


def render_overview():

    df = load_history("daily")

    overview = get_overview_dataframe(df)

    st.dataframe(
        overview,
        use_container_width=True,
        hide_index=True,
    )
