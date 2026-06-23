# core/auth.py

import streamlit as st
from authlib.integrations.requests_client import OAuth2Session

from core.config import ADMIN_EMAILS, GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, APP_URL

AUTHORIZATION_ENDPOINT = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_ENDPOINT         = "https://oauth2.googleapis.com/token"
USERINFO_ENDPOINT      = "https://www.googleapis.com/oauth2/v3/userinfo"
SCOPE                  = "openid email profile"
REDIRECT_URI           = f"{APP_URL}/oauth2callback"


def _make_oauth_session():
    return OAuth2Session(
        client_id=GOOGLE_CLIENT_ID,
        client_secret=GOOGLE_CLIENT_SECRET,
        redirect_uri=REDIRECT_URI,
        scope=SCOPE,
    )


def init_session_auth():
    """Set session state defaults. Call once at top of app.py."""
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


def get_authorization_url():
    if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
        st.error(
            "⚠️ OAuth not configured. "
            "Set GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, and APP_URL in Streamlit secrets."
        )
        st.stop()

    oauth = _make_oauth_session()
    uri, state = oauth.create_authorization_url(
        AUTHORIZATION_ENDPOINT,
        access_type="online",
        prompt="select_account",
    )
    st.session_state["oauth_state"] = state
    return uri


def handle_oauth_callback():
    """
    Call on every page load. Exchanges OAuth code for user info.
    Returns True if a new login just completed.
    Does NOT call st.rerun() — caller decides.
    """
    params = st.query_params.to_dict()

    if "code" not in params:
        return False

    code = params["code"]

    # Already processed this code
    if st.session_state.get("_processed_code") == code:
        st.query_params.clear()
        return False

    # Already authenticated — clear stale params and move on
    if st.session_state.get("authenticated"):
        st.query_params.clear()
        return False

    try:
        oauth = _make_oauth_session()
        oauth.fetch_token(
            TOKEN_ENDPOINT,
            code=code,
            authorization_response=f"{REDIRECT_URI}?code={code}",
        )
        resp = oauth.get(USERINFO_ENDPOINT)
        userinfo = resp.json()

        email = userinfo.get("email", "")
        name  = userinfo.get("name", "Guest")

        st.session_state["authenticated"]  = True
        st.session_state["username"]       = email
        st.session_state["display_name"]   = name
        st.session_state["role"]           = "admin" if email in ADMIN_EMAILS else "public"
        st.session_state["_processed_code"] = code

        st.query_params.clear()
        return True

    except Exception as e:
        st.session_state["oauth_error"] = str(e)
        st.query_params.clear()
        return False


def logout_user():
    """Clear auth state. Call st.rerun() after."""
    for key in ["authenticated", "role", "username", "display_name",
                "oauth_state", "_processed_code", "oauth_error"]:
        st.session_state[key] = None
    st.session_state["authenticated"] = False
    st.session_state["role"] = "public"


def get_current_user():
    if st.session_state.get("authenticated"):
        return {
            "email": st.session_state.get("username"),
            "name":  st.session_state.get("display_name"),
        }
    return None


def get_user_role(user=None):
    return st.session_state.get("role", "public")
