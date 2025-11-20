import streamlit as st

def show_questionnaire():
        
        st.title(f"Participant {st.session_state['current_participant']}")

        participant=st.session_state['current_participant']

        if f"budget_{participant}" not in st.session_state:
              st.session_state[f"budget_{participant}"] = None
              st.session_state[f"type_of_cuisine_{participant}"] = None
              st.session_state[f"dining_style_{participant}"] = None

        
        # fekbrhtgra
        # hhferhgtb      
        budget = st.selectbox(
            "Your budget preference",
            options=["$","$$","$$$"],
            index=None,
            placeholder="Please choose your budget",
            key=f"budget_{participant}"
        )

        budget_importance= st.slider(
              "How important is the budget for you?",
              1, 3,
              key=f"budget_importance{participant}"
        )

        #n dsjhfgewgfw

        type_of_cuisine= st.multiselect(
              "Your cuisine preference",
              options=["italian", "greek", "swiss", "chinese", "thai"],
              index=None,
              placeholder= "Please choose your prefered type of cuisine",
              max_selections=3,
              key=f"type_of_cuisine_{participant}"
        )

        type_of_cuisine_importance= st.slider(
              "How important is the type of cuisine for you?",
              1, 3,
              key=f"type_of_cuisine_importance{participant}"
        )


        dining_sytle= st.selectbox(
              "Your dining style preference",
              options=["Takeaway","Casual", "A la carte", "Set Menu / Chef's Menu", "Date Night"],
              index=None,
              placeholder= "Please choose your preferred dining style",
              key=f"dining_style_{participant}"
        )

        dining_style_importance= st.slider(
              "How important is the dining style for you?",
              1, 3,
              key=f"dining_style_importance{participant}"
        )

        if st.button("Next Person"):
           
           st.session_state["answers"].append({
                 "budget": budget,
                 "budget_importance": budget_importance,
                 "type_of_cuisine": type_of_cuisine,
                 "type_of_cuisine_importance": type_of_cuisine_importance,
                 "dining_style": dining_sytle, 
                 "dining_style_importance": dining_style_importance
           })
                 
           
           if st.session_state['current_participant'] < st.session_state['num_of_participants']:
                 st.session_state['current_participant'] += 1
                 
                 st.rerun()


           else:
                st.session_state["page"] = "result"
                st.rerun()
                
           
        
       
        
