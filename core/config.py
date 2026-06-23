import os
import streamlit as st


def _secret(key: str, default: str = "") -> str:
    try:
        val = st.secrets[key]
        if val is not None:
            result = str(val).strip()
            print(f"[CONFIG] {key} loaded from st.secrets: length={len(result)}")
            return result
    except (KeyError, AttributeError, FileNotFoundError) as e:
        print(f"[CONFIG] {key} NOT in st.secrets: {e}")
    
    result = str(os.environ.get(key, default)).strip()
    print(f"[CONFIG] {key} from os.environ: length={len(result) if result else 0}")
    return result


def _secret_emails(key: str) -> set:
    try:
        val = st.secrets[key]
        if isinstance(val, (list, tuple)):
            result = set(e.strip() for e in val if str(e).strip())
            print(f"[CONFIG] {key} loaded from st.secrets (list): {len(result)} emails")
            return result
        result = set(e.strip() for e in str(val).split(",") if e.strip())
        print(f"[CONFIG] {key} loaded from st.secrets (string): {len(result)} emails")
        return result
    except (KeyError, AttributeError, FileNotFoundError) as e:
        print(f"[CONFIG] {key} NOT in st.secrets: {e}")
    
    raw = os.environ.get(key, "")
    result = set(e.strip() for e in raw.split(",") if e.strip())
    print(f"[CONFIG] {key} from os.environ: {len(result)} emails")
    return result


print("[CONFIG] Starting configuration load...")
ADMIN_EMAILS = _secret_emails("ADMIN_EMAILS")
GOOGLE_CLIENT_ID = _secret("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = _secret("GOOGLE_CLIENT_SECRET")
print("[CONFIG] Configuration loaded complete")
print(f"[CONFIG] ADMIN_EMAILS = {ADMIN_EMAILS}")
print(f"[CONFIG] GOOGLE_CLIENT_ID length = {len(GOOGLE_CLIENT_ID)}")
print(f"[CONFIG] GOOGLE_CLIENT_SECRET length = {len(GOOGLE_CLIENT_SECRET)}")
