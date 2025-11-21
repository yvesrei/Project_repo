
import streamlit as st
import numpy as np
from statistics import mode
from collections import Counter



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

    rounded_budget= round(group_budget)

    reverse_budget_dict = {1: "$", 2: "$$", 3: "$$$"}

    budget_symbol_group = reverse_budget_dict.get(rounded_budget, "Unknown")

    
    dining_style_scores= []

    for participant in answers:
        
        dining_style_value= participant["dining_style"]

        dining_style_import = participant["dining_style_importance"]

        dining_style_scores.extend([dining_style_value] * dining_style_import)

        most_common_value = mode(dining_style_scores)


    most_common_dining_style = Counter(dining_style_scores).most_common(1)[0][0]


    cuisine_scores = Counter()

    for participant in answers:
        ranked_list = participant["ranked_cuisines"]

        for i, cuisine in enumerate(ranked_list):
            weight = 3 - i
            cuisine_scores[cuisine] += weight


    most_preferred_cuisine = cuisine_scores.most_common(1)[0][0]

    

    st.write(f"Your group budget preference is:  {budget_symbol_group}")

    st.write (f"Your groups prefers:  {most_preferred_cuisine}")

    st.write (f"Your group prefers:  {most_common_dining_style}")



