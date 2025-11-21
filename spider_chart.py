
import streamlit as st
import numpy as np
from statistics import mode
from collections import Counter
import matplotlib.pyplot as plt






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

        dining_counts = Counter(dining_style_scores)

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

 
    st.subheader("Importance Distribution")

    budget_importance_group = np.mean([p["budget_importance"] for p in answers])
    cuisine_importance_group = np.mean([p["cuisine_importance"] for p in answers])
    dining_importance_group = np.mean([p["dining_style_importance"] for p in answers])

    labels = np.array(["Budget", "Cuisine", "Dining Style"])
    stats = np.array([
        budget_importance_group,
        cuisine_importance_group,
        dining_importance_group,
    ])

    angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False)
    stats_closed = np.concatenate((stats, [stats[0]]))
    angles_closed = np.concatenate((angles, [angles[0]]))

    fig_radar, ax_radar = plt.subplots(subplot_kw=dict(polar=True))
    ax_radar.plot(angles_closed, stats_closed)
    ax_radar.fill(angles_closed, stats_closed, alpha=0.25)
    ax_radar.set_xticks(angles)
    ax_radar.set_xticklabels(labels)
    ax_radar.set_ylim(0, 3)
    ax_radar.set_title("Average Importance (1–3)")

    st.pyplot(fig_radar)
    st.markdown("---")


    st.subheader("Cuisine Preference Strength")

    fig_bar, ax_bar = plt.subplots()
    cuisines = list(cuisine_scores.keys())
    values = list(cuisine_scores.values())
    ax_bar.barh(cuisines, values)
    ax_bar.set_xlabel("Weighted Score")
    ax_bar.set_ylabel("Cuisine")
    ax_bar.set_title("Weighted Cuisine Scores")

    st.pyplot(fig_bar)
    st.markdown("---")


    st.subheader("Dining Style Distribution (Weighted)")

    if len(dining_counts) == 0:
        st.info("No dining style data available.")
    else:
        labels_pie = list(dining_counts.keys())
        sizes_pie = list(dining_counts.values())

        fig_pie, ax_pie = plt.subplots()
        ax_pie.pie(sizes_pie, labels=labels_pie, autopct="%1.1f%%", startangle=90)
        ax_pie.axis("equal")
        ax_pie.set_title("Dining Style Preferences")
        st.pyplot(fig_pie)

    st.markdown("---")


