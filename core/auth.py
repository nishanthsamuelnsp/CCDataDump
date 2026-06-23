import base64
import json
import time
import secrets
import streamlit as st
import requests
from urllib.parse import urlencode
from core.config import ADMIN_EMAILS, GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET

AUTHORIZE_URL = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_URL = "https://oauth2.googleapis.com/token"
SCOPE = "openid email profile"


def _get_redirect_uri() -> str:
    """Load redirect_uri from secrets."""
    try:
        uri = st.secrets.get("redirect_uri", "").strip()
        if uri:
            return uri
    except:
        pass
    return "https://ccdata.streamlit.app/oauth2callback"


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
        "token": None,
        "token_time": None,
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


def validate_session():
    """Validate current session and refresh token if needed."""
    if not st.session_state.get("authenticated"):
        return True

    token = st.session_state.get("token")
    if not token or "id_token" not in token:
        st.session_state["authenticated"] = False
        return False

    if _is_token_expired(token.get("id_token", "")):
        refresh_token = token.get("refresh_token")
        if refresh_token:
            new_token = _refresh_access_token(refresh_token)
            if new_token:
                st.session_state["token"] = new_token
                st.session_state["token_time"] = time.time()
                return True
        st.session_state["authenticated"] = False
        return False

    return True


def render_login_button() -> bool:
    """
    Render login UI with redirect link.
    Returns True if user just authenticated.
    """
    if st.session_state.get("authenticated"):
        return False

    if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
        st.error("OAuth not configured — check Streamlit secrets.")
        return False

    redirect_uri = _get_redirect_uri()
    
    # Generate state for CSRF protection
    if "oauth_state" not in st.session_state:
        st.session_state["oauth_state"] = secrets.token_urlsafe(32)
    
    state = st.session_state["oauth_state"]

    # Build OAuth authorization URL manually
    auth_params = {
        "client_id": GOOGLE_CLIENT_ID,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": SCOPE,
        "state": state,
        "prompt": "select_account",
        "access_type": "online",
    }
    
    auth_url = f"{AUTHORIZE_URL}?{urlencode(auth_params)}"

    # Render login button
    st.markdown(
        f'<a href="{auth_url}" target="_self"><button style="width:100%; padding:0.5rem; background-color:#1f77b4; color:white; border:none; border-radius:4px; font-size:16px; cursor:pointer;">Sign in with Google</button></a>',
        unsafe_allow_html=True,
    )

    # Handle callback
    query_params = st.query_params
    if "code" in query_params:
        code = query_params["code"]
        state_param = query_params.get("state", "")
        stored_state = st.session_state.get("oauth_state", "")

        if state_param == stored_state:
            try:
                # Exchange code for token
                token_response = requests.post(
                    TOKEN_URL,
                    data={
                        "client_id": GOOGLE_CLIENT_ID,
                        "client_secret": GOOGLE_CLIENT_SECRET,
                        "code": code,
                        "grant_type": "authorization_code",
                        "redirect_uri": redirect_uri,
                    },
                    timeout=10,
                )

                if token_response.status_code == 200:
                    token_data = token_response.json()
                    userinfo = _extract_userinfo(token_data)
                    email = userinfo["email"]
                    name = userinfo["name"]

                    st.session_state["token"] = token_data
                    st.session_state["token_time"] = time.time()
                    st.session_state["authenticated"] = True
                    st.session_state["username"] = email
                    st.session_state["display_name"] = name
                    st.session_state["role"] = "admin" if email in ADMIN_EMAILS else "public"

                    # Clear query params and rerun
                    st.query_params.clear()
                    st.rerun()
                    return True
                else:
                    st.error(f"Token exchange failed: {token_response.status_code}")
                    st.error(f"Response: {token_response.text}")
            except Exception as e:
                st.error(f"Login error: {e}")
        else:
            st.error("State mismatch - possible CSRF attack")

    return False


def logout_user():
    """Clear auth state."""
    st.session_state["authenticated"] = False
    st.session_state["role"] = "public"
    st.session_state["username"] = None
    st.session_state["display_name"] = None
    st.session_state["token"] = None
    st.session_state["token_time"] = None


def get_user_role() -> str:
    return st.session_state.get("role", "public")
