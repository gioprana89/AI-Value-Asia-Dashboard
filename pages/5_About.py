
import streamlit as st
from utils.styles import apply_style, header, footer, AUTHORS

st.set_page_config(page_title="About | Bloomberg AI Dashboard", page_icon="ℹ️", layout="wide")
apply_style()
header(
    "About the Dashboard",
    "Research dashboard for exploring AI thematic exposure, ESG information and financial data for Asian listed firms."
)

st.markdown("### Design and development")
st.write(AUTHORS)

st.markdown("### Current release")
st.write(
    "Version 1 focuses on Executive Overview, AI Landscape and Data Quality. "
    "Financial-resilience, firm-value, moderation and moderated-mediation pages should only be activated "
    "after Bloomberg financial histories are collected for the AI-theme companies and the datasets overlap."
)

st.markdown("### Data-source principle")
st.write(
    "The project is intentionally designed around Bloomberg Terminal and Bloomberg Intelligence data. "
    "Raw Bloomberg assessments remain available, while any transformed dashboard metric is explicitly documented."
)

footer()
