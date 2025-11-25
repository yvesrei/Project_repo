
import streamlit as st
import numpy as np
from statistics import mode
from collections import Counter
import altair as alt
import pandas as pd
from sklearn.cluster import KMeans
from pathlib import Path  
import csv               


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

DATA_FILE = Path("group_profiles.csv")


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

def generate_synthetic_group_profiles(n=50):
    """
    Generate n synthetic group profile vectors based on our archetypes:
    - Cheap & Cheerful Squad
    - Foodie Experience Hunters
    - Mediterranean Comfort Crowd
    - Local Traditionalists
    - Asian Craving Crew
    - Chill Whatever-Works Group

    Each synthetic group is sampled around one archetype center with some noise.
    """
    rng = np.random.default_rng(42)
    vectors = []

    # Helper to build cuisine/dining arrays from dict
    def pref_to_array(pref_dict, keys):
        arr = np.array([pref_dict.get(k, 0.0) for k in keys], dtype=float)
        arr = np.clip(arr, 1e-3, None)  # avoid zeros for Dirichlet
        return arr

    # Define archetype prototypes
    archetypes = [
        {
            "name": "cheap_cheerful",
            "weight": 1.0,
            "budget_mean": 1.2,
            "budget_imp_mean": 2.7,
            "cuisine_imp_mean": 1.8,
            "dining_imp_mean": 1.5,
            "cuisine_pref": {
                "italian": 0.2,
                "greek": 0.2,
                "swiss": 0.1,
                "chinese": 0.25,
                "thai": 0.25,
            },
            "dining_pref": {
                "Takeaway": 0.5,
                "Casual": 0.4,
                "A la carte": 0.05,
                "Set Menu / Chef's Menu": 0.02,
                "Date Night": 0.03,
            },
        },
        {
            "name": "foodie_experience",
            "weight": 1.0,
            "budget_mean": 2.6,
            "budget_imp_mean": 1.5,
            "cuisine_imp_mean": 2.7,
            "dining_imp_mean": 2.8,
            "cuisine_pref": {
                "italian": 0.3,
                "greek": 0.2,
                "swiss": 0.1,
                "chinese": 0.2,
                "thai": 0.2,
            },
            "dining_pref": {
                "Takeaway": 0.05,
                "Casual": 0.2,
                "A la carte": 0.35,
                "Set Menu / Chef's Menu": 0.25,
                "Date Night": 0.15,
            },
        },
        {
            "name": "mediterranean_comfort",
            "weight": 1.0,
            "budget_mean": 2.0,
            "budget_imp_mean": 2.0,
            "cuisine_imp_mean": 2.5,
            "dining_imp_mean": 2.0,
            "cuisine_pref": {
                "italian": 0.45,
                "greek": 0.35,
                "swiss": 0.1,
                "chinese": 0.05,
                "thai": 0.05,
            },
            "dining_pref": {
                "Takeaway": 0.1,
                "Casual": 0.5,
                "A la carte": 0.3,
                "Set Menu / Chef's Menu": 0.05,
                "Date Night": 0.05,
            },
        },
        {
            "name": "local_traditionalists",
            "weight": 0.8,
            "budget_mean": 2.3,
            "budget_imp_mean": 2.2,
            "cuisine_imp_mean": 2.4,
            "dining_imp_mean": 2.1,
            "cuisine_pref": {
                "italian": 0.15,
                "greek": 0.15,
                "swiss": 0.5,
                "chinese": 0.1,
                "thai": 0.1,
            },
            "dining_pref": {
                "Takeaway": 0.1,
                "Casual": 0.4,
                "A la carte": 0.3,
                "Set Menu / Chef's Menu": 0.15,
                "Date Night": 0.05,
            },
        },
        {
            "name": "asian_craving",
            "weight": 1.0,
            "budget_mean": 2.0,
            "budget_imp_mean": 1.8,
            "cuisine_imp_mean": 2.7,
            "dining_imp_mean": 2.0,
            "cuisine_pref": {
                "italian": 0.05,
                "greek": 0.05,
                "swiss": 0.05,
                "chinese": 0.45,
                "thai": 0.4,
            },
            "dining_pref": {
                "Takeaway": 0.35,
                "Casual": 0.4,
                "A la carte": 0.15,
                "Set Menu / Chef's Menu": 0.05,
                "Date Night": 0.05,
            },
        },
        {
            "name": "chill_flexible",
            "weight": 0.8,
            "budget_mean": 2.0,
            "budget_imp_mean": 2.0,
            "cuisine_imp_mean": 2.0,
            "dining_imp_mean": 2.0,
            "cuisine_pref": {
                "italian": 0.2,
                "greek": 0.2,
                "swiss": 0.2,
                "chinese": 0.2,
                "thai": 0.2,
            },
            "dining_pref": {
                "Takeaway": 0.25,
                "Casual": 0.4,
                "A la carte": 0.2,
                "Set Menu / Chef's Menu": 0.05,
                "Date Night": 0.1,
            },
        },
    ]

    weights = np.array([a["weight"] for a in archetypes], dtype=float)
    weights = weights / weights.sum()

    for _ in range(n):
        # Pick an archetype
        idx = rng.choice(len(archetypes), p=weights)
        a = archetypes[idx]

        # Sample numeric features around the means, with noise
        budget_numeric = np.clip(rng.normal(a["budget_mean"], 0.25), 1.0, 3.0)
        budget_imp = np.clip(rng.normal(a["budget_imp_mean"], 0.4), 1.0, 3.0)
        cuisine_imp = np.clip(rng.normal(a["cuisine_imp_mean"], 0.4), 1.0, 3.0)
        dining_imp = np.clip(rng.normal(a["dining_imp_mean"], 0.4), 1.0, 3.0)

        # Sample cuisine distribution from a Dirichlet around the archetype preferences
        cuisine_alpha = pref_to_array(a["cuisine_pref"], CUISINES) * 8.0
        cuisine_vec = rng.dirichlet(cuisine_alpha)

        # Sample dining style distribution
        dining_alpha = pref_to_array(a["dining_pref"], DINING_STYLES) * 8.0
        dining_vec = rng.dirichlet(dining_alpha)

        vec = [
            budget_numeric,
            budget_imp,
            cuisine_imp,
            dining_imp,
            *cuisine_vec,
            *dining_vec,
        ]
        vectors.append(vec)

    return vectors


def register_group_profile(feature_vector):
    """Store this group's feature vector in session_state AND on disk."""
    if feature_vector is None:
        return

    # Keep current session behaviour (optional)
    if "group_profile_vectors" not in st.session_state:
        st.session_state["group_profile_vectors"] = []
    st.session_state["group_profile_vectors"].append(feature_vector.tolist())

    # Append to CSV so it survives app restarts
    try:
        with DATA_FILE.open("a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(feature_vector.tolist())
    except Exception as e:
        st.warning(f"Could not save group profile to file: {e}")



def cluster_group_profiles():
    """
    Run K-Means on all stored group profiles (from CSV).
    Returns:
        labels  - cluster id per group
        centers - cluster centers
        current_group_label - cluster id of the current (last) dinner
    """
    vectors_list = []

    # If no data file yet, create synthetic examples
    if not DATA_FILE.exists():
        synthetic = generate_synthetic_group_profiles(n=50)
        try:
            with DATA_FILE.open("w", newline="") as f:
                writer = csv.writer(f)
                for vec in synthetic:
                    writer.writerow(vec)
        except Exception as e:
            st.warning(f"Could not create synthetic profiles file: {e}")

    # Load all historical profiles from CSV
    if DATA_FILE.exists():
        try:
            with DATA_FILE.open("r", newline="") as f:
                reader = csv.reader(f)
                for row in reader:
                    if not row:
                        continue
                    try:
                        vec = [float(x) for x in row]
                        vectors_list.append(vec)
                    except ValueError:
                        continue
        except Exception as e:
            st.warning(f"Could not read group profiles file: {e}")

    if len(vectors_list) == 0:
        return None, None, None

    X = np.array(vectors_list, dtype=float)
    n_groups = X.shape[0]

    # If only one dinner total, treat as one cluster
    if n_groups == 1:
        labels = np.array([0])
        centers = X.copy()
    else:
        n_clusters = min(6, n_groups)  # up to 6 group profile types
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
