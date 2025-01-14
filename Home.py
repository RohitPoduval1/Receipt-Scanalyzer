"""
The homepage for the Receipt Scanalyzer app. Connects both scanner.py and analyzer.py and allow
for usage of both through the sidebar.
"""
import streamlit as st

st.set_page_config(
    page_title="Receipt Scanalyzer",     # what is shown in the browser tab
    page_icon=":material/receipt_long:"  # the favicon
)
st.title("Welcome to the Receipt Scanalyzer!")
st.write(
    """
    Upload a photo of your receipt and get a CSV with the data that could be extracted from the
    receipt (i.e. date, item name, price). This CSV can be used with the Receipt Analyzer to gain
    insight into monthly spending habits, most purchased items, and how healthy you're eating.
    """
)
