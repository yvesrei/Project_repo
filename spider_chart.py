
import streamlit as st
import numpy as np


def group_taste_profile(answers):

    st.title("This is your groups taste profile of today!")

    st.subheader("Let's analyze it.")

    st.header("Results Summary")

    






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

    
    dining_style_scores= []

    for participant in answers:
        
        dining_style_value= participant["dining_style"]

        dining_style_import = participant["dining_style_importance"]

        dining_style_scores.extend([dining_style_value] * dining_style_import)


    type_of_cuisine_scores = {}

    for participant in answers:
        importance = participant["type_of_cuisine_importance"]
        cuisines = participant["type_of_cuisine"]

        for c in cuisines:
            if c not in type_of_cuisine_scores:
                type_of_cuisine_scores[c] = 0

            type_of_cuisine_scores[c] += 1 * importance

    

    st.write(f"Your group budget preference is:{group_budget}")

    st.write (f"Your groups prefers: {type_of_cuisine_scores}")

    st.write (f"Your group prefers: {dining_style_scores}")





