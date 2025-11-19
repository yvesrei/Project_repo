import streamlit as st
def show_homepage():
        
        st.title("FOODMINGLE")
        st.subheader("Where tastes meet!")
        
        num_of_part = st.selectbox(
            "Number of participants",
            options=[2, 3, 4, 5],
            index=None,
            placeholder="Please select a number"
        )
        
        st.session_state["num_of_participants"] = num_of_part
        
        if st.button("Set up dinner"):
            if num_of_part is None:
                st.warning("Please select a number of participants for your dinner")
            else:
                st.session_state["page"] = "questionnaire"
                st.rerun()

