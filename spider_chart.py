
import streamlit as st
import numpy as np
from statistics import mode
from collections import Counter
import altair as alt
import pandas as pd
from sklearn.cluster import KMeans

# ---------- ML HELPER FUNCTIONS (NEW) ----------
CUISINES = ["italian", "greek", "swiss", "chinese", "thai"]

DINING_STYLES = [
    "Takeaway",
    "Casual",
    "A la carte",
    "Set Menu / Chef's Menu",
    "Date Night",
]

BUDGET_DICT = {"$": 1, "$$": 2, "$$$": 3}
REVERSE_BUDGET_DICT = {v: k for k, v in BUDGET_DICT.items()}

def build_group_feature_vector(answers):
    """
    Build ONE numeric vector that represents the entire group.
    Uses:
    - weighted average budget (numeric)
    - average importances
    - normalized cuisine score distribution (from ranks)
    - normalized dining style distribution (weighted by importance)
    """
    if not answers:
        return None

    # ---- weighted budget ----
    budget_scores = []
    budget_weights = []

    for p in answers:
        numeric_budget = BUDGET_DICT[p["budget"]]
        imp = p["budget_importance"]
        budget_scores.append(numeric_budget * imp)
        budget_weights.append(imp)

    group_budget_numeric = sum(budget_scores) / sum(budget_weights)

    # ---- importances: averages ----
    budget_imp_avg = np.mean([p["budget_importance"] for p in answers])
    cuisine_imp_avg = np.mean([p["cuisine_importance"] for p in answers])
    dining_imp_avg = np.mean([p["dining_style_importance"] for p in answers])

    # ---- cuisine scores (same idea as in group_taste_profile) ----
    cuisine_scores = Counter()
    for p in answers:
        ranked = p["ranked_cuisines"]
        for i, cuisine in enumerate(ranked):
            weight = 3 - i  # rank1=3, rank2=2, rank3=1
            cuisine_scores[cuisine] += weight

    cuisine_vec = [cuisine_scores.get(c, 0) for c in CUISINES]
    total_cuisine = sum(cuisine_vec) or 1
    cuisine_vec_norm = [x / total_cuisine for x in cuisine_vec]

    # ---- dining style distribution (weighted by importance) ----
    dining_counts = Counter()
    for p in answers:
        style = p["dining_style"]
        imp = p["dining_style_importance"]
        dining_counts[style] += imp

    dining_vec = [dining_counts.get(s, 0) for s in DINING_STYLES]
    total_dining = sum(dining_vec) or 1
    dining_vec_norm = [x / total_dining for x in dining_vec]

    # ---- final group vector ----
    features = [
        group_budget_numeric,
        budget_imp_avg,
        cuisine_imp_avg,
        dining_imp_avg,
    ] + cuisine_vec_norm + dining_vec_norm

    return np.array(features, dtype=float)


def register_group_profile(feature_vector):
    """Store this group's feature vector in session_state."""
    if feature_vector is None:
        return

    if "group_profile_vectors" not in st.session_state:
        st.session_state["group_profile_vectors"] = []

    st.session_state["group_profile_vectors"].append(feature_vector.tolist())


def cluster_group_profiles():
    """
    Run K-Means on all stored group profiles.
    Returns:
        labels  - cluster id per group
        centers - cluster centers
        current_group_label - cluster id of the current (last) dinner
    """
    vectors_list = st.session_state.get("group_profile_vectors", [])
    if len(vectors_list) < 2:
        return None, None, None  # need at least 2 dinners

    X = np.array(vectors_list, dtype=float)
    n_groups = X.shape[0]

    n_clusters = min(3, n_groups)  # up to 3 group profile types

    kmeans = KMeans(
        n_clusters=n_clusters,
        random_state=42,
        n_init=10,
    )
    labels = kmeans.fit_predict(X)
    centers = kmeans.cluster_centers_

    current_group_label = int(labels[-1])  # last = current dinner
    return labels, centers, current_group_label


def describe_cluster_center(center):
    """Turn a cluster center vector into a human-readable name + description."""
    n_cuisines = len(CUISINES)

    budget_numeric = center[0]
    budget_imp, cuisine_imp, dining_imp = center[1:4]

    cuisine_vec = center[4:4 + n_cuisines]
    dining_vec = center[4 + n_cuisines:]

    # top cuisine(s)
    top_cuisine_idx = int(np.argmax(cuisine_vec))
    top_cuisine = CUISINES[top_cuisine_idx]

    if n_cuisines > 1:
        second_cuisine_idx = int(np.argsort(cuisine_vec)[-2])
    else:
        second_cuisine_idx = top_cuisine_idx
    second_cuisine = CUISINES[second_cuisine_idx]

    # top dining style
    top_dining_idx = int(np.argmax(dining_vec))
    top_dining = DINING_STYLES[top_dining_idx]

    def importance_main():
        vals = {
            "budget": float(budget_imp),
            "cuisine": float(cuisine_imp),
            "dining": float(dining_imp),
        }
        return max(vals, key=vals.get)

    main_importance = importance_main()

    # --------- naming logic based on our archetypes ---------
    name = "Chill Whatever-Works Group"
    explanation = (
        "Balanced preferences without strong extremes. Budget, cuisine and dining style "
        "are all somewhat flexible."
    )

    # Cheap & Cheerful Squad
    if budget_numeric <= 1.6 and main_importance == "budget" and top_dining in ["Takeaway", "Casual"]:
        name = "Cheap & Cheerful Squad"
        explanation = (
            "Your group strongly prioritises a low budget and prefers relaxed options like takeaway "
            "or casual dining. Cuisine and dining style are more flexible as long as it stays affordable."
        )

    # Foodie Experience Hunters
    elif budget_numeric >= 2.4 and main_importance in ["cuisine", "dining"] and top_dining in ["A la carte", "Set Menu / Chef's Menu", "Date Night"]:
        name = "Foodie Experience Hunters"
        explanation = (
            "Your group is willing to spend more for a good experience. Cuisine and/or dining style are "
            "the most important factors, and sit-down or special menus fit you well."
        )

    # Mediterranean Comfort Crowd
    elif top_cuisine in ["italian", "greek"] and 1.7 <= budget_numeric <= 2.4:
        name = "Mediterranean Comfort Crowd"
        explanation = (
            "Your group is drawn to Mediterranean comfort food like Italian or Greek at a moderate budget. "
            "You enjoy familiar flavours and a relaxed but proper sit-down meal."
        )

    # Local Traditionalists
    elif top_cuisine == "swiss":
        name = "Local Traditionalists"
        explanation = (
            "Your group leans towards Swiss or traditional options. You value familiar local dishes "
            "and a classic dining experience."
        )

    # Asian Craving Crew
    elif top_cuisine in ["chinese", "thai"]:
        name = "Asian Craving Crew"
        explanation = (
            "Your group has a clear craving for Asian flavours, especially {} and {}. "
            "Cuisine is an important driver for your choice tonight."
        ).format(top_cuisine.capitalize(), second_cuisine.capitalize())

    # budget level string
    budget_level = (
        "$" if budget_numeric < 1.5 else
        "$$" if budget_numeric < 2.5 else
        "$$$"
    )

    details = {
        "budget_level": budget_level,
        "main_cuisine": top_cuisine,
        "second_cuisine": second_cuisine,
        "main_dining_style": top_dining,
        "main_importance_dimension": main_importance,
    }

    return name, explanation, details


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

    st.session_state["group_budget_numeric"] = str(rounded_budget)

    
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

    

    # Counts the rank of the cuisine choices of the participants.
    # Assigns values to ranks: rank 1 = 3 points, rank 2 = 2 points, rank 3 = 1 point.
    # And gets the cuisine that has got the most points and stores it in "most_preferred_cuisine".
    
    

    # Counts the rank of the cuisine choices of the participants.
    # Assigns values to ranks: rank 1 = 3 points, rank 2 = 2 points, rank 3 = 1 point.
    # And gets the cuisine that has got the most points and stores it in "most_preferred_cuisine".
        # Counts how many times each dining style appears (after weighting).
    dining_counts = Counter(dining_style_scores)

    # Gives us the weighted most common dining style of the list
    most_common_dining_style = dining_counts.most_common(1)[0][0]

    # Counts the rank of the cuisine choices of the participants.
    # Assigns values to ranks: rank 1 = 3 points, rank 2 = 2 points, rank 3 = 1 point.
    # And gets the cuisine that has got the most points and stores it in "most_preferred_cuisine".
    cuisine_scores = Counter()

    for participant in answers:
        ranked_list = participant["ranked_cuisines"]
        for i, cuisine in enumerate(ranked_list):
            weight = 3 - i       # rank1=3, rank2=2, rank3=1
            cuisine_scores[cuisine] += weight

    if cuisine_scores:
        most_preferred_cuisine = cuisine_scores.most_common(1)[0][0]
    else:
        most_preferred_cuisine = "unknown"

    # Save cuisine for the API (lowercase, e.g. "italian")
    st.session_state["group_cuisine"] = most_preferred_cuisine.lower()


    
    # Summary metrics --> shows the three group Values in boxes.
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
    dining_importance_group  = np.mean([p["dining_style_importance"] for p in answers])


    df_radar = pd.DataFrame({
    "category": ["Budget", "Cuisine", "Dining Style"],
    "value": [
        budget_importance_group,
        cuisine_importance_group,
        dining_importance_group
        ]
        })


    chart = alt.Chart(df_radar).mark_bar().encode(
    x=alt.X("category:N", title="Category"),
    y=alt.Y("value:Q", title="Average Importance (1–3)"),
    color=alt.Color("category:N")
    )

    st.altair_chart(chart, use_container_width=True)

    st.markdown("---")


    ## This code block visualizes the weighted cuisine scores as a bar chart.
    # We first convert the cuisine_scores counter into a dataframe so Altair can read the data init.
    # Each bar then represents one cuisine and how many points it received in total.
    # Sorted from most points to least points.


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

        # 🔴 NEW: MACHINE LEARNING – GROUP PROFILE CLUSTERING 🔴
    group_vector = build_group_feature_vector(answers)
    register_group_profile(group_vector)

    st.subheader("Group Taste Profile (Machine Learning)")

    labels, centers, current_label = cluster_group_profiles()

    if labels is None:
        st.info(
            "Not enough past dinners to compare group taste profiles yet. "
            "After you have used the app for multiple dinners, I'll start recognising recurring group types."
        )
    else:
        center = centers[current_label]
        name, explanation, details = describe_cluster_center(center)

        st.success(
            f"Tonight's group looks like: **{name}** "
            f"(Cluster {current_label + 1} of {len(set(labels))})"
        )
        st.write(explanation)

        colg1, colg2, colg3 = st.columns(3)
        with colg1:
            st.metric("Typical Budget", details["budget_level"])
        with colg2:
            st.metric("Key Cuisine", details["main_cuisine"].capitalize())
        with colg3:
            st.metric("Dining Style", details["main_dining_style"])

        # Show cluster sizes across all saved dinners
        counts = Counter(labels)
        st.caption("Cluster distribution across all saved dinners:")
        for cid, count in sorted(counts.items()):
            st.caption(f"- Cluster {cid + 1}: {count} dinner(s)")

        # Store for other pages (e.g. API page)
        st.session_state["current_group_cluster_id"] = int(current_label)
        st.session_state["current_group_cluster_name"] = name

    if st.button("Find matching Restaurants!"):
        st.session_state["page"] = "api"
        st.rerun()
