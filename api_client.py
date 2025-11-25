#Placeholder
import streamlit as st
import requests

    
API_KEY = "7orLYaGwCifLnM0Ok6aMRFsdutKDtlrSfJUlwsWAGfRdJ8vGlDBjjwgOYS2KrFwimFod7CGdP0jcrrtcyvGr1iQuQPPZGmJ3wiP1qmXPedQCHk6f5Azt1L6jgfgZaXYx"


# -------------------------------------
# 🍽 Restaurant Finder Function
# -------------------------------------
def api_access(latitude, longitude, open_at, radius, budget_level, cuisine):
    """
    Query Yelp API to return 3 restaurants matching:
    - Location (latitude, longitude)
    - Open at a certain timestamp
    - Radius (meters)
    - Budget level ("1", "2", "3")
    - Cuisine type ("italian", "mexican", "japanese", ...)
    """

    url = "https://api.yelp.com/v3/businesses/search"

    headers = {
        "Authorization": f"Bearer {API_KEY}"
    }

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "radius": radius,
        "open_at": open_at,
        "categories": cuisine,      # e.g. "italian"
        "price": str(budget_level), # "1" or "2" or "3"
        "limit": 20                 # fetch more so we can filter down to 3
    }

    response = requests.get(url, headers=headers, params=params)

    # Convert to JSON
    data = response.json()
    businesses = data.get("businesses", [])

    results = []
    for business in businesses:
        results.append({
            "name": business.get("name"),
            "rating": business.get("rating"),
            "price": business.get("price"),
            "categories": [c["title"] for c in business.get("categories", [])]
        })

        # Stop after 3 results
        if len(results) == 3:
            break

    return results