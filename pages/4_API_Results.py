# This file is stored in the pages directory
# Streamlit loads it automatically as an independent page

import streamlit as st
from session_init import init_session
init_session()

from app import show_api_results

# This is a button to return to the Result page file
# We use "switch_page()"" because this page bypasses the router implemented in app.py (st.session_state)
st.button("⬅️ Back to result", on_click=lambda: st.switch_page("pages/3_Result.py"))

# Now show API results safely
show_api_results()

