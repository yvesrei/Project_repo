import streamlit as st
import os

# Function shows the landing page (home) of the FoodMingle app.
# It:
# - shows the logo from the app
# - Lets the host choose how many people will participate in the dinner and thereofe the questionnaire
# - Provides additional navigation to the "questionnaire" page

def show_homepage():
        
        # Path to the logo image inside the folder "images"
    logo_path = os.path.join("Images", "FOODMINGLE_Final_Logo_TextMatch.png")

     # Use a 3 column layout to center the logo on the page
    left, center, right = st.columns([1, 2, 1])
    with center:
        st.image(logo_path, width=330)
        

     # Main title of the homepage
    st.header("Welcome to FoodMingle!")

         
        
        ## The user is able to select how many people will take part in the questionnaire in this select-button
        # The number gets safed in "st.session_state" so the app remembers it across all pages.
    num_of_part = st.selectbox(
            "Number of participants",
            options=[2, 3, 4, 5],
            index=None,
            placeholder="Please select a number"
        )
        # Save the selected number in the session state
    st.session_state["num_of_participants"] = num_of_part
        
        ## This button checks if the user has inserted a valid number of participants.
        # If the user hasn't it will display an Error message
        # If the user has inserted a valdi value, the st.session_state is set to "questionnaire" --> page questionnaire is displayed
    if st.button("Set up meal"):
        if num_of_part is None:
                st.warning("Please select a number of participants for your meal")
                st.stop
        else:
                st.session_state["page"] = "questionnaire"
                st.rerun()
         


