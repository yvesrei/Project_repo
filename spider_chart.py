
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
CUISINES = [
    "Italian",
    "Asian",
    "Swiss / Alpine",
    "Mediterranean",
    "American",
    "Middle Eastern",
    "Latin American",
    "Indian / South Asian",
    "Vegetarian / Vegan",
    "Seafood & Sushi"
]

DINING_STYLES = [
    "Takeaway",
    "Casual",
    "A la carte",
    "Set Menu / Chef's Menu",
    "Date Night",
]

EXPECTED_DIM = 4 + len(CUISINES) + len(DINING_STYLES)
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
                "Italian": 0.12,
                "Asian": 0.28,
                "Swiss / Alpine": 0.06,
                "Mediterranean": 0.18,
                "American": 0.10,
                "Middle Eastern": 0.06,
                "Latin American": 0.06,
                "Indian / South Asian": 0.06,
                "Vegetarian / Vegan": 0.05,
                "Seafood & Sushi": 0.03
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
                "Italian": 0.20,
                "Asian": 0.18,
                "Swiss / Alpine": 0.08,
                "Mediterranean": 0.20,
                "American": 0.06,
                "Middle Eastern": 0.08,
                "Latin American": 0.08,
                "Indian / South Asian": 0.06,
                "Vegetarian / Vegan": 0.04,
                "Seafood & Sushi": 0.12
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
                "Italian": 0.35,
                "Asian": 0.08,
                "Swiss / Alpine": 0.10,
                "Mediterranean": 0.30,
                "American": 0.04,
                "Middle Eastern": 0.05,
                "Latin American": 0.02,
                "Indian / South Asian": 0.02,
                "Vegetarian / Vegan": 0.03,
                "Seafood & Sushi": 0.01
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
                "Italian": 0.10,
                "Asian": 0.05,
                "Swiss / Alpine": 0.55,
                "Mediterranean": 0.10,
                "American": 0.05,
                "Middle Eastern": 0.04,
                "Latin American": 0.03,
                "Indian / South Asian": 0.03,
                "Vegetarian / Vegan": 0.03,
                "Seafood & Sushi": 0.02
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
                "Italian": 0.03,
                "Asian": 0.60,
                "Swiss / Alpine": 0.04,
                "Mediterranean": 0.08,
                "American": 0.05,
                "Middle Eastern": 0.03,
                "Latin American": 0.04,
                "Indian / South Asian": 0.08,
                "Vegetarian / Vegan": 0.03,
                "Seafood & Sushi": 0.02
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
                "Italian": 0.12,
                "Asian": 0.12,
                "Swiss / Alpine": 0.12,
                "Mediterranean": 0.12,
                "American": 0.12,
                "Middle Eastern": 0.10,
                "Latin American": 0.08,
                "Indian / South Asian": 0.08,
                "Vegetarian / Vegan": 0.08,
                "Seafood & Sushi": 0.06
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
                        # ⚠️ Skip old rows with wrong vector length
                        if len(vec) == EXPECTED_DIM:
                            vectors_list.append(vec)
                    except ValueError:
                        continue
        except Exception as e:
            st.warning(f"Could not read group profiles file: {e}")


    # 🔴 NEW: if file exists but has too few rows (e.g. only 1),
    # top it up with synthetic profiles so we have at least 50 total.
    if len(vectors_list) < 50:
        needed = 50 - len(vectors_list)
        synthetic_extra = generate_synthetic_group_profiles(n=needed)
        vectors_list.extend(synthetic_extra)

        # Also append these extra ones to the CSV so it stays in sync
        try:
            with DATA_FILE.open("a", newline="") as f:
                writer = csv.writer(f)
                for vec in synthetic_extra:
                    writer.writerow(vec)
        except Exception as e:
            st.warning(f"Could not extend group profiles file: {e}")

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
        # --------- naming logic based on new 10 cuisine groups ---------
    name = "Chill Whatever-Works Group"
    explanation = (
        "Balanced preferences without strong extremes. Your group is flexible across all dimensions."
    )

    # Cheap & Cheerful Squad
    if budget_numeric <= 1.6 and main_importance == "budget" and top_dining in ["Takeaway", "Casual"]:
        name = "Cheap & Cheerful Squad"
        explanation = (
            "Your group strongly prioritises a low budget and leans towards relaxed, casual places. "
            "Cuisine is flexible as long as it’s affordable and easy-going."
        )

    # Foodie Experience Hunters
    elif budget_numeric >= 2.4 and main_importance in ["cuisine", "dining"] and top_dining in [
        "A la carte", "Set Menu / Chef's Menu", "Date Night"
    ]:
        name = "Foodie Experience Hunters"
        explanation = (
            "Your group is willing to spend more for a memorable dining experience. "
            "Cuisine and ambience are highly valued."
        )

    # --------- cuisine-driven clusters (new 10 categories) ---------

    # Italian Comfort Crowd
    elif top_cuisine == "Italian":
        name = "Italian Comfort Crowd"
        explanation = (
            "Your group loves classic Italian comfort — pasta, pizza, trattorias or modern Italian kitchens. "
            "Warm, familiar flavours feel just right."
        )

    # Asian Craving Crew
    elif top_cuisine == "Asian":
        name = "Asian Craving Crew"
        explanation = (
            "Your group has a clear preference for Asian flavours — whether it’s sushi, ramen, Thai or Chinese. "
            "Bold flavours and variety matter most tonight."
        )

    # Local Traditionalists
    elif top_cuisine == "Swiss / Alpine":
        name = "Local Traditionalists"
        explanation = (
            "Your group leans toward Swiss and Alpine favourites — classic comfort food and familiar dishes."
        )

    # Mediterranean Lovers
    elif top_cuisine == "Mediterranean":
        name = "Mediterranean Lovers"
        explanation = (
            "Your group prefers Mediterranean flavours — Greek, Spanish, Italian influence or coastal dishes. "
            "Warm, shareable, comforting foods define your taste."
        )

    # All-American Crowd
    elif top_cuisine == "American":
        name = "All-American Crowd"
        explanation = (
            "Your group enjoys American-style food — burgers, BBQ, diners or steakhouses. "
            "Hearty, satisfying meals matter most tonight."
        )

    # Middle Eastern Enthusiasts
    elif top_cuisine == "Middle Eastern":
        name = "Middle Eastern Enthusiasts"
        explanation = (
            "Your group is drawn to Middle Eastern flavours — Lebanese, Persian or Arabic dishes. "
            "You enjoy rich spices, grills, mezze and warm hospitality."
        )

    # Latin American Heat Seekers
    elif top_cuisine == "Latin American":
        name = "Latin American Heat Seekers"
        explanation = (
            "Your group loves the vibrant variety of Latin American cuisines — Mexican, Brazilian or Peruvian."
        )

    # Indian / South Asian Spice Lovers
    elif top_cuisine == "Indian / South Asian":
        name = "South Asian Spice Lovers"
        explanation = (
            "Your group clearly enjoys Indian or South Asian flavours — aromatic spices, curries and bold tastes."
        )

    # Plant-Based Preference Group
    elif top_cuisine == "Vegetarian / Vegan":
        name = "Plant-Based Preference Group"
        explanation = (
            "Your group shows a strong preference for vegetarian or vegan options — health-conscious and flavourful."
        )

    # Seafood / Sushi Lovers
    elif top_cuisine == "Seafood & Sushi":
        name = "Seafood & Sushi Lovers"
        explanation = (
            "Your group gravitates towards seafood, sushi, and fresh ocean flavours."
        )


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

    # Save cuisine for the API
    st.session_state["group_cuisine"] = most_preferred_cuisine


    
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

    # MACHINE LEARNING – GROUP PROFILE CLUSTERING
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

        # Store for other pages (e.g. API page)
        st.session_state["current_group_cluster_id"] = int(current_label)
        st.session_state["current_group_cluster_name"] = name

    if st.button("Find matching Restaurants!"):
        st.session_state["page"] = "api"
        st.rerun()

