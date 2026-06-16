import streamlit as st

st.set_page_config(page_title="Recovery Dashboard", layout="wide")

summary_page = st.Page("modules/summary/page.py", title="Summary", icon="🏠", default=True)
dwc_page = st.Page("modules/dwc/page.py", title="DWC", icon="📊")
wwc_page = st.Page("modules/wwc/page.py", title="WWC", icon="📈")
rural_page = st.Page("modules/rural/page.py", title="Rural", icon="🌾")


def login_screen():
    st.title("Recovery Dashboard")
    st.write("Please sign in with Google to continue.")
    if st.button("Sign in with Google"):
        st.login()
    st.stop()


if not st.user.is_logged_in:
    login_screen()

email = st.user.email
admin_emails = set(st.secrets["access"]["admin_emails"])
is_admin = email in admin_emails

with st.sidebar:
    st.caption(f"Signed in as: {email}")
    st.caption("Role: Admin" if is_admin else "Role: Public")
    if st.button("Log out"):
        st.logout()

if is_admin:
    pg = st.navigation(
        {
            "Home": [summary_page],
            "Operations": [dwc_page, wwc_page, rural_page],
        }
    )
else:
    pg = st.navigation(
        {
            "Home": [summary_page],
        }
    )

pg.run()
