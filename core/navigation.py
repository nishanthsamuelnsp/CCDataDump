import streamlit as st
from modules.summary.page import render_summary_page
from modules.dwc.page import render_dwc_page
from modules.wwc.page import render_wwc_page
from modules.rural.page import render_rural_page

def render_navigation(user, role):
    st.sidebar.title("Recovery Dashboard")
    st.sidebar.caption(f"Signed in as: {^(user or {}^).get('email', 'Guest')}")
    st.sidebar.caption(f"Role: {role}")

    if role == "public":
        render_summary_page(public_view=True)
        return

    page = st.sidebar.radio(
        "Go to",
        ["Summary", "DWC", "WWC", "Rural"],
        index=0,
    )

    if page == "Summary":
        render_summary_page(public_view=False)
    elif page == "DWC":
        render_dwc_page()
    elif page == "WWC":
        render_wwc_page()
    elif page == "Rural":
        render_rural_page()
