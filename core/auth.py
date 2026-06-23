import streamlit as st

from core.config import ADMIN_EMAILS


def init_session_auth():
    pass


def get_user_role() -> str:

    if not st.user.is_logged_in:
        return "public"

    email = str(
        st.user.get("email", "")
    ).lower()

    return (
        "admin"
        if email in ADMIN_EMAILS
        else "public"
    )


def render_login_button() -> bool:

    if not st.user.is_logged_in:
        if st.button(
            "Sign in with Google",
            width="stretch"
        ):
            st.login()

        return False

    return True


def logout_user():

    st.logout()
