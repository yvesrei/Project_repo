# This file is stored in the pages directory
# Streamlit loads it automatically as an independent page

import streamlit as st

# Immediately reset all session state
st.session_state.clear()

# Set page=home for your app router
st.session_state["page"] = "home"

# Redirect to main app immediately
st.switch_page("app.py")
