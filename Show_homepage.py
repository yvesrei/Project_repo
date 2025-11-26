import streamlit as st
import os
def show_homepage():
        
        # Path to the logo inside your project
    logo_path = os.path.join("Images", "FOODMINGLE_Final_Logo_TextMatch.png")

    # Create 3 columns for centering
    left, center, right = st.columns([1, 2, 1])

    with center:
        st.image(logo_path, width=260)
        


    st.header("Welcome to FoodMingle")
    
         
        
        ## The user is able to select how many people will take part in the questionnaire in this select-button
        # The number gets safed in "st.session_state" so the app remembers it across all pages.
    num_of_part = st.selectbox(
            "Number of participants",
            options=[2, 3, 4, 5],
            index=None,
            placeholder="Please select a number"
        )
        
    st.session_state["num_of_participants"] = num_of_part
        
        ## This button checks if the user has inserted a valid number of participants.
        # If the user hasn't it will display an Error message
        # If the user has inserted a valdi value, the st.session_state is set to "questionnaire" --> page questionnaire is displayed
    if st.button("Set up dinner"):
        if num_of_part is None:
                st.warning("Please select a number of participants for your dinner")
                st.stop
        else:
                st.session_state["page"] = "questionnaire"
                st.rerun()
        ## Visual line to seperat the two buttons
    st.write("---")    

        ## If the user clicks this button, the st.session_state is set to the page "about" --> page about is displayed
    if st.button("About us", key="about_button"): 
        st.session_state["page"] = "about"
        st.rerun()