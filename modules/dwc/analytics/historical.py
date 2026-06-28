import streamlit as st


def render_historical():

    st.subheader("Historical Trends")

    past3_tab, monthly_tab, yearly_tab = st.tabs(
        [
            "Past 3 Months",
            "Monthly",
            "Yearly",
        ]
    )

    with past3_tab:

        st.info(
            "Daily trends for the past three months."
        )

    with monthly_tab:

        st.info(
            "Monthly average trends."
        )

    with yearly_tab:

        st.info(
            "Yearly average trends."
        )
