# core/config.py

import streamlit as st

# Admin access list
ADMIN_EMAILS = set(st.secrets.get("ADMIN_EMAILS", "").split(","))

# Google OAuth credentials — set in .streamlit/secrets.toml
GOOGLE_CLIENT_ID = st.secrets.get("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = st.secrets.get("GOOGLE_CLIENT_SECRET", "")

# Your deployed app URL (no trailing slash)
# e.g. https://ccdata.streamlit.app
APP_URL = st.secrets.get("APP_URL", "http://localhost:8501")

# DEV_MODE: set to false now, real OAuth is used
DEV_MODE = False
DEV_USER_EMAIL = ""
