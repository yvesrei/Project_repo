# This file is stored in the pages directory
# Streamlit loads it automatically as an independent page

import streamlit as st
from session_init import init_session
init_session()

from About_us import show_about_us

# This is a button to return to the homepage page file
# We use "switch_page()"" because this page bypasses the router implemented in app.py (st.session_state)
st.button("⬅️ Back to homepage", on_click=lambda: st.switch_page("pages/1_Homepage.py"))

show_about_us()
