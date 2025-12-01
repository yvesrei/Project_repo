# This file is stored in the pages directory
# Streamlit loads it automatically as an independent page

import streamlit as st
from session_init import init_session
init_session()

from spider_chart import group_taste_profile

# This is a button to return to the questionnaire page file
# We use "switch_page()"" because this page bypasses the router implemented in app.py (st.session_state)
st.button("⬅️ Back to questionnaire", on_click=lambda: st.switch_page("pages/2_Questionnaire.py"))

# Ensure that answers exist
if not st.session_state["answers"]:
    st.error("Please complete the questionnaire first.")
else:
    group_taste_profile(st.session_state["answers"])
