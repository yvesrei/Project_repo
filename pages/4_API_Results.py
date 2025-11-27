import streamlit as st
from session_init import init_session
init_session()

from app import show_api_results

st.button("⬅️ Back to result", on_click=lambda: st.switch_page("pages/3_Result.py"))

# Now show API results safely
show_api_results()

