# app.py

import streamlit as st

from core.auth import init_session_auth, logout_user
from modules.summary.page import render_summary_page
from modules.dwc.page import render_dwc_entry_page
from modules.wwc.page import render_wwc_page
from modules.rural.page import render_rural_page

st.set_page_config(page_title="Recovery Dashboard", layout="wide")

# ── Bootstrap auth (safe to call on every rerun) ────────────────────────────
init_session_auth()

role = st.session_state["role"]

# ── Sidebar: signed in as / sign out ───────────────────────────────────────
with st.sidebar:
    if st.session_state["authenticated"] and role == "admin":
        st.markdown(
            f"""
            <div style='padding:0.5rem 0 0.75rem; border-bottom:1px solid rgba(0,0,0,0.1); margin-bottom:0.75rem;'>
                <div style='font-size:0.75rem; color:grey; margin-bottom:2px;'>Signed in as</div>
                <div style='font-weight:600; font-size:0.9rem; word-break:break-all;'>{st.session_state['username']}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Sign out", key="signout_btn", use_container_width=True):
            logout_user()
            st.rerun()
    else:
        st.markdown(
            "<div style='font-size:0.8rem; color:grey; padding:0.4rem 0;'>Viewing as public</div>",
            unsafe_allow_html=True,
        )

# ── Route ───────────────────────────────────────────────────────────────────
if role != "admin":
    render_summary_page(public_view=True)
    st.stop()

summary_page = st.Page(
    lambda: render_summary_page(public_view=False),
    title="Summary",
    url_path="summary",
)
dwc_page = st.Page(render_dwc_entry_page, title="DWC", url_path="dwc")
wwc_page = st.Page(render_wwc_page, title="WWC", url_path="wwc")
rural_page = st.Page(render_rural_page, title="Rural", url_path="rural")

pg = st.navigation(
    {
        "Home": [summary_page],
        "Operations": [dwc_page, wwc_page, rural_page],
    }
)
pg.run()
