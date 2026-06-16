import streamlit as st

def section_header(title: str, help_text: str | None = None):
    st.subheader(title)
    if help_text:
        st.caption(help_text)
