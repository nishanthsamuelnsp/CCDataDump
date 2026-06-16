import streamlit as st
from shared.charts import placeholder_chart

def render_rural_page():
    st.title("RURAL Module")
    tab1, tab2, tab3 = st.tabs(["Entry", "Analytics", "Variables"])

    with tab1:
        st.subheader("Data Entry")
        st.write("Add forms for workman data, waste delivery, segregation, despatch, and more.")

    with tab2:
        st.subheader("Analytics")
        placeholder_chart("KPI overview")
        placeholder_chart("Confounding variables")
        placeholder_chart("Intervening variables")

    with tab3:
        st.subheader("Variables Mapping")
        st.write("Map uploaded column headers to internal standard field names.")
