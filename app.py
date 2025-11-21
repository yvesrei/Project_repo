import streamlit as st
from Show_homepage import show_homepage
from Questionnaire import show_questionnaire
from spider_chart import group_taste_profile
from About_us import show_about_us




         
# 1. Implement session state

if "page" not in st.session_state:
        st.session_state["page"] = "home"

if "num_of_participants" not in st.session_state:
        st.session_state["num_of_participants"] = None
    
if "current_participant" not in st.session_state:
        st.session_state["current_participant"] = 1
    
if "answers" not in st.session_state:
        st.session_state["answers"] = []



if st.session_state["page"] == "home":
    show_homepage()


if st.session_state["page"] == "questionnaire":
    show_questionnaire()
    
if st.session_state["page"] == "result":
    group_taste_profile("answers")

elif st.session_state["page"] == "about":
    show_about_us()

