import streamlit as st

from core.auth import (
    init_session_auth,
    render_login_button,
    logout_user,
    get_user_role,
)

from modules.summary.page import render_summary_page
from modules.dwc.page import render_dwc_entry_page
from modules.wwc.page import render_wwc_page
from modules.rural.page import render_rural_page

st.set_page_config(
    page_title="Recovery Dashboard",
    layout="wide"
)

# Bootstrap
init_session_auth()

authenticated = st.user.is_logged_in
role = get_user_role()

# Sidebar
with st.sidebar:

    if authenticated:

        try:
            name = (
                st.user.get("name")
                or st.user.get("email")
                or "User"
            )
        except Exception:
            name = "User"

        badge_color = "#2e7d32" if role == "admin" else "grey"
        badge_label = (
            "● Admin access"
            if role == "admin"
            else "● Public access"
        )

        st.markdown(
            f"""
            <div style='padding:0.5rem 0 0.75rem 0;
                        border-bottom:1px solid rgba(49,51,63,0.2);
                        margin-bottom:0.75rem;'>

                <div style='font-size:0.72rem;
                            color:grey;
                            margin-bottom:3px;'>
                    Signed in as
                </div>

                <div style='font-weight:600;
                            font-size:0.88rem;
                            word-break:break-all;'>
                    {name}
                </div>

                <div style='font-size:0.72rem;
                            color:{badge_color};
                            margin-top:3px;'>
                    {badge_label}
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button(
            "Sign out",
            width="stretch",
            
        ):
            
            st.logout()

    else:

        st.markdown(
            "<div style='font-size:0.78rem; color:grey; margin-bottom:0.5rem;'>"
            "Sign in for admin access"
            "</div>",
            unsafe_allow_html=True,
        )

        render_login_button()

# Navigation
summary_page = st.Page(
    lambda: render_summary_page(
        public_view=(role != "admin")
    ),
    title="Summary",
    url_path="summary",
)

if role == "admin":

    dwc_page = st.Page(
        render_dwc_entry_page,
        title="DWC",
        url_path="dwc",
    )

    wwc_page = st.Page(
        render_wwc_page,
        title="WWC",
        url_path="wwc",
    )

    rural_page = st.Page(
        render_rural_page,
        title="Rural",
        url_path="rural",
    )

    nav = {
        "Home": [summary_page],
        "Operations": [
            dwc_page,
            wwc_page,
            rural_page,
        ],
    }

else:

    nav = {
        "Home": [summary_page]
    }

pg = st.navigation(nav)
pg.run()
