import streamlit as st
from spider_chart import group_taste_profile

def render(back_button):
    back_button()

    # Ensure answers exist
    if "answers" not in st.session_state or not st.session_state["answers"]:
        st.error("Please complete the questionnaire first.")
        return

    group_taste_profile(st.session_state["answers"])
