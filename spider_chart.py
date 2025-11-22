
import streamlit as st
import numpy as np
from statistics import mode
from collections import Counter
import altair as alt
import pandas as pd


def group_taste_profile(answers):

    # Titlle and headers for the result summary
    st.title("This is your groups taste profile of today!")

    st.subheader("Let's analyze it.")

    st.header("Results Summary")


    # Created a dictionary to convert the budget answers into numeric Values example: "$" --> 1.

    budget_dict = {"$":1, "$$":2, "$$$":3}

   # Create empty lists to store interim results.

    budget_scores= []
    budget_weights=[]


    ## For each participant their numeric budget value gets multiplied by their importance value.
    # This gives more weight to the answers of participants who chose to give their budget preference more weight.

    for participant in answers:
        
        budget_value= participant["budget"]

        numeric_budget= budget_dict[budget_value]

        budget_import= participant["budget_importance"]

        weighted_score= numeric_budget * budget_import

        budget_scores.append(weighted_score)

        budget_weights.append(budget_import)

    # Calculates the weighted group averagre result of the group budget value.

    group_budget = sum(budget_scores) / sum(budget_weights)

    ## Rounds the weigthed group value to the nearest whole number and converts it back into "$, $$, $$$".

    rounded_budget= round(group_budget)

    reverse_budget_dict = {1: "$", 2: "$$", 3: "$$$"}

    budget_symbol_group = reverse_budget_dict.get(rounded_budget, "Unknown")

    
    # Empty list gets created to store the dining_style scores.

    dining_style_scores= []

    # For each participant the chosen dining style gets muplitplied by the chosen importance for that style.
    # Then the list gets extended with the dining style times the importance value.
    # Example: Casual (importance = 2) --> "Casual" gets addded 2 times in the list.

    for participant in answers:
        
        dining_style_value= participant["dining_style"]

        dining_style_import = participant["dining_style_importance"]

        dining_style_scores.extend([dining_style_value] * dining_style_import)

    # Counts how many times each dining style appears (after weighting).

    dining_counts = Counter(dining_style_scores)

    # Gives us the weighted most common dining style of the list, by selecting the first one == the most common one.

    most_common_dining_style = Counter(dining_style_scores).most_common(1)[0][0]

    # Counts the rank of the cuisine choices of the participants.
    # Assigns values to ranks: rank 1 = 3 points, rank 2 = 2 points, rank 3 = 1 point.
    
    cuisine_scores = Counter()

    for participant in answers:
        ranked_list = participant["ranked_cuisines"]

        for i, cuisine in enumerate(ranked_list):
            weight = 3 - i
            cuisine_scores[cuisine] += weight


    most_preferred_cuisine = cuisine_scores.most_common(1)[0][0]

    

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Budget Preference", budget_symbol_group)
    with col2:
        st.metric("Top Cuisine", most_preferred_cuisine)
    with col3:
        st.metric("Dining Style", most_common_dining_style)

    st.markdown("---")

    
    st.subheader("Importance Distribution")

    budget_importance_group = np.mean([p["budget_importance"] for p in answers])
    dining_importance_group = np.mean([p["dining_style_importance"] for p in answers])

    df_radar = pd.DataFrame({
        'category': ["Budget", "Cuisine"],
        'value': [
            budget_importance_group,
            dining_importance_group
        ]
    })

    radar = alt.Chart(df_radar).mark_area(
        opacity=0.3
    ).encode(
        theta=alt.Theta("category:N", sort=None),
        radius=alt.Radius("value:Q", scale=alt.Scale(domain=[0,3])),
        color=alt.value("#4C72B0")
    )

    st.altair_chart(radar, use_container_width=True)

    st.markdown("---")
    
    st.subheader("Cuisine Preference Strength")

    df_cuisine = pd.DataFrame({
        "Cuisine": list(cuisine_scores.keys()),
        "Score": list(cuisine_scores.values())
    })

    bar = alt.Chart(df_cuisine).mark_bar().encode(
        x="Score:Q",
        y=alt.Y("Cuisine:N", sort='-x'),
        color=alt.value("#55A868")
    )

    st.altair_chart(bar, use_container_width=True)

    st.markdown("---")

    # ----------------------------------------------------
    # DINING STYLE PIE CHART (Altair)
    # ----------------------------------------------------
    st.subheader("Dining Style Distribution (Weighted)")

    if len(dining_counts) == 0:
        st.info("No dining style data available.")
    else:
        df_pie = pd.DataFrame({
            "Dining Style": list(dining_counts.keys()),
            "Count": list(dining_counts.values())
        })

        pie = alt.Chart(df_pie).mark_arc().encode(
            theta="Count:Q",
            color="Dining Style:N"
        )

        st.altair_chart(pie, use_container_width=True)

    st.markdown("---")

