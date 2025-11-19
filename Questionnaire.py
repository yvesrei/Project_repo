import streamlit as st

def show_questionnaire():
        
        st.title(f"Participant {st.session_state['current_participant']}")
        
        # fekbrhtgra
        # hhferhgtb      
        budget = st.selectbox(
            "Your budget preference",
            options=["$","$$","$$$"],
            index=None,
            placeholder="Please choose your budget"
        )

        #n dsjhfgewgfw

        type_of_cuisine= st.selectbox(
              "Your cuisine preference",
              options=["italian", "greek", "swiss", "chinese", "thai"],
              index=None
              placeholder= "Please choose your prefered type of cuisine"
        )
        dining_sytle= st.selectbox(
              "Your dining style preference",
              options=["takeaway","Casual", "A la carte", "Set Menu / Chef's Menu", "Date Night"],
              index=None
              placeholder= "Please choose your prefered dining style"
        )
        if st.button("Next Person"):
           st.session_state["page"] = "result"
           st.rerun()
        
       
        
