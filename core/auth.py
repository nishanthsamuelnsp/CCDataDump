# core/auth.py

import streamlit as st
from core.config import ADMIN_EMAILS, DEV_MODE, DEV_USER_EMAIL


# ── Session bootstrap ────────────────────────────────────────────────────────
# Call this once at the top of app.py before any role checks.

def init_session_auth():
    """Initialize auth-related session state keys if not already set."""
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False
    if "role" not in st.session_state:
        st.session_state["role"] = None
    if "username" not in st.session_state:
        st.session_state["username"] = None

    # Auto-login for DEV_MODE — only runs once per session
    if DEV_MODE and not st.session_state["authenticated"]:
        user = {"email": DEV_USER_EMAIL, "name": "Dev User"}
        role = _resolve_role(user)
        st.session_state["authenticated"] = True
        st.session_state["role"] = role
        st.session_state["username"] = user["email"]


# ── User / role resolution ───────────────────────────────────────────────────

def get_current_user():
    """
    Returns the current user dict if authenticated, else None.
    In DEV_MODE, always returns the dev user.
    """
    if DEV_MODE:
        return {"email": DEV_USER_EMAIL, "name": "Dev User"}
    if st.session_state.get("authenticated"):
        return {"email": st.session_state.get("username"), "name": ""}
    return None


def get_user_role(user):
    """Derive role from user dict. Falls back to 'public'."""
    return _resolve_role(user)


def _resolve_role(user):
    email = (user or {}).get("email")
    return "admin" if email in ADMIN_EMAILS else "public"


# ── Logout ───────────────────────────────────────────────────────────────────

def logout_user():
    """
    Clears auth session state.
    In DEV_MODE, re-authenticates immediately on next rerun.
    Call st.rerun() after this.
    """
    st.session_state["authenticated"] = False
    st.session_state["role"] = None
    st.session_state["username"] = None
