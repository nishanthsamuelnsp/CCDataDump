import os
import streamlit as st


def _secret(key: str, default: str = "") -> str:
    try:
        return str(st.secrets[key]).strip()
    except Exception:
        return str(os.getenv(key, default)).strip()


def _secret_emails(key: str) -> set[str]:
    try:
        value = st.secrets[key]

        if isinstance(value, (list, tuple)):
            return {
                str(x).strip().lower()
                for x in value
                if str(x).strip()
            }

        return {
            x.strip().lower()
            for x in str(value).split(",")
            if x.strip()
        }

    except Exception:
        raw = os.getenv(key, "")

        return {
            x.strip().lower()
            for x in raw.split(",")
            if x.strip()
        }


ADMIN_EMAILS = _secret_emails("ADMIN_EMAILS")
APP_URL = _secret("APP_URL")
