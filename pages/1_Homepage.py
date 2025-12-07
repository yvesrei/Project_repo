# This file is stored in the pages directory
# Streamlit loads it automatically as an independent page

# This file is stored in the pages directory
# Streamlit loads it automatically as an independent page

import streamlit as st
from session_init import init_session
from Show_homepage import show_homepage


# --- 1) Make sure the base session keys exist (like before) ---
init_session()


# --- 2) Setup a small state flag for the confirmation step ---
if "confirm_reset" not in st.session_state:
    st.session_state["confirm_reset"] = False


st.title("🏠 Home")


# --- 3) If user has clicked reset: show confirmation dialog ---
if st.session_state["confirm_reset"]:
    st.warning(
        "⚠️ This will reset **the entire FoodMingle session**:\n"
        "- All participant answers\n"
        "- Group results\n"
        "- Questionnaire progress\n"
        "- Selected cuisines\n"
        "- API results\n\n"
        "Do you really want to continue?"
    )

    col1, col2 = st.columns(2)

    with col1:
        if st.button("❌ Cancel"):
            # Just cancel and go back to normal homepage view
            st.session_state["confirm_reset"] = False
            st.rerun()

    with col2:
        if st.button("✔️ Yes, reset everything"):
            # Clear everything, re-init, and reload this page clean
            st.session_state.clear()
            init_session()
            st.session_state["confirm_reset"] = False
            st.rerun()

else:
    # --- 4) Normal view: show info + reset button ---
    st.info(
        "You are on the **Home** page.\n\n"
        "If you click **Reset FoodMingle**, the current session will be erased "
        "and you will start again from the beginning."
    )

    if st.button("🔄 Reset FoodMingle"):
        st.session_state["confirm_reset"] = True
        st.rerun()


# --- 5) Finally, show the normal homepage content (logo, intro, etc.) ---
show_homepage()
