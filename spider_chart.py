
import streamlit as st
import numpy as np


def group_taste_profile(answers):

    st.title("This is your groups taste profile of today!")

    st.subheader("Let's analyze it.")

    st.header("Results Summary")

    st.subheader("💸 Budget Preference (1 = $, 3 = $$$)")
    st.metric("Group Budget Score", round(group_budget, 2))

    st.subheader("🍽️ Dining Style Preference (1 = Takeaway, 5 = Date Night)")
    st.metric("Group Dining Style Score", round(group_dining_style, 2))

    st.subheader("🌎 Popular Cuisines")
    for cuisine, score in type_of_cuisine_scores.items():
        st.write(f"- **{cuisine}**: {score}")

    budget_dict = {"$":1, "$$":2, "$$$":3}

    budget_scores= []
    budget_weights=[]

    for participant in answers:
        
        budget_value= participant["budget"]

        numeric_budget= budget_dict[budget_value]

        budget_import= participant["budget_importance"]

        weighted_score= numeric_budget * budget_import

        budget_scores.append(weighted_score)

        budget_weights.append(budget_import)

    group_budget = sum(budget_scores) / sum(budget_weights)

    dining_style_dict= {"Takeaway": 1,"Casual": 2, "A la carte": 3, "Set Menu / Chef's Menu": 4, "Date Night": 5}

    dining_style_scores= []
    dining_style_weights=[]

    for participant in answers:
        
        dining_style_value= participant["dining_style"]

        numeric_dining_style= dining_style_dict[dining_style_value]

        dining_style_import= participant["dining_style_importance"]

        weighted_dining_style_score= numeric_dining_style * dining_style_import

        dining_style_scores.append(weighted_dining_style_score)

        dining_style_weights.append(dining_style_import)

    group_dining_style = sum(dining_style_scores) / sum(dining_style_weights)

    type_of_cuisine_scores = {}

    for participant in answers:
        importance = participant["type_of_cuisine_importance"]
        cuisines = participant["type_of_cuisine"]

        for c in cuisines:
            if c not in type_of_cuisine_scores:
                type_of_cuisine_scores[c] = 0

            type_of_cuisine_scores[c] += 1 * importance


    


