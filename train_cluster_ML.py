# This will be the training script for the ML

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
import joblib

# ------------------------------------------------------------
# GENERATE SYNTHETIC TRAINING DATA
# ------------------------------------------------------------
# We simulate 3 realistic “group taste profiles”
# so the ML model learns to distinguish between them.

N = 300  # number of synthetic samples

# Cluster 0: Budget-Friendly Casual Eaters
cluster0 = pd.DataFrame({
    "budget_numeric": np.random.normal(1.5, 0.3, N),
    "budget_importance": np.random.normal(2.5, 0.3, N),
    "cuisine_importance": np.random.normal(1.5, 0.3, N),
    "dining_importance": np.random.normal(2.0, 0.3, N),
    "top_cuisine_score": np.random.normal(4, 1, N),
    "cuisine_diversity": np.random.normal(2.5, 0.5, N),
})

# Cluster 1: Premium Fine Dining Lovers
cluster1 = pd.DataFrame({
    "budget_numeric": np.random.normal(2.8, 0.2, N),
    "budget_importance": np.random.normal(1.5, 0.3, N),
    "cuisine_importance": np.random.normal(2.5, 0.3, N),
    "dining_importance": np.random.normal(2.8, 0.2, N),
    "top_cuisine_score": np.random.normal(8, 1, N),
    "cuisine_diversity": np.random.normal(3.0, 0.7, N),
})

# Cluster 2: Adventurous Global Foodies
cluster2 = pd.DataFrame({
    "budget_numeric": np.random.normal(2.2, 0.3, N),
    "budget_importance": np.random.normal(1.8, 0.3, N),
    "cuisine_importance": np.random.normal(2.8, 0.3, N),
    "dining_importance": np.random.normal(2.0, 0.3, N),
    "top_cuisine_score": np.random.normal(9, 1, N),
    "cuisine_diversity": np.random.normal(5.5, 0.7, N),
})

# Combine all samples
df = pd.concat([cluster0, cluster1, cluster2], ignore_index=True)

# ------------------------------------------------------------
# TRAIN KMEANS CLUSTERING MODEL
# ------------------------------------------------------------
kmeans = KMeans(n_clusters=3, random_state=42)
kmeans.fit(df)

# ------------------------------------------------------------
# SAVE THE MODEL
# ------------------------------------------------------------
joblib.dump(kmeans, "cluster_model.pkl")

print("Model trained and saved as cluster_model.pkl")

