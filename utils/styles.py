
import streamlit as st

AUTHORS = "Abdillah Arif Nasution, Aulia Arif Nasution & Prana Ugiana Gio"

def apply_style():
    st.markdown(
        """
        <style>
        .block-container {padding-top: 1.6rem; padding-bottom: 3rem; max-width: 1450px;}
        [data-testid="stSidebar"] {background: #101828;}
        [data-testid="stSidebar"] * {color: #F9FAFB;}
        .app-kicker {font-size: 0.86rem; color: #667085; letter-spacing: .08em; text-transform: uppercase;}
        .app-title {font-size: 2rem; font-weight: 760; color: #101828; margin-bottom: .15rem;}
        .app-subtitle {font-size: 1rem; color: #667085; margin-bottom: 1.2rem;}
        .credit {font-size: .82rem; color: #667085; margin-top: .25rem;}
        .notice {
            border: 1px solid #FEDF89; background: #FFFAEB; color: #7A2E0E;
            border-radius: 10px; padding: 12px 14px; margin: 8px 0 18px 0;
        }
        .footer {
            border-top: 1px solid #EAECF0; margin-top: 2.5rem; padding-top: 1rem;
            font-size: .8rem; color: #667085;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

def header(title, subtitle):
    st.markdown('<div class="app-kicker">Bloomberg Intelligence Research Dashboard</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="app-title">{title}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="app-subtitle">{subtitle}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="credit">Designed and developed by <b>{AUTHORS}</b></div>', unsafe_allow_html=True)

def footer():
    st.markdown(
        f'<div class="footer">Data source: Bloomberg Terminal & Bloomberg Intelligence. '
        f'Dashboard designed and developed by <b>{AUTHORS}</b>.</div>',
        unsafe_allow_html=True,
    )
