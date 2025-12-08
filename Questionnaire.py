import streamlit as st
from statistics import mode


def show_questionnaire():
        

         ## Function displays the questionnaire for each participant.
         # Each participant fills out :
         # - His budget preference
         # - His three cuisine preferences and ranks them by importance
         # - His walking distance preference
         # - His importance ranking of the three attributes
         # Their answers get stored individually in the st.session_state
         

         ## Title displays which participant is currently answering the questionnaire.
        st.title(f"Participant {st.session_state['current_participant']}")

        participant=st.session_state['current_participant']
        

         ## Initializes for each participant the fields the first time they appear.
         # These per-participant keys ensure that answers from the previous participant
         # are not shown again. Each participant has their own widget keys for example
         # "budget_1", so Streamlit loads a fresh and empty state.


        if f"budget_{participant}" not in st.session_state:
              st.session_state[f"budget_{participant}"] = None
              st.session_state[f"type_of_cuisine_{participant}"] = []
              st.session_state[f"walking_distance_{participant}"] = None

        
        # In this button each participant can choose his budget preference and
        # it gets stored in his personal key.
        

        budget = st.selectbox(
            "Your budget preference",
            options=["$","$$","$$$", "$$$$"],
            index=None,
            placeholder="Please choose your budget",
            key=f"budget_{participant}"
        )


        # This is a multiselect button, eg. the participant is able to choose 3 different type of cuisines.
        # The maximum number of selected types of cuisines is set to 3.
        # Gets stored in the personal key.
        # The ranking section only activates if exactly 3 cuisines have been selected.
        # Every cuisine category that contains multiple cuisines includes an explanatory list in brackets.

        type_of_cuisine = st.multiselect(
             "Your cuisine preference",
             options=[
                  "Italian",
                  "Asian (Thai, Chinese, Japanese, Korean)",
                  "Swiss / Alpine (Swiss, Austrian, German)",
                  "Mediterranean (Greek, Spanish, Turkish, Portuguese)",
                  "American",
                  "Middle Eastern (Lebanese, Persian, Arabic, Persian)",
                  "Latin American (Mexican, Peruvian, Brazilian, Argentinian)",
                  "Indian / South Asian (Indian, Pakistani, Sri Lankan)",
                  "Vegetarian / Vegan",
                  "Seafood & Sushi"
                  ],
            placeholder="Please choose your preferred type of cuisine",
            max_selections=3,
            key=f"type_of_cuisine_{participant}"
            )

         # This function maps frontend long labels from the multiselect button back to the original internal category keys.
         # Therefore we keep the naming simple and clean.
        CUISINE_LABEL_MAP = {
              "Italian": "Italian",
            "Asian (Thai, Chinese, Japanese, Korean)": "Asian",
            "Swiss / Alpine (Swiss, Austrian, German)": "Swiss / Alpine",
            "Mediterranean (Greek, Spanish, Turkish, Portuguese)": "Mediterranean",
            "American": "American",
            "Middle Eastern (Lebanese, Persian, Arabic, Persian)": "Middle Eastern",
            "Latin American (Mexican, Peruvian, Brazilian, Argentinian)": "Latin American",
            "Indian / South Asian (Indian, Pakistani, Sri Lankan)": "Indian / South Asian",
            "Vegetarian / Vegan": "Vegetarian / Vegan",
            "Seafood & Sushi": "Seafood & Sushi"
            }

         # Here they get converted to the internal keys.
        type_of_cuisine_internal = [
             CUISINE_LABEL_MAP[c] for c in type_of_cuisine
             ]
   
              
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

             # Convert ranked cuisines to internal keys
            ranked_cuisines_internal = [CUISINE_LABEL_MAP[c] for c in ranked_cuisines]

         # Error message is displayed when not exactly 3 cuisines have been selected by the participant.
        else:
            ranked_cuisines = []
            st.warning("You must select exactly 3 cuisines to rank them!")

        
        ## Selectbox where participant decides his preferred walking distance.
        # Stored as well in a specific participant key.

        walking_distance = st.selectbox(
        "🚶 How far are you willing to walk from the main train station?",
        options= ["5 minutes", "10 minutes", "15 minutes", "No preference"],
        index= None,
        placeholder= "Please choose your preferred walking distance",
              key=f"walking_distance_{participant}"
        )
    
        
        st.markdown("Set a weight (1–3) for each attribute (3 = most important, 1 = least important. Use each number once.")


        ## The importance ranking system
        # Each factor (budget, cuisine, walking distance) must receive a unique importance value (1, 2, 3).
        # Each participant chooses 1–3 for budget, then the remaining values for cuisine,
        # and the final value is automatically assigned to walking distance. Same logic as before in the cuisine part.


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

   
        walking_distance_importance = [v for v in [1, 2, 3]
                                   if v not in [budget_importance, cuisine_importance]][0]


        st.write(f"Importance of WALKING DISTANCE: **{walking_distance_importance}** (auto-assigned)")


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
             if walking_distance is None:
                  st.error("❌ Please select a walking distance before continuing.")
                  st.stop()

           
             st.session_state["answers"].append({
                 "budget": budget,
                 "budget_importance": budget_importance,
                 "type_of_cuisine": type_of_cuisine_internal,
                 "ranked_cuisines": ranked_cuisines_internal,
                 "cuisine_importance": cuisine_importance,
                 "walking_distance": walking_distance, 
                 "walking_distance_importance": walking_distance_importance
           })
                 
            
             if st.session_state['current_participant'] < st.session_state['num_of_participants']:
                 st.session_state['current_participant'] += 1
                 
                 st.rerun()


             else:
                   st.session_state["page"] = "result"
                   st.rerun()
                
           

       
        