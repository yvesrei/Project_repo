import streamlit as st
from statistics import mode
from Show_homepage import show_homepage
from Questionnaire import show_questionnaire
from spider_chart import group_taste_profile
from About_us import show_about_us
from api_client import api_access





         
## 1. Implement session state
# The Streamlit app reruns on every interaction, so we use:
# st.session_state to remember values between reruns.
# "page" controls which screen the user is on
# "num_of_participants" shows how many people will attend the dinner --> answer the questionnaire
# "current_participant"  --> Tracks which participant is currently filling out the questionnaire
# "answers" is the list in which each participants answers are stored

if "page" not in st.session_state:
        st.session_state["page"] = "home"


if "num_of_participants" not in st.session_state:
        st.session_state["num_of_participants"] = None


if "current_participant" not in st.session_state:
        st.session_state["current_participant"] = 1


if "answers" not in st.session_state:
        st.session_state["answers"] = []

## This block controls the page navigation in the app
# Depending on the value stored in st.session_state["page"],
# the corresponding screen is displayed through accessing the function

if st.session_state["page"] == "home":
    show_homepage()


if st.session_state["page"] == "questionnaire":
    show_questionnaire()


if st.session_state["page"] == "result":
    group_taste_profile(st.session_state["answers"])

if st.session_state["page"] == "api":
      api_access()
      


elif st.session_state["page"] == "about":
    show_about_us()

