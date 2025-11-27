import streamlit as st
from Questionnaire import show_questionnaire

st.button("⬅️ Back", on_click=lambda: st.session_state.pop("nav_history", None))
show_questionnaire()

