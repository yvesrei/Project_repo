import streamlit as st

def init_session():
    # Number of participants
    if "num_of_participants" not in st.session_state:
        st.session_state["num_of_participants"] = None

    # Current participant index
    if "current_participant" not in st.session_state:
        st.session_state["current_participant"] = 1

    # Answers list
    if "answers" not in st.session_state:
        st.session_state["answers"] = []

    # Taste profile results
    if "group_budget_numeric" not in st.session_state:
        st.session_state["group_budget_numeric"] = None

    if "group_cuisine" not in st.session_state:
        st.session_state["group_cuisine"] = None
