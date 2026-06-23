import streamlit as st
import json
import time
from google.oauth2.service_account import Credentials
from google_auth_oauthlib.flow import Flow
from core.config import ADMIN_EMAILS, GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET


def _get_redirect_uri() -> str:
    """Get redirect URI from secrets."""
    try:
        return st.secrets.get("redirect_uri", "https://ccdata.streamlit.app/oauth2callback").strip()
    except:
        return "https://ccdata.streamlit.app/oauth2callback"


def _decode_id_token(token: str) -> dict:
    """Decode JWT without verification."""
    try:
        import base64
        payload = token.split(".")[1]
        payload += "=" * (-len(payload) % 4)
        return json.loads(base64.b64decode(payload))
    except:
        return {}


def init_session_auth():
    """Initialize session state."""
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
    """Validate and refresh token if needed."""
    if not st.session_state.get("authenticated"):
        return True
    
    token = st.session_state.get("token")
    if not token or "id_token" not in token:
        st.session_state["authenticated"] = False
        return False
    
    return True


def render_login_button() -> bool:
    """Render Google login button and handle callback."""
    if st.session_state.get("authenticated"):
        return False

    if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
        st.error("OAuth credentials not configured in secrets.")
        return False

    redirect_uri = _get_redirect_uri()

    # Create OAuth flow
    flow = Flow.from_client_config(
        {
            "installed": {
                "client_id": GOOGLE_CLIENT_ID,
                "client_secret": GOOGLE_CLIENT_SECRET,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [redirect_uri],
            }
        },
        scopes=["openid", "email", "profile"],
        redirect_uri=redirect_uri,
    )

    auth_url, state = flow.authorization_url(
        access_type="online",
        prompt="select_account",
    )

    # Store state for validation
    st.session_state["oauth_state"] = state

    # Show login button
    st.markdown(
        f'<a href="{auth_url}" target="_self"><button style="width:100%; padding:0.5rem; background-color:#1f77b4; color:white; border:none; border-radius:4px; font-size:16px; cursor:pointer;">Sign in with Google</button></a>',
        unsafe_allow_html=True,
    )

    # Handle OAuth callback
    query_params = st.query_params
    
    if "code" in query_params:
        code = query_params["code"]
        state_param = query_params.get("state", "")

        if state_param == st.session_state.get("oauth_state"):
            try:
                # Exchange code for token
                flow.fetch_token(code=code)
                credentials = flow.credentials

                # Decode ID token to get user info
                userinfo = _decode_id_token(credentials.id_token)
                email = userinfo.get("email", "")
                name = userinfo.get("name", "Guest")

                # Set session state
                st.session_state["authenticated"] = True
                st.session_state["username"] = email
                st.session_state["display_name"] = name
                st.session_state["role"] = "admin" if email in ADMIN_EMAILS else "public"
                st.session_state["token"] = {
                    "id_token": credentials.id_token,
                    "access_token": credentials.token,
                }
                st.session_state["token_time"] = time.time()

                # Clear query params
                st.query_params.clear()
                st.rerun()
                return True

            except Exception as e:
                st.error(f"Login failed: {str(e)}")
                st.write(f"Error details: {e}")

    return False


def logout_user():
    """Clear authentication state."""
    st.session_state["authenticated"] = False
    st.session_state["role"] = "public"
    st.session_state["username"] = None
    st.session_state["display_name"] = None
    st.session_state["token"] = None
    st.session_state["token_time"] = None


def get_user_role() -> str:
    """Get current user role."""
    return st.session_state.get("role", "public")
