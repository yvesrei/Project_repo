
import streamlit as st
import numpy as np
from statistics import mode
from collections import Counter
import plotly.graph_objects as go
import plotly.express as px



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



    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Budget Preference", budget_symbol_group)

    with col2:
        st.metric("Top Cuisine", most_preferred_cuisine)

    with col3:
        st.metric("Dining Style", most_common_dining_style)

    st.markdown("---")

   
    st.subheader("Importance Distribution (Radar Chart)")

    
    budget_importance_group = np.mean([p["budget_importance"] for p in answers])
    cuisine_importance_group = np.mean([p["cuisine_importance"] for p in answers])
    dining_importance_group = np.mean([p["dining_style_importance"] for p in answers])

    radar_categories = ["Budget Importance", "Cuisine Importance", "Dining Style Importance"]
    radar_values = [
        budget_importance_group,
        cuisine_importance_group,
        dining_importance_group
    ]

    fig_radar = go.Figure(
        data=go.Scatterpolar(
            r=radar_values,
            theta=radar_categories,
            fill='toself'
        )
    )

    fig_radar.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 3])
        ),
        showlegend=False
    )

    st.plotly_chart(fig_radar)

    st.markdown("---")

 
    st.subheader("Cuisine Preference Strength")

    fig_bar = px.bar(
        x=list(cuisine_scores.values()),
        y=list(cuisine_scores.keys()),
        orientation='h',
        title="Weighted Cuisine Scores",
        labels={"x": "Score", "y": "Cuisine"},
    )

    st.plotly_chart(fig_bar)

    st.markdown("---")

    st.subheader("Dining Style Distribution (Weighted)")

    dining_counts = Counter(dining_style_scores)

    fig_pie = px.pie(
        names=list(dining_counts.keys()),
        values=list(dining_counts.values()),
        title="Dining Style Preferences"
    )

    st.plotly_chart(fig_pie)

    st.markdown("---")



