import streamlit as st

from core.auth import get_current_user, get_user_role
from modules.summary.page import render_summary_page
from modules.dwc.page import render_dwc_page
from modules.wwc.page import render_wwc_page
from modules.rural.page import render_rural_page


st.set_page_config(page_title="Recovery Dashboard", layout="wide")

user = get_current_user()
role = get_user_role(user)

if role == "public":
    render_summary_page(public_view=True)
    st.stop()

summary_page = st.Page(lambda: render_summary_page(public_view=False), title="Summary", url_path="summary")
dwc_page = st.Page(render_dwc_page, title="DWC", url_path="dwc")
wwc_page = st.Page(render_wwc_page, title="WWC", url_path="wwc")
rural_page = st.Page(render_rural_page, title="Rural", url_path="rural")

pg = st.navigation(
    {
        "Home": [summary_page],
        "Operations": [dwc_page, wwc_page, rural_page],
    }
)
pg.run()
