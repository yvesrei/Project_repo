# This is the main Streamlit app file
#  Defines the navigation system (home, questionnaire, result, API, about)
#  Manages session state (participants, answers, current page)


import streamlit as st
from Show_homepage import show_homepage
from Questionnaire import show_questionnaire
from spider_chart import group_taste_profile
from About_us import show_about_us
from Show_api_results import show_api_results

## 1. Session state initialization
# Streamlit reruns the script on every interaction. We use st.session_state
# to track values across reruns so we know:
# - which page the user is on,
# - how many participants there are,
# - which participant is currently answering the questionnaire,
# - and all collected answers so far.
# 
# St.session_state works like a dictionary. A key only exists after you set it once.

if "page" not in st.session_state:
    # First run: start the user on the home page.
    st.session_state["page"] = "home"
else:
    # Later runs: keep the current page value so navigation is stable.
    pass

if "num_of_participants" not in st.session_state:
    # Stores the total number of people who will answer the questionnaire.
    # Initially unknown, so set it to None until the user enters it.
    st.session_state["num_of_participants"] = None
else:
    pass

if "current_participant" not in st.session_state:
    # Tracks which participant is currently filling out the questionnaire.
    # We start counting at 1 for the first participant.
    st.session_state["current_participant"] = 1
else:
    pass

if "answers" not in st.session_state:
    # List that holds one answer dictionary per participant.
    # Each element should contain that participant's responses.
    st.session_state["answers"] = []
else:
    pass


## 2. Page navigation (router)
# The "page" key in session_state acts as a simple router.
# Depending on its value, we call exactly one view function that displays a page.
# Other parts of the app (buttons, etc.) update st.session_state["page"]
# to switch between screens.

 # Gets the page at which the app is at the moment.
 # If "page" exists it returns its value, if not it returns "home".
page = st.session_state.get("page", "home")

if page == "home":
    # Home screen:
    # - Introduces the app
    # - Asks for number of participants
    # - Provides entry point into the questionnaire
    show_homepage()

elif page == "questionnaire":
    # Questionnaire screen:
    # - Collects all answers from the current participant
    # - Uses current_participant and num_of_participants from session_state

    # Back navigation: go back to the main landing page.
    col_home, col_prev_participant = st.columns(2)
    with col_home:
        if st.button("← Back to home"):
            st.session_state["page"] = "home"
            st.rerun()

    # Back navigation between participants:
    # If we are on participant N > 1, allow user to step back to N-1 and re-enter answers.
    with col_prev_participant:
        if st.session_state["current_participant"] > 1:
            if st.button("← Back to previous participant"):
                old_cp = st.session_state["current_participant"]
                new_cp = old_cp - 1
                st.session_state["current_participant"] = new_cp
                # Truncate stored answers so the previous participant's data can be changed cleanly.
                st.session_state["answers"] = st.session_state["answers"][:new_cp]
                st.rerun()

    show_questionnaire()

elif page == "result":
    # Result screen:
    # - Aggregates all participants' answers
    # - Computes and displays the group taste profile

    # Back navigation: allow user to return to the questionnaire to adjust preferences.
    if st.button("← Back to questionnaire"):
        st.session_state["page"] = "questionnaire"
        st.rerun()

    group_taste_profile(st.session_state["answers"])

elif page == "api":
    # API results screen:
    # - Uses the computed group profile values (budget, cuisine, walking distance(radius)
    # - Calls the external API (e.g. Yelp) and displays matching restaurants

    # Back navigation: let user move back to the result page or questionnaire.
    col_back_result, col_back_questionnaire = st.columns(2)
    with col_back_result:
        if st.button("← Back to result"):
            st.session_state["page"] = "result"
            st.rerun()
    with col_back_questionnaire:
        if st.button("← Back to questionnaire"):
            st.session_state["page"] = "questionnaire"
            st.rerun()

    show_api_results()

elif page == "about":
    # About screen:
    # - General information about the app, authors and context

    show_about_us()

else:
    # Fallback for invalid / unexpected page values:
    # - Reset to home to avoid the app breaking on a bad state
    st.session_state["page"] = "home"
    show_homepage()