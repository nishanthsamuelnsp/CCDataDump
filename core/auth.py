# core/auth.py

import base64
import json
import streamlit as st
from streamlit_oauth import OAuth2Component

from core.config import ADMIN_EMAILS, GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET

AUTHORIZE_URL = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_URL     = "https://oauth2.googleapis.com/token"
REVOKE_URL    = "https://oauth2.googleapis.com/revoke"
SCOPE         = "openid email profile"
REDIRECT_URI  = "https://ccdata.streamlit.app/oauth2callback"


def _decode_id_token(token: str) -> dict:
    """Decode JWT payload without signature verification."""
    payload = token.split(".")[1]
    payload += "=" * (-len(payload) % 4)
    return json.loads(base64.b64decode(payload))


def init_session_auth():
    """Set session state defaults. Call once at top of app.py."""
    defaults = {
        "authenticated": False,
        "role":          "public",
        "username":      None,
        "display_name":  None,
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


def render_login_button() -> bool:
    """
    Renders the Google OAuth button in the current context.
    Populates session state on success.
    Returns True if login just completed.
    """
    if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
        st.error(
            "OAuth not configured — check GOOGLE_CLIENT_ID and "
            "GOOGLE_CLIENT_SECRET in Streamlit secrets."
        )
        return False

    oauth2 = OAuth2Component(
        client_id=GOOGLE_CLIENT_ID,
        client_secret=GOOGLE_CLIENT_SECRET,
        authorize_endpoint=AUTHORIZE_URL,
        token_endpoint=TOKEN_URL,
        refresh_token_endpoint=TOKEN_URL,
        revoke_token_endpoint=REVOKE_URL,
    )

    result = oauth2.authorize_button(
        name="Sign in with Google",
        redirect_uri=REDIRECT_URI,
        scope=SCOPE,
        key="google_oauth_btn",
        extras_params={"prompt": "select_account", "access_type": "online"},
        use_container_width=True,
        icon="https://www.google.com/favicon.ico",
    )

    if result and "token" in result:
        try:
            userinfo = _decode_id_token(result["token"]["id_token"])
            email = userinfo.get("email", "")
            name  = userinfo.get("name", "Guest")

            st.session_state["authenticated"] = True
            st.session_state["username"]      = email
            st.session_state["display_name"]  = name
            st.session_state["role"]          = "admin" if email in ADMIN_EMAILS else "public"
            return True
        except Exception as e:
            st.error(f"Login error: {e}")

    return True


def logout_user():
    """Clear auth state. Call st.rerun() after."""
    st.session_state["authenticated"] = False
    st.session_state["role"]          = "public"
    st.session_state["username"]      = None
    st.session_state["display_name"]  = None


def get_user_role() -> str:
    return st.session_state.get("role", "public")
