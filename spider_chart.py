
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



EXPECTED_DIM = 5 + len(CUISINES)
BUDGET_DICT = {"$": 1, "$$": 2, "$$$": 3, "$$$$": 4}
REVERSE_BUDGET_DICT = {v: k for k, v in BUDGET_DICT.items()}

DATA_FILE = Path("group_profiles.csv")


def build_group_feature_vector(answers):
    """
    Build ONE numeric vector that represents the entire group.
    Uses:
    - weighted average budget
    - weighted walking distance (meters)
    - average importances
    - normalized cuisine score distribution
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

    # ---- walking distance ----
    DISTANCE_DICT = {
        "5 minutes": 500,
        "10 minutes": 900,
        "15 minutes": 1400,
        "No preference": 3000
    }

    walking_scores = []
    walking_weights = []

    for p in answers:
        walk_radius = DISTANCE_DICT[p["walking_distance"]]
        imp = p["walking_distance_importance"]
        walking_scores.append(walk_radius * imp)
        walking_weights.append(imp)

    group_walking_radius = sum(walking_scores) / sum(walking_weights)

    # ---- importances averages ----
    budget_imp_avg = np.mean([p["budget_importance"] for p in answers])
    cuisine_imp_avg = np.mean([p["cuisine_importance"] for p in answers])
    walking_imp_avg = np.mean([p["walking_distance_importance"] for p in answers])

    # ---- cuisine scores ----
    cuisine_scores = Counter()
    for p in answers:
        ranked = p["ranked_cuisines"]
        for i, cuisine in enumerate(ranked):
            weight = 3 - i   # rank1=3, rank2=2, rank3=1
            cuisine_scores[cuisine] += weight

    cuisine_vec = [cuisine_scores.get(c, 0) for c in CUISINES]
    total_cuisine = sum(cuisine_vec) or 1
    cuisine_vec_norm = [x / total_cuisine for x in cuisine_vec]

    return np.array([
        group_budget_numeric,
        group_walking_radius,
        budget_imp_avg,
        cuisine_imp_avg,
        walking_imp_avg,
        *cuisine_vec_norm
    ], dtype=float)


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
        

        # Sample cuisine distribution from a Dirichlet around the archetype preferences
        cuisine_alpha = pref_to_array(a["cuisine_pref"], CUISINES) * 8.0
        cuisine_vec = rng.dirichlet(cuisine_alpha)

        # Sample dining style distribution
        vec = [
            budget_numeric,
            1000,  # average walking radius placeholder
            budget_imp,
            cuisine_imp,
            2.0,   # walking importance placeholder
            *cuisine_vec
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
    # --- Ensure we have at least 50 profiles in memory ---
    if len(vectors_list) < 50:
        needed = 50 - len(vectors_list)
        synthetic_extra = generate_synthetic_group_profiles(n=needed)
        vectors_list.extend(synthetic_extra)

    # Try writing them to CSV; if writing fails, recreate the whole file
    try:
        with DATA_FILE.open("w", newline="") as f:  # overwrite completely
            writer = csv.writer(f)
            for vec in vectors_list:  # write ALL valid vectors
                writer.writerow(vec)
    except Exception as e:
        st.warning("⚠️ Could not update profiles file — recreating it fresh.")
        try:
            with DATA_FILE.open("w", newline="") as f:
                writer = csv.writer(f)
                for vec in vectors_list:
                    writer.writerow(vec)
        except Exception:
            st.error("❌ Could not recreate the group profiles file at all.")


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

    # Unpack feature vector
    budget_numeric = center[0]
    walking_radius = center[1]
    budget_imp, cuisine_imp, walking_imp = center[2:5]

    # Cuisine distribution
    cuisine_vec = center[5:5 + n_cuisines]

    # Top cuisines
    top_cuisine_idx = int(np.argmax(cuisine_vec))
    top_cuisine = CUISINES[top_cuisine_idx]

    if n_cuisines > 1:
        second_cuisine_idx = int(np.argsort(cuisine_vec)[-2])
    else:
        second_cuisine_idx = top_cuisine_idx
    second_cuisine = CUISINES[second_cuisine_idx]

    # Determine most important dimension
    vals = {
        "budget": float(budget_imp),
        "cuisine": float(cuisine_imp),
        "walking": float(walking_imp),
    }
    main_importance = max(vals, key=vals.get)

    # ==========================================
    # CLUSTER NAMING LOGIC (FINAL VERSION)
    # ==========================================

    # -------- Cheap & Cheerful Squad --------
    if budget_numeric <= 1.6 and main_importance == "budget":
        name = "Cheap & Cheerful Squad"
        explanation = (
            "Your group strongly prioritises a low budget and prefers easy, nearby options. "
            "Cuisine is flexible as long as it's affordable and convenient."
        )
        return name, explanation, {
            "budget_level": "$" if budget_numeric < 1.5 else "$$",
            "main_cuisine": top_cuisine,
            "second_cuisine": second_cuisine,
            "main_importance_dimension": main_importance,
            "walking_radius": int(walking_radius)
        }

    # -------- Foodie Experience Hunters --------
    elif budget_numeric >= 2.4 and main_importance == "cuisine" and walking_radius > 900:
        name = "Foodie Experience Hunters"
        explanation = (
            "Your group is willing to spend more and walk further for a memorable dining experience. "
            "Cuisine quality matters the most."
        )
        return name, explanation, {
            "budget_level": "$$" if budget_numeric < 2.5 else "$$$",
            "main_cuisine": top_cuisine,
            "second_cuisine": second_cuisine,
            "main_importance_dimension": main_importance,
            "walking_radius": int(walking_radius)
        }

    # ==========================================
    # CUISINE-ONLY CLUSTERS (ALWAYS MATCH TOP CUISINE)
    # ==========================================
    if top_cuisine == "Italian":
        name = "Italian Comfort Crowd"
        explanation = (
            "Your group loves classic Italian comfort — pasta, pizza, trattorias or modern Italian kitchens."
        )

    elif top_cuisine == "Asian":
        name = "Asian Craving Crew"
        explanation = (
            "Your group clearly prefers Asian flavours — sushi, ramen, Thai, Chinese, or fusion."
        )

    elif top_cuisine == "Swiss / Alpine":
        name = "Local Traditionalists"
        explanation = (
            "Your group leans toward Swiss and Alpine favourites — classic comfort food with local roots."
        )

    elif top_cuisine == "Mediterranean":
        name = "Mediterranean Lovers"
        explanation = (
            "Your group enjoys Mediterranean flavours — Greek, Spanish, Italian influence or coastal dishes."
        )

    elif top_cuisine == "American":
        name = "All-American Crowd"
        explanation = (
            "Your group enjoys American-style food — burgers, BBQ, diners or steakhouses."
        )

    elif top_cuisine == "Middle Eastern":
        name = "Middle Eastern Enthusiasts"
        explanation = (
            "Your group is drawn to Middle Eastern flavours — grills, mezze, spices, and warm hospitality."
        )

    elif top_cuisine == "Latin American":
        name = "Latin American Heat Seekers"
        explanation = (
            "Your group loves vibrant Latin American flavours — Mexican, Brazilian, Peruvian or fusion."
        )

    elif top_cuisine == "Indian / South Asian":
        name = "South Asian Spice Lovers"
        explanation = (
            "Your group clearly enjoys Indian or South Asian flavours — aromatic spices and bold tastes."
        )

    elif top_cuisine == "Vegetarian / Vegan":
        name = "Plant-Based Preference Group"
        explanation = (
            "Your group shows a strong preference for vegetarian or vegan options."
        )

    elif top_cuisine == "Seafood & Sushi":
        name = "Seafood & Sushi Lovers"
        explanation = (
            "Your group gravitates towards seafood, sushi, and fresh ocean flavours."
        )

    # ------------------------------------------
    # DEFAULT RETURN (always cuisine-aligned)
    # ------------------------------------------
    budget_level = (
        "$" if budget_numeric < 1.5 else
        "$$" if budget_numeric < 2.5 else
        "$$$"
    )

    details = {
        "budget_level": budget_level,
        "main_cuisine": top_cuisine,
        "second_cuisine": second_cuisine,
        "main_importance_dimension": main_importance,
        "walking_radius": int(walking_radius)
    }

    return name, explanation, details




def group_taste_profile(answers):

    # Title
    st.title("This is your groups taste profile of today!")
    st.subheader("Let's analyze it.")
    st.header("Results Summary")

    # ---- BUDGET CALCULATION ----
    budget_dict = {"$": 1, "$$": 2, "$$$": 3}
    budget_scores = []
    budget_weights = []

    for participant in answers:
        numeric_budget = budget_dict[participant["budget"]]
        imp = participant["budget_importance"]
        budget_scores.append(numeric_budget * imp)
        budget_weights.append(imp)

    group_budget = sum(budget_scores) / sum(budget_weights)
    rounded_budget = round(group_budget)

    reverse_budget_dict = {1: "$", 2: "$$", 3: "$$$"}
    budget_symbol_group = reverse_budget_dict.get(rounded_budget, "$")

    st.session_state["group_budget_numeric"] = str(rounded_budget)

    # ---- CUISINE SCORING ----
    cuisine_scores = Counter()
    for p in answers:
        for i, cuisine in enumerate(p["ranked_cuisines"]):
            cuisine_scores[cuisine] += (3 - i)

    most_preferred_cuisine = (
        cuisine_scores.most_common(1)[0][0] if cuisine_scores else "unknown"
    )
    st.session_state["group_cuisine"] = most_preferred_cuisine

    # ---- WALKING DISTANCE (METERS) ----
    DISTANCE_DICT = {
        "5 minutes": 500,
        "10 minutes": 900,
        "15 minutes": 1400,
        "No preference": 3000
    }

    walking_scores = []
    walking_weights = []
    for p in answers:
        walking_scores.append(DISTANCE_DICT[p["walking_distance"]] * p["walking_distance_importance"])
        walking_weights.append(p["walking_distance_importance"])

    group_walking_radius = sum(walking_scores) / sum(walking_weights)
    st.session_state["group_walking_radius"] = int(group_walking_radius)

    # Convert meters → label
    if group_walking_radius <= 700:
        walk_label = "5 minutes"
    elif group_walking_radius <= 1150:
        walk_label = "10 minutes"
    elif group_walking_radius <= 2000:
        walk_label = "15 minutes"
    else:
        walk_label = "No preference"

    # ---- SUMMARY METRICS ----
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Budget Preference", budget_symbol_group)
    with col2:
        st.metric("Top Cuisine", most_preferred_cuisine)
    with col3:
        st.metric("Walking Distance", walk_label)

    st.markdown("---")

    # ---- IMPORTANCE BAR CHART ----
    st.subheader("Importance Distribution")

    df_radar = pd.DataFrame({
        "category": ["Budget", "Cuisine", "Walking Distance"],
        "value": [
            np.mean([p["budget_importance"] for p in answers]),
            np.mean([p["cuisine_importance"] for p in answers]),
            np.mean([p["walking_distance_importance"] for p in answers])
        ]
    })

    chart = alt.Chart(df_radar).mark_bar().encode(
        x=alt.X("category:N", title="Category"),
        y=alt.Y("value:Q", title="Average Importance (1–3)"),
        color=alt.Color("category:N")
    )
    st.altair_chart(chart, use_container_width=True)

    st.markdown("---")

    # ---- CUISINE BAR CHART ----
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

    # ------------------------------------------
    # WALKING DISTANCE PIE CHART (FIXED)
    # ------------------------------------------
    st.subheader("Walking Distance Preferences (Weighted)")

    DISTANCE_TO_MINUTES = {
        "5 minutes": 5,
        "10 minutes": 10,
        "15 minutes": 15,
        "No preference": 20
    }

    walking_minutes_scores = {}
    for p in answers:
        minutes = DISTANCE_TO_MINUTES[p["walking_distance"]]
        weight = p["walking_distance_importance"]
        walking_minutes_scores[minutes] = walking_minutes_scores.get(minutes, 0) + weight

    df_walk = pd.DataFrame({
        "Walking Minutes": [f"{m} min" for m in walking_minutes_scores.keys()],
        "Weighted Importance": list(walking_minutes_scores.values())
    })

    walk_pie = alt.Chart(df_walk).mark_arc().encode(
        theta="Weighted Importance:Q",
        color="Walking Minutes:N",
        tooltip=["Walking Minutes:N", "Weighted Importance:Q"]
    )
    st.altair_chart(walk_pie, use_container_width=True)

    st.markdown("---")

    # ------------------------------------------
    # MACHINE LEARNING CLUSTERING
    # ------------------------------------------
    group_vector = build_group_feature_vector(answers)
    register_group_profile(group_vector)

    st.subheader("Group Taste Profile (Machine Learning)")

    labels, centers, current_label = cluster_group_profiles()

    if labels is None:
        st.info("Not enough past dinners yet — clustering will start after more sessions.")
    else:
        center = centers[current_label]
        name, explanation, details = describe_cluster_center(center)

        st.success(
            f"Tonight's group looks like: **{name}** "
            f"(Cluster {current_label + 1} of {len(set(labels))})"
        )
        st.write(explanation)

        st.session_state["current_group_cluster_id"] = int(current_label)
        st.session_state["current_group_cluster_name"] = name

    if st.button("Find matching Restaurants!"):
        st.session_state["page"] = "api"
        st.rerun()





