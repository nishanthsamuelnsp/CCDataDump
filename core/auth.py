# core/auth.py

import urllib.parse
import streamlit as st
from authlib.integrations.requests_client import OAuth2Session

from core.config import ADMIN_EMAILS, GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, APP_URL

AUTHORIZATION_ENDPOINT = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_ENDPOINT = "https://oauth2.googleapis.com/token"
USERINFO_ENDPOINT = "https://www.googleapis.com/oauth2/v3/userinfo"
SCOPE = "openid email profile"
REDIRECT_URI = f"{APP_URL}/oauth2callback"


def _make_oauth_session():
    return OAuth2Session(
        client_id=GOOGLE_CLIENT_ID,
        client_secret=GOOGLE_CLIENT_SECRET,
        redirect_uri=REDIRECT_URI,
        scope=SCOPE,
    )


def get_authorization_url():
    oauth = _make_oauth_session()
    uri, state = oauth.create_authorization_url(
        AUTHORIZATION_ENDPOINT,
        access_type="online",
    )
    st.session_state["oauth_state"] = state
    return uri


def handle_oauth_callback():
    """
    Call this on every page load. If query params contain 'code',
    exchange it for a token and populate session state.
    Returns True if a new login just completed.
    """
    params = st.query_params
    if "code" not in params:
        return False

    code = params["code"]
    state = params.get("state", "")

    # Avoid re-processing the same code
    if st.session_state.get("_processed_code") == code:
        return False

    try:
        oauth = _make_oauth_session()
        # authlib state check — pass stored state
        stored_state = st.session_state.get("oauth_state", state)
        token = oauth.fetch_token(
            TOKEN_ENDPOINT,
            code=code,
            state=stored_state,
        )
        resp = oauth.get(USERINFO_ENDPOINT)
        userinfo = resp.json()

        email = userinfo.get("email", "")
        name = userinfo.get("name", "Guest")

        st.session_state["authenticated"] = True
        st.session_state["username"] = email
        st.session_state["display_name"] = name
        st.session_state["role"] = "admin" if email in ADMIN_EMAILS else "public"
        st.session_state["_processed_code"] = code

        # Clean up URL
        st.query_params.clear()
        return True

    except Exception as e:
        st.session_state["oauth_error"] = str(e)
        st.query_params.clear()
        return False


def init_session_auth():
    """Set defaults. Call once at the top of app.py."""
    defaults = {
        "authenticated": False,
        "role": "public",
        "username": None,
        "display_name": None,
        "oauth_state": None,
        "_processed_code": None,
        "oauth_error": None,
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


def logout_user():
    """Clear auth state. Call st.rerun() after."""
    for key in ["authenticated", "role", "username", "display_name", "oauth_state", "_processed_code"]:
        st.session_state[key] = None
    st.session_state["authenticated"] = False
    st.session_state["role"] = "public"


def get_current_user():
    if st.session_state.get("authenticated"):
        return {
            "email": st.session_state.get("username"),
            "name": st.session_state.get("display_name"),
        }
    return None


def get_user_role(user=None):
    return st.session_state.get("role", "public")
