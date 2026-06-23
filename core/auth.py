import base64
import json
import time
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
    try:
        payload = token.split(".")[1]
        payload += "=" * (-len(payload) % 4)
        return json.loads(base64.b64decode(payload))
    except Exception:
        return {}


def _is_token_expired(id_token: str) -> bool:
    """Check if JWT token is expired."""
    decoded = _decode_id_token(id_token)
    if not decoded or "exp" not in decoded:
        return True
    return time.time() > decoded["exp"]


def _refresh_access_token(refresh_token: str) -> dict | None:
    """Attempt to refresh the access token using refresh_token."""
    try:
        import requests
        response = requests.post(
            TOKEN_URL,
            data={
                "client_id": GOOGLE_CLIENT_ID,
                "client_secret": GOOGLE_CLIENT_SECRET,
                "refresh_token": refresh_token,
                "grant_type": "refresh_token",
            },
            timeout=10,
        )
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        st.warning(f"Token refresh failed: {e}")
    return None


def _extract_userinfo(token_result: dict) -> dict:
    """Extract user info from token result."""
    try:
        userinfo = _decode_id_token(token_result.get("id_token", ""))
        return {
            "email": userinfo.get("email", ""),
            "name": userinfo.get("name", "Guest"),
        }
    except Exception:
        return {"email": "", "name": "Guest"}


def init_session_auth():
    """Set session state defaults. Call once at top of app.py."""
    defaults = {
        "authenticated": False,
        "role": "public",
        "username": None,
        "display_name": None,
        "token": None,  # Store full token object
        "token_time": None,  # Track when token was set
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


def validate_session():
    """
    Validate current session and refresh token if needed.
    Call this at the start of app.py after init_session_auth().
    Returns True if session is valid, False if user needs to re-authenticate.
    """
    if not st.session_state.get("authenticated"):
        return True  # Not authenticated is a valid state

    token = st.session_state.get("token")
    if not token or "id_token" not in token:
        st.session_state["authenticated"] = False
        return False

    # Check if token is expired
    if _is_token_expired(token.get("id_token", "")):
        refresh_token = token.get("refresh_token")
        if refresh_token:
            # Try to refresh
            new_token = _refresh_access_token(refresh_token)
            if new_token:
                st.session_state["token"] = new_token
                st.session_state["token_time"] = time.time()
                return True
        # Token expired and can't refresh
        st.session_state["authenticated"] = False
        return False

    return True


def render_login_button() -> bool:
    """
    Renders the Google OAuth button ONLY if not authenticated.
    Populates session state on success.
    Returns True if login just completed.
    """
    # Guard: Don't render if already authenticated
    if st.session_state.get("authenticated"):
        return False

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
            userinfo = _extract_userinfo(result["token"])
            email = userinfo["email"]
            name = userinfo["name"]

            # Store everything we need
            st.session_state["token"] = result["token"]
            st.session_state["token_time"] = time.time()
            st.session_state["authenticated"] = True
            st.session_state["username"] = email
            st.session_state["display_name"] = name
            st.session_state["role"] = "admin" if email in ADMIN_EMAILS else "public"

            return True

        except Exception as e:
            st.error(f"Login error: {e}")
            return False

    return False


def logout_user():
    """Clear auth state. Call st.rerun() after."""
    st.session_state["authenticated"] = False
    st.session_state["role"] = "public"
    st.session_state["username"] = None
    st.session_state["display_name"] = None
    st.session_state["token"] = None
    st.session_state["token_time"] = None


def get_user_role() -> str:
    return st.session_state.get("role", "public")
