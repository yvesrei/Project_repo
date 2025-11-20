import streamlit as st

def show_questionnaire():
        
        st.title(f"Participant {st.session_state['current_participant']}")

        participant=st.session_state['current_participant']

        
        # fekbrhtgra
        # hhferhgtb      
        budget = st.selectbox(
            "Your budget preference",
            options=["$","$$","$$$"],
            index=None,
            placeholder="Please choose your budget",
            key=f"budget_{participant}"
        )

        #n dsjhfgewgfw

        type_of_cuisine= st.selectbox(
              "Your cuisine preference",
              options=["italian", "greek", "swiss", "chinese", "thai"],
              index=None,
              placeholder= "Please choose your prefered type of cuisine",
              key=f"type_of_cuisine_{participant}"
        )
        dining_sytle= st.selectbox(
              "Your dining style preference",
              options=["Takeaway","Casual", "A la carte", "Set Menu / Chef's Menu", "Date Night"],
              index=None,
              placeholder= "Please choose your preferred dining style",
              key=f"dining_style_{participant}"
        )

        if st.button("Next Person"):
           
           st.session_state["answers"].append({
                 "budget": budget,
                 "type_of_cuisine": type_of_cuisine,
                 "dining_style": dining_sytle
           })
                 
           
           if st.session_state['current_participant'] < st.session_state['num_of_participants']:
                 st.session_state['current_participant'] += 1
                 
                 st.rerun()


           else:
                st.session_state["page"] = "result"
                st.rerun()
                
           
        
       
        
