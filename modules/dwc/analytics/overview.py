import streamlit as st
import pandas as pd


def render_overview():

    st.subheader("Overview")

    # Placeholder until service.py is implemented
    df = pd.DataFrame(
        columns=[
            "Parameter",
            "Yesterday",
            "Today",
            "Change",
        ]
    )

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
    )
