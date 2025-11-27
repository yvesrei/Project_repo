import streamlit as st

# Import the API results function from app.py
from app import show_api_results

def render(back_button):
    back_button()

    # Ensure required taste profile info exists
    if (
        "group_budget_numeric" not in st.session_state or
        "group_cuisine" not in st.session_state
    ):
        st.error("Please view the taste profile page first.")
        return

    show_api_results()
