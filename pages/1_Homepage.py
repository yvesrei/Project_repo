# This file is stored in the pages directory
# Streamlit loads it automatically as an independent pagr
# Clicking "Home" in the Streamlit sidebar opens this page.
# Its only purpose is to reset the current FoodMingle session and
# redirect the user back to the main homepage in app.py.


import streamlit as st
import time

# Implemented a short explanation to inform the user that they clicked onto the homepage,
# which will reset the whole session and that they will get redirected to the home page.
st.title(" Resetting Session...")

st.info(
    "You clicked on Home, which will start a new FoodMingle session \n\n"
    "All previous answers and results will be cleared."
)

# Implemented a 5 second pause so that the user is able to read the information.
time.sleep(5)

# Immediately reset all session state = clear all answers.
st.session_state.clear()

# Sets the session back to home.
st.session_state["page"] = "home"

# Redirect the user back to the main application.
# This ensures that all interactions happen inside the central app flow.
st.switch_page("app.py")
