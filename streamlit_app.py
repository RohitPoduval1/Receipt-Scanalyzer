"""
The homepage for the Receipt Scanalyzer app. Connects both scanner.py and analyzer.py and allow
for usage of both through the sidebar.
"""
import streamlit as st

scanner = st.Page("pages/scanner.py", title="Receipt Scanner")
analyzer = st.Page("pages/analyzer.py", title="Receipt Analyzer")

pg = st.navigation([scanner, analyzer])
st.set_page_config(page_title="Receipt Scanalyzer")
pg.run()
