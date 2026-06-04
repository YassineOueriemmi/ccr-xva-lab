"""app.py — CCR & XVA Lab navigation controller"""
from utils.ui import inject_css
import streamlit as st
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))


st.set_page_config(
    page_title="CCR & XVA Lab",
    page_icon="▌",
    layout="wide",
)
inject_css()

pg = st.navigation([
    st.Page("pages/00_Home.py",
            title="00  HOME",                   default=True),
    st.Page("pages/01_Counterparty_Portfolio.py",
            title="01  COUNTERPARTY PORTFOLIO"),
    st.Page("pages/02_XVA_Metrics.py",             title="02  XVA METRICS"),
    st.Page("pages/03_CVA_VaR_Stress.py",          title="03  CVA RISK & VAR"),
    st.Page("pages/04_Methodology.py",             title="04  METHODOLOGY"),
])
pg.run()
