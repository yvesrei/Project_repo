
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

# NEW: Taste-Matrix for real ML clustering
# --------------------------------------------------------------
# We transform each cuisine into 5 underlying taste dimensions:
# 1) spice     - how spicy the cuisine usually is (1–5)
# 2) hearty    - how heavy/comfort-oriented the cuisine is (1–5)
# 3) healthy   - how light/fresh/healthy the cuisine tends to be (1–5)
# 4) exotic    - how adventurous/unusual/unique the flavours are (1–5)
# 5) light     - how light/easy-to-digest the cuisine is (1–5)
#
# This matrix allows us to convert cuisine choices into a numerical
# taste profile — which makes real machine learning possible.
#
# IMPORTANT:
# This does NOT replace the questionnaire or UI logic.
# It is ONLY used internally to build the ML feature vectors.

TASTE_MATRIX = {
    "Italian":              [1, 4, 2, 1, 3],
    "Asian":                [3, 2, 3, 4, 3],
    "Swiss / Alpine":       [1, 5, 2, 1, 1],
    "Mediterranean":        [1, 3, 5, 2, 4],
    "American":             [1, 5, 1, 1, 1],
    "Middle Eastern":       [3, 4, 3, 4, 2],
    "Latin American":       [3, 3, 2, 4, 2],
    "Indian / South Asian": [5, 4, 2, 5, 1],
    "Vegetarian / Vegan":   [1, 2, 5, 2, 5],
    "Seafood & Sushi":      [1, 2, 5, 3, 5]
}
DEFAULT_TASTE = [2, 3, 3, 3, 3]

# --------------------------------------------------------------
# NEW: Convert participant's cuisine ranking into a 5D taste vector
# --------------------------------------------------------------
# We combine the 3 ranked cuisines (rank1 → weight 3, rank2 → weight 2, rank3 → weight 1)
# into a weighted average taste profile.
# Result shape: [spice, hearty, healthy, exotic, light]
# This is one of the core components for real machine learning.
# --------------------------------------------------------------

def build_participant_taste_vector(p):
    ranked = p.get("ranked_cuisines", [])

    if not ranked:
        return np.array(DEFAULT_TASTE, dtype=float)

    weights = [3, 2, 1]   # rank weights
    taste_sum = np.zeros(5, dtype=float)
    total_w = 0.0

    for i, cuisine in enumerate(ranked):
        if i >= 3:
            break
        w = weights[i]
        taste_sum += w * np.array(TASTE_MATRIX.get(cuisine, DEFAULT_TASTE))
        total_w += w

    return taste_sum / total_w


EXPECTED_DIM = 6
BUDGET_DICT = {"$": 1, "$$": 2, "$$$": 3, "$$$$": 4}
REVERSE_BUDGET_DICT = {v: k for k, v in BUDGET_DICT.items()}

DATA_FILE = Path("group_profiles.csv")

# --------------------------------------------------------------
# NEW: Auto-reset group_profiles.csv if old ML vectors exist
# --------------------------------------------------------------
# We used an old ML system before with 15+ dimensions.
# The new ML system uses EXACTLY 6 dimensions:
#   [budget, spice, hearty, healthy, exotic, light]
#
# If the CSV contains any vectors with a different length,
# we delete the file automatically and start fresh.
# This prevents ML errors and means the user does NOT need
# to manually delete files on their machine.
# --------------------------------------------------------------

if DATA_FILE.exists():
    try:
        with DATA_FILE.open("r", newline="") as f:
            reader = csv.reader(f)
            rows = [row for row in reader]

        # check if ANY row has the wrong length
        wrong_format = any(len(row) != 6 for row in rows if row)

        if wrong_format:
            DATA_FILE.unlink()  # delete file
            print("⚠ group_profiles.csv reset automatically (old ML format detected)")
    except Exception as e:
        print(f"⚠ Could not validate CSV: {e}")


# --------------------------------------------------------------
# NEW ML FEATURE VECTOR
# --------------------------------------------------------------
# We completely replace the old ML vector with a simple, clean one:
#
#   [ budget_numeric, spice, hearty, healthy, exotic, light ]
#
# This does NOT affect UI, charts, summaries or restaurant search.
# It ONLY affects machine learning clustering.
#
# The old feature vector is not deleted; it is just not used anymore.
# --------------------------------------------------------------

def build_group_feature_vector(answers):
    if not answers:
        return None

    participant_vectors = []

    for p in answers:
        # Convert budget symbol to numeric (1–4)
        budget_num = float(BUDGET_DICT.get(p["budget"], 2))

        # Compute the participant’s taste vector (5D)
        taste_vec = build_participant_taste_vector(p)

        # Build final participant vector shape:
        # [budget, spice, hearty, healthy, exotic, light]
        participant_vector = np.concatenate([[budget_num], taste_vec])

        participant_vectors.append(participant_vector)

    # Group vector = mean of all participants
    group_vec = np.mean(participant_vectors, axis=0)

    return group_vec.astype(float)



# --------------------------------------------------------------
# NEW: Synthetic training data for 6-dimensional ML vectors
# --------------------------------------------------------------
# This replaces the old synthetic profiles completely.
# Every synthetic vector has the shape:
#   [budget, spice, hearty, healthy, exotic, light]
# --------------------------------------------------------------

def generate_synthetic_group_profiles(n=50):
    rng = np.random.default_rng(42)
    vectors = []

    # Archetype centers (hand-designed)
    # [budget, spice, hearty, healthy, exotic, light]
    archetypes = [
        np.array([1.5, 1.5, 4.5, 2.0, 2.0, 2.0]),  # Comfort Classics
        np.array([2.0, 4.5, 3.0, 2.0, 4.5, 2.0]),  # Adventurous Spice
        np.array([2.5, 1.5, 2.0, 4.5, 3.0, 4.5]),  # Fresh & Light
        np.array([3.5, 2.0, 3.0, 3.5, 3.0, 3.0]),  # Premium Gourmet
    ]

    for _ in range(n):
        base = archetypes[rng.integers(0, len(archetypes))]

        noise = rng.normal(0, 0.4, size=6)  
        vec = base + noise

        vec[0] = np.clip(vec[0], 1.0, 4.0)   # budget 1–4
        vec[1:] = np.clip(vec[1:], 1.0, 5.0) # taste dims 1–5

        vectors.append(vec.tolist())

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



# --------------------------------------------------------------
# NEW: K-Means Clustering on the NEW ML Vectors
# --------------------------------------------------------------
# We now cluster ONLY the 6-dimensional ML-vectors created above.
# This clustering is independent of the UI and works fully on
# taste patterns derived from cuisine + budget.
#
# Output: 4 general taste-based group types (clusters).
# --------------------------------------------------------------

def cluster_group_profiles():
    vectors_list = []

    # Load existing vectors from CSV (dimension must match 6)
    if DATA_FILE.exists():
        try:
            with DATA_FILE.open("r", newline="") as f:
                reader = csv.reader(f)
                for row in reader:
                    try:
                        vec = [float(x) for x in row]
                        if len(vec) == 6:
                            vectors_list.append(vec)
                    except:
                        continue
        except:
            st.warning("Could not read existing ML vectors.")

    # If file empty → create sweet synthetic training data
    if len(vectors_list) < 20:
        vectors_list.extend(generate_synthetic_group_profiles(n=40))

    X = np.array(vectors_list)

    # Run K-Means
    kmeans = KMeans(
        n_clusters=4,
        n_init=10,
        random_state=42
    )
    labels = kmeans.fit_predict(X)
    centers = kmeans.cluster_centers_

    current_label = int(labels[-1])  # last = today's group

    return labels, centers, current_label




# --------------------------------------------------------------
# NEW: Cluster interpretation for NEW ML vectors
# --------------------------------------------------------------
# center = [budget, spice, hearty, healthy, exotic, light]
# We derive 4 cluster personalities:
#
#   1) Adventurous Spice Explorers
#   2) Fresh & Light Foodies
#   3) Comfort Classics Crowd
#   4) Premium Gourmet Group
#
# These are general taste personalities — NOT based on kitchens.
# --------------------------------------------------------------

def describe_cluster_center(center):
    budget, spice, hearty, healthy, exotic, light = center

    # Determine most dominant taste dimension
    dims = {
        "spice": spice,
        "hearty": hearty,
        "healthy": healthy,
        "exotic": exotic,
        "light": light
    }
    main_dim = max(dims, key=dims.get)

    # Now classify cluster
    if spice >= 3.8 and exotic >= 3.8:
        return (
            "Adventurous Spice Explorers",
            "Your group enjoys bold, spicy and adventurous flavours.",
            {"main_dimension": "spice + exotic"}
        )

    elif healthy >= 3.8 and light >= 3.8:
        return (
            "Fresh & Light Foodies",
            "Your group prefers fresh, balanced, light dishes.",
            {"main_dimension": "healthy + light"}
        )

    elif hearty >= 3.8 and budget <= 2.5:
        return (
            "Comfort Classics Crowd",
            "Your group loves comforting, hearty, familiar foods.",
            {"main_dimension": "hearty"}
        )

    else:
        return (
            "Premium Gourmet Group",
            "Your group appreciates more refined, balanced and high-quality dishes.",
            {"main_dimension": main_dim}
        )





def group_taste_profile(answers):

    # Title
    st.title("This is your groups taste profile of today!")
    st.subheader("Let's analyze it.")
    st.header("Results Summary")

    # ---- BUDGET CALCULATION ----
    budget_dict = {"$": 1, "$$": 2, "$$$": 3, "$$$$": 4}

    budget_scores = []
    budget_weights = []

    for participant in answers:
        numeric_budget = budget_dict[participant["budget"]]
        imp = participant["budget_importance"]
        budget_scores.append(numeric_budget * imp)
        budget_weights.append(imp)

    group_budget = sum(budget_scores) / sum(budget_weights)
    rounded_budget = round(group_budget)

    reverse_budget_dict = {1: "$", 2: "$$", 3: "$$$", 4: "$$$$"}

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





