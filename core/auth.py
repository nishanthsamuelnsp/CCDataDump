import streamlit as st
import json
import time
import base64
import requests
from urllib.parse import urlencode
from core.config import ADMIN_EMAILS, GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET


AUTHORIZE_URL = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_URL = "https://oauth2.googleapis.com/token"


def _get_redirect_uri() -> str:
    try:
        return st.secrets.get("redirect_uri", "https://ccdata.streamlit.app/oauth2callback").strip()
    except:
        return "https://ccdata.streamlit.app/oauth2callback"


def _decode_id_token(token: str) -> dict:
    try:
        payload = token.split(".")[1]
        payload += "=" * (-len(payload) % 4)
        return json.loads(base64.b64decode(payload))
    except:
        return {}


def init_session_auth():
    defaults = {
        "authenticated": False,
        "role": "public",
        "username": None,
        "display_name": None,
        "token": None,
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


def validate_session():
    if not st.session_state.get("authenticated"):
        return True
    return True


def render_login_button() -> bool:
    """Render login button and handle OAuth callback."""
    if st.session_state.get("authenticated"):
        return False

    if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
        st.error("OAuth not configured.")
        return False

    redirect_uri = _get_redirect_uri()

    # Build OAuth URL (NO fancy libraries, just basic params)
    auth_params = {
        "client_id": GOOGLE_CLIENT_ID,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "online",
    }
    auth_url = f"{AUTHORIZE_URL}?{urlencode(auth_params)}"

    # Render button
    st.markdown(
        f'<a href="{auth_url}" target="_self"><button style="width:100%; padding:0.5rem; background:#1f77b4; color:white; border:none; border-radius:4px; cursor:pointer;">Sign in with Google</button></a>',
        unsafe_allow_html=True,
    )

    # Handle callback
    query_params = st.query_params
    if "code" in query_params:
        code = query_params["code"]
        
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
                userinfo = _decode_id_token(token_data.get("id_token", ""))
                email = userinfo.get("email", "")
                name = userinfo.get("name", "Guest")

                st.session_state["authenticated"] = True
                st.session_state["username"] = email
                st.session_state["display_name"] = name
                st.session_state["role"] = "admin" if email in ADMIN_EMAILS else "public"
                st.session_state["token"] = token_data

                st.query_params.clear()
                st.rerun()
                return True
            else:
                st.error(f"Token exchange failed: {token_response.status_code}")
                st.write(f"Error: {token_response.text}")
        except Exception as e:
            st.error(f"Login error: {str(e)}")

    return False


def logout_user():
    st.session_state["authenticated"] = False
    st.session_state["role"] = "public"
    st.session_state["username"] = None
    st.session_state["display_name"] = None
    st.session_state["token"] = None


def get_user_role() -> str:
    return st.session_state.get("role", "public")
