
import streamlit as st
import numpy as np
from statistics import mode
from collections import Counter
import altair as alt
import pandas as pd
from sklearn.cluster import KMeans

from pathlib import Path  
import csv               
# Needed for AI implementation (group summary)
from explanation import generate_group_summary


 # List of all cuisine categories used in the project.
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

 ## Taste-Matrix for the ML clustering.
 # We transform each cuisine into 5 underlying taste dimensions:
 # 1) spice: how spicy the cuisine usually is
 # 2) hearty: how heavy/comfort-oriented the cuisine is
 # 3) healthy: how light/fresh/healthy the cuisine tends to be
 # 4) exotic: how adventurous/unusual/unique the flavours are
 # 5) light: how light/easy-to-digest the cuisine is

 # This matrix allows us to convert cuisine choices into a numerical
 # taste profile which makes the machine learning possible.

 # Important:
 # It is only used internally to build the ML feature vectors.

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
 # For the case that something goes wrong.
DEFAULT_TASTE = [2, 3, 3, 3, 3]


 ## Define function that converts each participants cuisine ranking into a 5D taste vector
 # We combine the 3 ranked cuisines (rank1 → weight 3, rank2 → weight 2, rank3 → weight 1)
 # into a weighted average taste profile for each participant
 # Result of the shape: (spice, hearty, healthy, exotic, light) = 5 dimensions

def build_participant_taste_vector(p):

     # Extract the ranked cuisines from this participants answers.
     # If the key does not exist, we use an empty list.
    ranked = p.get("ranked_cuisines", [])
    
     # If the participant has no ranked cuisines, 
     # return a neutral/default taste profile that was created before. 
    if not ranked:
        return np.array(DEFAULT_TASTE, dtype=float)

     # Ranking weights for rank positions
    weights = [3, 2, 1]  
     # Initialize a 5D vector of zeros to start accumulating the weighted taste values.
    taste_sum = np.zeros(5, dtype=float)
     # Stores the total weight applied, its always 6 for 3 cuisines.
    total_w = 0.0
   
     # Enumerate gets the index and cuisine from the ranked list.
     # We then loop through it get the correct weight for this rank and add that to the total weight,
     # and then add the cuisines taste vector multiplied by its weight to the taste sum.
    for i, cuisine in enumerate(ranked):
        if i >= 3:
            break
        w = weights[i]
        taste_sum += w * np.array(TASTE_MATRIX.get(cuisine, DEFAULT_TASTE))
        total_w += w
     
     # Divide by the total weight to produce the weighted average taste vector per participant.
    return taste_sum / total_w

 # These lines define settings and the file path used later for CSV writing.
EXPECTED_DIM = 6 # Budget + 5 taste values
BUDGET_DICT = {"$": 1, "$$": 2, "$$$": 3, "$$$$": 4}
REVERSE_BUDGET_DICT = {v: k for k, v in BUDGET_DICT.items()}

DATA_FILE = Path("group_profiles.csv")




 ## Define ML group feature vector function
 # We combine:
 # - average group budget (numeric)
 # - average taste values

def build_group_feature_vector(answers):
    if not answers:
        return None

    participant_vectors = []

    for p in answers:
         # Convert budget symbol to numeric (1–4)
        budget_num = float(BUDGET_DICT.get(p["budget"], 2))

         # Compute the participant’s taste vector (5D)
        taste_vec = build_participant_taste_vector(p)

         # Build the final participant vector shape:
         # [budget, spice, hearty, healthy, exotic, light]
        participant_vector = np.concatenate([[budget_num], taste_vec])

        participant_vectors.append(participant_vector)

     # Group vector = average of all participants
    group_vec = np.mean(participant_vectors, axis=0)

    return group_vec.astype(float)



 ## Synthetic training data (used when csv is empty in the beginning)
 # we generate "fake" taste profiles so that KMeans always has enough data to form clusters.
 # These represent the 4 general food profile archetypes.

def generate_synthetic_group_profiles(n=50):
    rng = np.random.default_rng(42)
    vectors = []

     # Hand written archetypes !!!!!
     # [budget, spice, hearty, healthy, exotic, light]
    archetypes = [
        np.array([1.5, 1.5, 4.5, 2.0, 2.0, 2.0]),  # Comfort Classics
        np.array([2.0, 4.5, 3.0, 2.0, 4.5, 2.0]),  # Adventurous Spice
        np.array([2.5, 1.5, 2.0, 4.5, 3.0, 4.5]),  # Fresh & Light
        np.array([3.5, 2.0, 3.0, 3.5, 3.0, 3.0]),  # Premium Gourmet
    ]
     # Loop n times (e.g., 50 times) to generate n synthetic taste profiles
    for _ in range(n):
         # Randmoly pick one of the four predefined taste archetypes.
         # Because RNG has a fixed seed, the selection is repeatable across runs -> results are stable.
        base = archetypes[rng.integers(0, len(archetypes))]
         # Create small random variations (6 numbers: budget + 5 taste dimensions).
         # Mean = 0 (centered), std = 0.4 (moderate variation).
         # This makes each synthetic profile similar but not identical to its archetype.
        noise = rng.normal(0, 0.4, size=6) 
         # Add the random noise to the chosen archetype to create a unique taste vector. 
        vec = base + noise
         
         # Ensure the budget value stays in the valid range.
         # Clipping prevents unrealistic values (< 1 or > 4).
        vec[0] = np.clip(vec[0], 1.0, 4.0)

         # Ensure taste value stays in valid range.
         # Clipping like before prevnts values outside range.
        vec[1:] = np.clip(vec[1:], 1.0, 5.0) 
         
         # Convert the NumPy array to a normal Python list
         # and add the synthetic taste profile to the final list.
        vectors.append(vec.tolist())
     # Afterwards return the complete dataset.
    return vectors



def register_group_profile(feature_vector):
    """Store this group's feature vector in session_state AND on disk."""
    if feature_vector is None:
        return
     ## Saves profiles in st.session_state
     # This keeps the current session's history available
     # but only as long as the app is open
    if "group_profile_vectors" not in st.session_state:
        st.session_state["group_profile_vectors"] = []
    st.session_state["group_profile_vectors"].append(feature_vector.tolist())

     ## Save the profiles permanently by adding them to CSV so it survives app restarts
     # Therefore the ML is able to learn over time
     # More data from each session is safed over time
    try:
        with DATA_FILE.open("a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(feature_vector.tolist())
     # Shows a warning if the saving fails. 
     # This is just for our information.
    except Exception as e:
        st.warning(f"Could not save group profile to file: {e}")


 ## Clustering on the vectors
 # This function loads all stored taste profiles (past groups) and
 # adds synthetic profiles if needed, and runs K-Means clustering.
 # It returns:
 # - all cluster labels
 # - the 4 cluster centers
 # - the cluster that today's group belongs to.


def cluster_group_profiles():
    vectors_list = [] # Contains all ML vectors (real + synthetic)

     # Load existing vectors from CSV (dimension must match 6)
    if DATA_FILE.exists():
        try:
             # Opens the CSV file in read mode and goes through each line
            with DATA_FILE.open("r", newline="") as f:
                reader = csv.reader(f)
                for row in reader:
                    try:
                         # Converts each value in the row from str to float -> creates a numeric vector
                        vec = [float(x) for x in row]
                         # only accepts rows that contain exactly 6 values
                        if len(vec) == 6:
                            vectors_list.append(vec)
                    except:
                        continue
        except:
            st.warning("Could not read existing ML vectors.")

     # If the file contains less than 20 vectors, then 40 synthetic get added
    if len(vectors_list) < 20:
        vectors_list.extend(generate_synthetic_group_profiles(n=40))

     # Save updated clean dataset back to CSV in write mode
    try:
        with DATA_FILE.open("w", newline="") as f:
            writer = csv.writer(f)
            for vec in vectors_list:
                writer.writerow(vec)
    except Exception as e:
        st.warning(f"Could not update ML dataset: {e}")

     # converts the pyhton list with the vectors into a Numpy array
    X = np.array(vectors_list)

     # Creates a K-Means model with:
     # -  4 clusters (group taste profiles)
     # - runs the clustering 10 times and chooses best result
     # - random_state=42 insures that the cluster starts at the same spot -> results stable and predictable
    kmeans = KMeans(
        n_clusters=4,
        n_init=10,
        random_state=42
    )
     # Runs K-Means on data and assigns each taste vector to a cluster
    labels = kmeans.fit_predict(X)

     # Gets the average taste profle of each cluster
    centers = kmeans.cluster_centers_

     # Gets the label of the last vector = label of the last group
    current_label = int(labels[-1])  # last = today's group

     # labels → cluster assignment for every vector
     # centers → the 4 cluster taste centers
     # current_label → the taste personality of today’s group
    return labels, centers, current_label



def describe_cluster_center(center):
     
     # Takes the numeric center of a cluster (the average taste profile) 
     # and translates it into a personality description.

     # Unpack the 6 values from the cluster center vector
     # center = [budget, spice, hearty, healthy, exotic, light]

    budget, spice, hearty, healthy, exotic, light = center

     # Determine the most dominant taste dimension
     # We therefore create a dictionary that maps each dimension name to its value.

    dims = {
        "spice": spice,
        "hearty": hearty,
        "healthy": healthy,
        "exotic": exotic,
        "light": light
    }

     # Find the key with the highest value.
     # Example: if 'spice' has the highest number, main_dim = "spice"
    main_dim = max(dims, key=dims.get)

     # Classify the cluster into one of the four taste personalities.
     # Each "if" block checks specific patterns in the taste values.
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

     ## Builds the full results page after all participants filled out the questionnaire.
     # It:
     # - calculates group budget, cuisine and walking distance
     # - visualizes the results with charts
     # - generates the ML group taste profile
     # - determines the group's cluster personality

     # Title
    st.title("This is your groups taste profile of today!")
    st.subheader("Let's analyze it.")
    st.header("Results Summary")

     ## BUDGET CALCULATION
     # Map each budget symbol to a number for easier averaging
    budget_dict = {"$": 1, "$$": 2, "$$$": 3, "$$$$": 4}

    budget_scores = [] # list for weighted budget values
    budget_weights = []  # list for importance weights
     
     # For each participant multiply numeric budget value × importance (1–3)
     # and append it to the lists
    for participant in answers:
        numeric_budget = budget_dict[participant["budget"]]
        imp = participant["budget_importance"]
        budget_scores.append(numeric_budget * imp)
        budget_weights.append(imp)
     
     # Calculate the weighted average
    group_budget = sum(budget_scores) / sum(budget_weights)
    rounded_budget = round(group_budget) # round to nearest whole number

     # Reverse map the number for displaying
    reverse_budget_dict = {1: "$", 2: "$$", 3: "$$$", 4: "$$$$"}

    budget_symbol_group = reverse_budget_dict.get(rounded_budget, "$")
    
     # Safe the value for the API request later
    st.session_state["group_budget_numeric"] = str(rounded_budget)

     ## CUISINE SCORING
     # Count how many points each cuisine gets:
     # Rank 1 → +3, Rank 2 → +2, Rank 3 → +1
     # and stores them in a Counter, example: {"Italian": 7, "Asian": 5, "Mexican": 3}
    cuisine_scores = Counter()
    for p in answers:
        for i, cuisine in enumerate(p["ranked_cuisines"]):
            cuisine_scores[cuisine] += (3 - i)
     
     # Pick the cuisine with the highest score = most_common
     # (1)[0][0] gets only the string, the cuisine name
    most_preferred_cuisine = (
        cuisine_scores.most_common(1)[0][0] if cuisine_scores else "unknown"
    )

     # Safe value for API request later
    st.session_state["group_cuisine"] = most_preferred_cuisine

     ## WALKING DISTANCE (METERS)
     # Convert labels → minutes for chart visualization
    DISTANCE_DICT = {
        "5 minutes": 500,
        "10 minutes": 900,
        "15 minutes": 1400,
        "No preference": 3000
    }

     # Weighed average (same logic as budget)
    walking_scores = []
    walking_weights = []
    for p in answers:
        walking_scores.append(DISTANCE_DICT[p["walking_distance"]] * p["walking_distance_importance"])
        walking_weights.append(p["walking_distance_importance"])

    group_walking_radius = sum(walking_scores) / sum(walking_weights)
    st.session_state["group_walking_radius"] = int(group_walking_radius)

     # Convert meters → label (for display)
    if group_walking_radius <= 700:
        walk_label = "5 minutes"
    elif group_walking_radius <= 1150:
        walk_label = "10 minutes"
    elif group_walking_radius <= 2000:
        walk_label = "15 minutes"
    else:
        walk_label = "No preference"

     ## SUMMARY METRICS
     # Displays the group values in 3 columns
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Budget Preference", budget_symbol_group)
    with col2:
        st.metric("Top Cuisine", most_preferred_cuisine)
    with col3:
        st.metric("Walking Distance", walk_label)

    st.markdown("---")

     ## IMPORTANCE BAR CHART
    st.subheader("Importance Distribution")
     
     # Create a small table showing the average importance value
     # for each category (1 = low importance, 3 = high importance)
    df_radar = pd.DataFrame({
        "category": ["Budget", "Cuisine", "Walking Distance"],
        "value": [
            np.mean([p["budget_importance"] for p in answers]),
            np.mean([p["cuisine_importance"] for p in answers]),
            np.mean([p["walking_distance_importance"] for p in answers])
        ]
    })

     # Build a simple bar chart with Altair
     # x-axis: the 3 categories
     # y-axis: the average importance values (1–3)
     # Altair gets the values directly from the df_radar
     # N = nominal -> name, label, Q= quanitative -> number
    chart = alt.Chart(df_radar).mark_bar().encode(
        x=alt.X("category:N", title="Category"),
        y=alt.Y("value:Q", title="Average Importance (1–3)"),
        color=alt.Color("category:N") # same color for category and legend
    )
     # Show the chart in Streamlit
    st.altair_chart(chart, use_container_width=True)

    st.markdown("---")

     ## CUISINE BAR CHART
    st.subheader("Cuisine Preference Strength")
    
     # Turn the cuisine_scores counter into a DataFrame
     # Example:
     #   Cuisine     Score
     #   Italian       8
     #   Asian         6

    df_cuisine = pd.DataFrame({
        "Cuisine": list(cuisine_scores.keys()),
        "Score": list(cuisine_scores.values())
    })
     # Build another bar chart:
     # - x-axis = score (how many points the cuisine got)
     # - y-axis = name of cuisine
     # - sorted by score (highest at top) = "-" in front of x means descending
    bar = alt.Chart(df_cuisine).mark_bar().encode(
        x="Score:Q",
        y=alt.Y("Cuisine:N", sort='-x'),
        color=alt.value("#55A868") # chose this custom green colour
    )
     # Streamlit show the chart
    st.altair_chart(bar, use_container_width=True)

    st.markdown("---")

   
     ## WALKING DISTANCE PIE CHART
    
    st.subheader("Walking Distance Preferences (Weighted)")
     
     # Convert the labels ( example "10 minutes") into numeric minutes
     # for easier grouping and plotting
    DISTANCE_TO_MINUTES = {
        "5 minutes": 5,
        "10 minutes": 10,
        "15 minutes": 15,
        "No preference": 20
    }

    
    walking_minutes_scores = {}

     # Build a dictionary that sums up all importance values per distance
     # Example:
     #   5 → 6 importance points
     #   10 → 9 importance points
    for p in answers:
        minutes = DISTANCE_TO_MINUTES[p["walking_distance"]]
        weight = p["walking_distance_importance"]

         # Adds the weight value to the minutes in the dictionary
        walking_minutes_scores[minutes] = walking_minutes_scores.get(minutes, 0) + weight

     # Convert this into a DataFrame for the pie chart
    df_walk = pd.DataFrame({
        "Walking Minutes": [f"{m} min" for m in walking_minutes_scores.keys()],
        "Weighted Importance": list(walking_minutes_scores.values())
    })

     # Create a pie chart showing how the importance is distributed
    walk_pie = alt.Chart(df_walk).mark_arc().encode(
        theta="Weighted Importance:Q", # angle = importance weight
        color="Walking Minutes:N",     # color-coded by distance option = altair automatically chooses different colours
        tooltip=["Walking Minutes:N", "Weighted Importance:Q"]
    )
    st.altair_chart(walk_pie, use_container_width=True)

    st.markdown("---")

    
     ## MACHINE LEARNING CLUSTERING
     # Create a 6D feature vector from the group’s answers
    group_vector = build_group_feature_vector(answers)

     # Save it for future ML training (CSV + session)
    register_group_profile(group_vector)

    st.subheader("Group Taste Profile (Machine Learning)")
     
     # Save it for future ML training (CSV + session)

    labels, centers, current_label = cluster_group_profiles()

     # If we do not have enough stored profiles yet, show a message
    if labels is None:
        st.info("Not enough past dinners yet — clustering will start after more sessions.")
    else:
         # Select the cluster center of today’s group
        center = centers[current_label]
         # Convert numeric cluster center -> personality name
        name, explanation, details = describe_cluster_center(center)
    
         # Display the final “taste personality”
         # Displays a green success message box in the streamlit app
        st.success(
            f"Tonight's group looks like: **{name}** "
            f"(Cluster {current_label + 1} of {len(set(labels))})"
        )
        st.write(explanation)

        # AI implementation: Group Summary
        # Gives all the necessary Info to the AI helper function and writes text based on this
        try:
            ai_input = {
                "cluster_name": name,
                "cluster_id": int(current_label),
                "budget_symbol_group": budget_symbol_group,
                "numeric_budget_group": rounded_budget,
                "top_cuisine_group": most_preferred_cuisine,
                "walking_distance_label_group": walk_label,
                "walking_radius_m_group": int(group_walking_radius),
            }

            # Call the AI helper to generate a short, fun summary text
            ai_summary_text = generate_group_summary(ai_input)

            st.subheader("AI Summary of Your Group")  # AI result headline
            st.info(ai_summary_text)                  # Shows AI text in a highlighted box
        except Exception as e:
            # Fallback so the app never crashes because of AI issues
            st.caption(f"(AI group summary could not be generated: {e})")


         # Save cluster info for the API page
        st.session_state["current_group_cluster_id"] = int(current_label)
        st.session_state["current_group_cluster_name"] = name

    # Button to go to restaurant results
    if st.button("Find matching Restaurants!"):
        st.session_state["page"] = "api"
        st.rerun()





