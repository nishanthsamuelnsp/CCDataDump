import streamlit as st

st.title("🔐 Secrets Debug Test")

# Test 1: Check if secrets exist at all
st.subheader("Available secrets:")
if hasattr(st, 'secrets'):
    st.write(f"Keys: {list(st.secrets.keys())}")
else:
    st.error("st.secrets not available!")

# Test 2: Try to read each secret
st.subheader("Trying to read secrets:")
try:
    cid = st.secrets.get("GOOGLE_CLIENT_ID", "NOT FOUND")
    if cid == "NOT FOUND":
        st.error("❌ GOOGLE_CLIENT_ID not found in secrets!")
    else:
        st.success(f"✅ GOOGLE_CLIENT_ID found: {cid[:20]}...{cid[-10:]}")
except Exception as e:
    st.error(f"Error reading GOOGLE_CLIENT_ID: {e}")

try:
    csecret = st.secrets.get("GOOGLE_CLIENT_SECRET", "NOT FOUND")
    if csecret == "NOT FOUND":
        st.error("❌ GOOGLE_CLIENT_SECRET not found in secrets!")
    else:
        st.success(f"✅ GOOGLE_CLIENT_SECRET found: {csecret[:20]}...{csecret[-10:]}")
except Exception as e:
    st.error(f"Error reading GOOGLE_CLIENT_SECRET: {e}")

try:
    admins = st.secrets.get("ADMIN_EMAILS", "NOT FOUND")
    if admins == "NOT FOUND":
        st.warning("⚠️ ADMIN_EMAILS not found in secrets (optional)")
    else:
        st.success(f"✅ ADMIN_EMAILS found: {admins}")
except Exception as e:
    st.error(f"Error reading ADMIN_EMAILS: {e}")

# Test 3: Check environment variables as fallback
st.subheader("Checking environment variables:")
import os
st.write(f"OS env has GOOGLE_CLIENT_ID: {'GOOGLE_CLIENT_ID' in os.environ}")
st.write(f"OS env has GOOGLE_CLIENT_SECRET: {'GOOGLE_CLIENT_SECRET' in os.environ}")
