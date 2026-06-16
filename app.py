import streamlit as st
from core.auth import get_current_user, get_user_role
from core.navigation import render_navigation

st.set_page_config(page_title="Recovery Dashboard", layout="wide")

user = get_current_user()
role = get_user_role(user)
render_navigation(user=user, role=role)
