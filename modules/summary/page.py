import streamlit as st
from shared.dummy_data import sample_summary_data

def render_summary_page(public_view: bool = False):
    st.title("Recovery Center Summary")
    if public_view:
        st.caption("Public view: high-level summary only")
    else:
        st.caption("Admin view: operational summary")

    df = sample_summary_data()
    st.dataframe(df, use_container_width=True)
