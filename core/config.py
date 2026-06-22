# core/config.py

import streamlit as st


def _secret(key: str, default: str = "") -> str:
    """Safely read a Streamlit secret by key."""
    try:
        return st.secrets[key]
    except (KeyError, FileNotFoundError):
        return default


# Admin access — comma-separated emails in secrets
_admin_raw = _secret("ADMIN_EMAILS", "")
ADMIN_EMAILS = set(e.strip() for e in _admin_raw.split(",") if e.strip())

GOOGLE_CLIENT_ID     = _secret("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = _secret("GOOGLE_CLIENT_SECRET")
APP_URL              = _secret("APP_URL", "http://localhost:8501")

DEV_MODE       = False
DEV_USER_EMAIL = ""
