# app.py

import streamlit as st

from core.auth import init_session_auth, handle_oauth_callback, get_authorization_url, logout_user
from modules.summary.page import render_summary_page
from modules.dwc.page import render_dwc_entry_page
from modules.wwc.page import render_wwc_page
from modules.rural.page import render_rural_page

st.set_page_config(page_title="Recovery Dashboard", layout="wide")

# ── Bootstrap + handle OAuth return ────────────────────────────────────────
init_session_auth()
just_logged_in = handle_oauth_callback()
if just_logged_in:
    st.rerun()

role = st.session_state["role"]
authenticated = st.session_state["authenticated"]

# ── Sidebar ─────────────────────────────────────────────────────────────────
with st.sidebar:
    if authenticated:
        name = st.session_state.get("display_name") or st.session_state.get("username")
        st.markdown(
            f"""
            <div style='padding:0.5rem 0 0.75rem 0; border-bottom:1px solid rgba(49,51,63,0.2); margin-bottom:0.75rem;'>
                <div style='font-size:0.72rem; color:grey; margin-bottom:3px;'>Signed in as</div>
                <div style='font-weight:600; font-size:0.88rem; word-break:break-all;'>{name}</div>
                {'<div style="font-size:0.72rem; color:#2e7d32; margin-top:3px;">● Admin access</div>' if role == "admin" else '<div style="font-size:0.72rem; color:grey; margin-top:3px;">Public access</div>'}
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Sign out", use_container_width=True, key="signout_btn"):
            logout_user()
            st.rerun()
    else:
        st.markdown(
            "<div style='font-size:0.78rem; color:grey; margin-bottom:0.75rem;'>Sign in for admin access</div>",
            unsafe_allow_html=True,
        )
        auth_url = get_authorization_url()
        st.link_button("Sign in with Google", auth_url, use_container_width=True)

    if st.session_state.get("oauth_error"):
        st.error(f"Login error: {st.session_state['oauth_error']}")

# ── Navigation ───────────────────────────────────────────────────────────────
summary_page = st.Page(
    lambda: render_summary_page(public_view=(role != "admin")),
    title="Summary",
    url_path="summary",
)

if role == "admin":
    dwc_page = st.Page(render_dwc_entry_page, title="DWC", url_path="dwc")
    wwc_page = st.Page(render_wwc_page, title="WWC", url_path="wwc")
    rural_page = st.Page(render_rural_page, title="Rural", url_path="rural")
    nav = {
        "Home": [summary_page],
        "Operations": [dwc_page, wwc_page, rural_page],
    }
else:
    nav = {"Home": [summary_page]}

pg = st.navigation(nav)
pg.run()
