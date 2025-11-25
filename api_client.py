#Placeholder
import streamlit as st
import requests

    
API_KEY = "DWAyru0_dEUX8E3nQ679ka2iv8cj24u3Pl4ZCpcU_O1ciClu-HziLNSmqMItE5P22aApBVkLwVfkNqR0v6X9K8DcuyqZBycjrPixxx9-DQen0SeR0Qp2yjaTD4UlaXYx"
ZURICH_LAT = 47.3769
ZURICH_LON = 8.5417

# -------------------------------------
# 🍽 Restaurant Finder Function
# -------------------------------------
def api_access(latitude, longitude, open_at, radius, budget_level, cuisine):
    """
    Query Yelp API to return up to 3 restaurants.
    Location is always Zürich (ZURICH_LAT, ZURICH_LON).
    """

    url = "https://api.yelp.com/v3/businesses/search"

    headers = {
        "Authorization": f"Bearer {API_KEY}"
    }

    # Map your cuisine names -> Yelp category aliases
    cuisine_alias_map = {
        "italian": "italian",
        "greek": "greek",
        "swiss": "swissfood",   # Yelp uses 'swissfood'
        "chinese": "chinese",
        "thai": "thai",
    }
    cuisine_alias = cuisine_alias_map.get(cuisine, cuisine)

    # Start with “strict” filters
    params = {
        "latitude": ZURICH_LAT,
        "longitude": ZURICH_LON,
        "radius": radius,
        # "open_at": open_at,          # 🔸 disable for now (can be too strict)
        "categories": cuisine_alias,
        "price": str(budget_level),    # "1", "2", "3"
        "limit": 20
    }

    st.write("🔍 Calling Yelp with:", params)

    response = requests.get(url, headers=headers, params=params)
    data = response.json()

    # Show raw response for debugging
    st.write("🧾 Yelp status:", response.status_code)
    st.write("🧾 Yelp response (truncated):", {k: data[k] for k in list(data.keys())[:3]})

    # If there's an error from Yelp, show it clearly
    if "error" in data:
        st.error(f"Yelp error: {data['error'].get('code')} – {data['error'].get('description')}")
        return []

    businesses = data.get("businesses", [])

    # If nothing found, relax filters:
    if not businesses:
        st.info("No results with price + cuisine. Trying without price…")
        params.pop("price", None)
        response = requests.get(url, headers=headers, params=params)
        data = response.json()
        businesses = data.get("businesses", [])

    if not businesses:
        st.info("Still no results. Trying without cuisine (any restaurant in Zürich)…")
        params.pop("categories", None)
        response = requests.get(url, headers=headers, params=params)
        data = response.json()
        businesses = data.get("businesses", [])

    results = []
    for b in businesses:
        results.append({
            "name": b.get("name"),
            "rating": b.get("rating"),
            "price": b.get("price"),
            "categories": [c["title"] for c in b.get("categories", [])]
        })
        if len(results) == 3:
            break

 