# app.py

import streamlit as st

from core.auth import get_current_user, get_user_role, logout_user
from modules.summary.page import render_summary_page
from modules.dwc.page import render_dwc_entry_page
from modules.wwc.page import render_wwc_page
from modules.rural.page import render_rural_page

st.set_page_config(page_title="Recovery Dashboard", layout="wide")

# ── Session state defaults ──────────────────────────────────────────────────
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
if "role" not in st.session_state:
    st.session_state["role"] = None
if "username" not in st.session_state:
    st.session_state["username"] = None

# ── Resolve current user (only if not already in session) ──────────────────
if not st.session_state["authenticated"]:
    user = get_current_user()
    role = get_user_role(user)
    if user and role:
        st.session_state["authenticated"] = True
        st.session_state["role"] = role
        st.session_state["username"] = getattr(user, "email", str(user))

role = st.session_state["role"]

# ── Sidebar: signed in as / sign out ───────────────────────────────────────
with st.sidebar:
    if st.session_state["authenticated"] and role == "admin":
        st.markdown(
            f"""
            <div style='padding: 0.5rem 0; border-bottom: 1px solid #e0e0e0; margin-bottom: 0.75rem;'>
                <small style='color: grey;'>Signed in as</small><br>
                <strong>{st.session_state['username']}</strong>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Sign out", key="signout_btn", use_container_width=True):
            logout_user()
            st.session_state["authenticated"] = False
            st.session_state["role"] = None
            st.session_state["username"] = None
            st.rerun()
    else:
        st.markdown(
            "<small style='color: grey;'>Viewing as public</small>",
            unsafe_allow_html=True,
        )

# ── Route ───────────────────────────────────────────────────────────────────
if role != "admin":
    # Public: summary only, no navigation chrome
    render_summary_page(public_view=True)
    st.stop()

# Admin: full navigation
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
