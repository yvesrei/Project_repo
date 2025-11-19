import streamlit as st
from Show_homepage import show_homepage


st.write("jeay, we connecetd everyhting" \
         
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
