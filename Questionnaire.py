import streamlit as st
from statistics import mode


def show_questionnaire():
        
        st.title(f"Participant {st.session_state['current_participant']}")

        participant=st.session_state['current_participant']

        if f"budget_{participant}" not in st.session_state:
              st.session_state[f"budget_{participant}"] = None
              st.session_state[f"type_of_cuisine_{participant}"] = []
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

        

        #n dsjhfgewgfw

        type_of_cuisine= st.multiselect(
              "Your cuisine preference",
              options=["italian", "greek", "swiss", "chinese", "thai"],
              placeholder= "Please choose your prefered type of cuisine",
              max_selections=3,
              key=f"type_of_cuisine_{participant}")
              
              
        st.markdown("### Rank your selected cuisines (1 = most preferred):")

        if len(type_of_cuisine) == 3:
            rank1 = st.selectbox(
                   "Rank 1 (most preferred)",
                   type_of_cuisine,
                   key=f"rank1_{participant}"
                   )
                   
            rank2_options = [c for c in type_of_cuisine if c != rank1]
            rank2 = st.selectbox(
                   "Rank 2",
                   rank2_options,
                   key=f"rank2_{participant}"
                   )

            rank3 = [c for c in rank2_options if c != rank2][0]
            st.write(f"Rank 3: {rank3}")
            
            ranked_cuisines = [rank1, rank2, rank3]

        else:
            ranked_cuisines = []
            st.warning("⚠️ You must select exactly 3 cuisines to rank them.")


        dining_style= st.selectbox(
              "Your dining style preference",
              options=["Takeaway","Casual", "A la carte", "Set Menu / Chef's Menu", "Date Night"],
              index=None,
              placeholder= "Please choose your preferred dining style",
              key=f"dining_style_{participant}"
        )
        
        st.markdown("### Importance of the three factors (use 1, 2, 3 once each)")

        budget_importance = st.selectbox(
        "Importance of BUDGET",
        [1, 2, 3],
        key=f"budget_importance_{participant}"
    )

    
        remaining_after_budget = [v for v in [1, 2, 3] if v != budget_importance]

        cuisine_importance = st.selectbox(
             "Importance of CUISINE",
             remaining_after_budget,
             key=f"cuisine_importance_{participant}"
             )

   
        dining_style_importance = [v for v in [1, 2, 3]
                                   if v not in [budget_importance, cuisine_importance]][0]

        st.write(f"Importance of DINING STYLE: **{dining_style_importance}** (auto-assigned)")




        

        

        if st.button("Next Person"):
             
             if len(type_of_cuisine) != 3:
                   st.error("❌ You must choose exactly 3 cuisines before continuing.")
                   st.stop()
             if budget is None:
                  st.error("❌ Please select a budget before continuing.")
                  st.stop()
             if dining_style is None:
                  st.error("❌ Please select a dining style before continuing.")
                  st.stop()

           
             st.session_state["answers"].append({
                 "budget": budget,
                 "budget_importance": budget_importance,
                 "type_of_cuisine": type_of_cuisine,
                 "ranked_cuisines": ranked_cuisines,
                 "dining_style": dining_style, 
                 "dining_style_importance": dining_style_importance
           })
                 
            
             if st.session_state['current_participant'] < st.session_state['num_of_participants']:
                 st.session_state['current_participant'] += 1
                 
                 st.rerun()


             else:
                   st.session_state["page"] = "result"
                   st.rerun()
                
           
        
       
        