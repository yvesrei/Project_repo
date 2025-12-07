# This file is stored in the pages directory
# Streamlit loads it automatically as an independent page

import streamlit as st
import time

st.title(" Resetting Session...")

st.info(
    "You clicked Home, which will start a new FoodMingle session"
    "All previous answers and results will be cleared."
)

# Small pause so user notices the info
time.sleep(3)

# Immediately reset all session state
st.session_state.clear()

# Set page=home for your app router
st.session_state["page"] = "home"

# Redirect to main app immediately
st.switch_page("app.py")
