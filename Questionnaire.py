import streamlit as st
from statistics import mode


def show_questionnaire():
        
        ## Title displays which participant is currently answering the questionnaire.
        st.title(f"Participant {st.session_state['current_participant']}")

        participant=st.session_state['current_participant']
        

        ## Initializes for each participant the fields the first time they appear.
        # These per-participant keys ensure that answers from previous participant. 
        # are not shown again. Each participant has their own widget keys for example
        # "budget_1", so Streamlit loads a fresh, empty state.


        if f"budget_{participant}" not in st.session_state:
              st.session_state[f"budget_{participant}"] = None
              st.session_state[f"type_of_cuisine_{participant}"] = []
              st.session_state[f"dining_style_{participant}"] = None

        
        # In this button each participant can choose his budget preference and
        # it gets stored in his personal key.
        

        budget = st.selectbox(
            "Your budget preference",
            options=["$","$$","$$$"],
            index=None,
            placeholder="Please choose your budget",
            key=f"budget_{participant}"
        )


        # This is a multiselect button, eg. the participant is able to choose 3 different type if cuisines.
        # The maximum number of selected types of cuisines is set to 3.
        # Gets stored in the personal key.
        # The ranking section only activates if exactly 3 cuisines have been selected.

        type_of_cuisine= st.multiselect(
              "Your cuisine preference",
              options=["italian", "greek", "swiss", "chinese", "thai"],
              placeholder= "Please choose your prefered type of cuisine",
              max_selections=3,
              key=f"type_of_cuisine_{participant}")
              
              
        st.markdown("### Rank your selected cuisines (1 = most preferred):")

        ## Ranking logic of the 3 selcted cuisines.
        # The participant must rank his selected cuisines manually.
        # Ranks are linked to each other. So Rank 2 options exclude the one chosen in rank 1.
        # Rank 3 is auto assigned with what is left--> ensure that every rank is used.

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

        
        ## Selectbox where participant decides his preferred dining style.
        # Stored as well in a specific participant key.


        dining_style= st.selectbox(
              "Your dining style preference",
              options=["Takeaway","Casual", "A la carte", "Set Menu / Chef's Menu", "Date Night"],
              index=None,
              placeholder= "Please choose your preferred dining style",
              key=f"dining_style_{participant}"
        )
        
        st.markdown("### Importance of the three factors (use 1, 2, 3 once each)")


        ## The importance ranking system
        # Each factor (budget, cuisine, dining style) must receive a unique importance value (1, 2, 3).
        # Each participant chooses 1–3 for budget, then the remaining values for cuisine,
        # and the final value is automatically assigned to dining style. Same logic as before in the cuisine part.


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


        ## This button performs at first the validation with the check if the participant has selected all valid answers. 
        # If not it displays an error-message with the problem, and what the participant has to do.
        # Then the answers of the participant get saved in "answers".
        # If everything was correct and the answers were stored it moves to the next participant or 
        # if all participants have completed the questionnaire it moves to the result page.


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
                
           

       
        