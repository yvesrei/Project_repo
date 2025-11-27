import streamlit as st
from spider_chart import group_taste_profile

st.button("⬅️ Back", on_click=lambda: st.session_state.pop("nav_history", None))

if "answers" not in st.session_state or not st.session_state["answers"]:
    st.error("Please complete the questionnaire first.")
else:
    group_taste_profile(st.session_state["answers"])

