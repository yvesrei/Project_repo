import streamlit as st
from session_init import init_session
init_session()

from Questionnaire import show_questionnaire

# Optional back button
st.button("⬅️ Back to homepage", on_click=lambda: st.switch_page("pages/1_Homepage.py"))

show_questionnaire()
