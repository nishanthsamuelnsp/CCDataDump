import os
import streamlit as st


def _secret(key: str, default: str = "") -> str:
    try:
        val = st.secrets[key]
        if val is not None:
            return str(val).strip()
    except (KeyError, AttributeError, FileNotFoundError):
        pass
    return str(os.environ.get(key, default)).strip()


def _secret_emails(key: str) -> set:
    try:
        val = st.secrets[key]
        if isinstance(val, (list, tuple)):
            return set(e.strip() for e in val if str(e).strip())
        return set(e.strip() for e in str(val).split(",") if e.strip())
    except (KeyError, AttributeError, FileNotFoundError):
        pass
    raw = os.environ.get(key, "")
    return set(e.strip() for e in raw.split(",") if e.strip())


ADMIN_EMAILS = _secret_emails("ADMIN_EMAILS")
GOOGLE_CLIENT_ID = _secret("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = _secret("GOOGLE_CLIENT_SECRET")
REDIRECT_URI = _secret("redirect_uri", "https://ccdata.streamlit.app/oauth2callback")
APP_URL = _secret("APP_URL", "https://ccdata.streamlit.app")
