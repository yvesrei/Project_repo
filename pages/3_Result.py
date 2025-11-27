import streamlit as st
from session_init import init_session
init_session()

from spider_chart import group_taste_profile

st.button("⬅️ Back to questionnaire", on_click=lambda: st.switch_page("pages/2_Questionnaire.py"))

# Ensure answers exist
if not st.session_state["answers"]:
    st.error("Please complete the questionnaire first.")
else:
    group_taste_profile(st.session_state["answers"])
