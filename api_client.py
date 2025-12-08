import streamlit as st
import requests

API_KEY = "DWAyru0_dEUX8E3nQ679ka2iv8cj24u3Pl4ZCpcU_O1ciClu-HziLNSmqMItE5P22aApBVkLwVfkNqR0v6X9K8DcuyqZBycjrPixxx9-DQen0SeR0Qp2yjaTD4UlaXYx"

# Cuisine mapping system within a dictionary, which assigns different Yelp 
# categories via catchphrases to our simplified cuisine types.
CUISINE_MAPPING = {
   "Italian": ["italian", "pizza", "pasta", "trattoria", "osteria", "bistro"],
    "Asian": ["asian", "thai", "chinese", "szechuan", "cantonese", "japanese",
              "sushi", "ramen", "korean", "vietnamese", "nepalese", "himalayan",
              "asianfusion"],
    "Swiss / Alpine": ["swiss", "swissfood", "fondue", "raclette", "beiz",
                       "austrian", "german", "schweizer küche", "wirtshaus"],
    "Mediterranean": ["mediterranean", "greek", "spanish", "tapas", "portuguese",
                      "french", "mezze", "turkish"],
    "American": ["american", "burger", "bbq", "barbecue", "steakhouse", "diner"],
    "Middle Eastern": ["middleeastern", "lebanese", "arabic", "persian", "falafel",
                       "kebab", "halal"],
    "Latin American": ["latin", "mexican", "texmex", "peruvian", "brazilian",
                       "argentinian"],
    "Indian / South Asian": ["indian", "pakistani", "srilankan", "srilankisch",
                             "southasian"],
    "Vegetarian / Vegan": ["vegetarian", "vegan", "healthy", "plantbased",
                           "glutenfree"],
    "Seafood & Sushi": ["seafood", "fish", "sushi", "fishmarket"]
}
def map_yelp_category(yelp_categories):
    yelp_categories = [c.lower() for c in yelp_categories]
    for simple, detailed_list in CUISINE_MAPPING.items():
        for d in detailed_list:
            if d in yelp_categories:
                return simple
    return "International"

# Coordinates for Zurich (Initially, we used to ONLY search around this location)
ZURICH_LAT = 47.3769
ZURICH_LON = 8.5417

# We now  support the 9 biggest Swiss cities (by population) as search centers,
# using their main train station or an equivalent central point as the reference
# for the radius feature.
CITY_COORDS = {
    # Zurich
    "Zurich": (ZURICH_LAT, ZURICH_LON),

    # Basel
    "Basel": (47.5474, 7.5890),

    # Geneva
    "Geneva": (46.2102, 6.1424),

    # Lausanne
    "Lausanne": (46.5160, 6.6291),

    # Winterthur
    "Winterthur": (47.4998, 8.7243),

    # St. Gallen)
    "St. Gallen": (47.4232, 9.3697),

    # Lugano
    "Lugano": (46.0061, 8.9463),

    # Bern
    "Bern": (46.9488, 7.4391),

    # Luzern
    "Luzern": (47.0502, 8.3102),
}

# Base URLs for Yelp
SEARCH_URL = "https://api.yelp.com/v3/businesses/search"
DETAIL_URL = "https://api.yelp.com/v3/businesses/"


def rating_to_emoji(rating):
    """
    Maps a numeric Yelp rating to a simple emoji for quick visual feedback.
    """
    if rating is None:
        return "❓"
    if rating >= 4.8:
        return "🤩"
    elif rating >= 4.5:
        return "😋"
    elif rating >= 4.0:
        return "🙂"
    else:
        return "😐"


# Main function used by the Streamlit app to get restaurant matches
def api_access(city, radius, budget_level, cuisine, open_at=None):
    """
    Returns up to 5 restaurants in Zurich that match budget + cuisine.
    For each restaurant it returns:
    - name
    - address
    - rating
    - phone
    - website
    - opening_hours (multi-line string)

    Additional:
    We now support searches centered around the 9 largest Swiss cities, with 
    each result also including an emoji representation of the rating from Yelp.
    """

    if not API_KEY:
        st.error("Yelp API key is missing. Add it to st.secrets['YELP_API_KEY'].")
        return []

    # Build the HTTP header with the Bearer token so Yelp accepts our requests
    headers = {
        "Authorization": f"Bearer {API_KEY}"
    }

    # Resolve the chosen city (with many spelling variants) to coordinates.
    city_key = (city or "Zurich").strip()
    latitude, longitude = CITY_COORDS.get(city_key, (ZURICH_LAT, ZURICH_LON))

    # Helper function to execute a Yelp search request and return the "businesses" list
    # Yelp wraps actual hits under "businesses". If missing, default to empty list.
    def search(params):
        try:
            resp = requests.get(SEARCH_URL, headers=headers, params=params, timeout=5)
            resp.raise_for_status()
            data = resp.json()
        except requests.RequestException as e:
            st.error(f"Error contacting Yelp API: {e}")
            return []
        businesses = data.get("businesses", [])

        # We only keep businesses where rating >= 3.5 AND review_count >= 0.
        # This ensures we only show reasonably rated places. However, we had to loosen up the
        # filter conditions as most restaurants have few reviews on Yelp.
        businesses = [
            b for b in businesses
            if (b.get("rating") or 0) >= 3.5 and (b.get("review_count") or 0) >= 0
        ]
        return businesses

    # Base search parameters: strict filter (Zurich + radius + cuisine + price)
    # Additional: we now use Zurich as the default fallback.
    # Note: The radius parameter (and its slider in the UI) is interpreted as 
    # straight-line distance from the selected city center.
    base_params = {
        "latitude": latitude,
        "longitude": longitude,
        "radius": radius,
        # "open_at": open_at,          # time-based filter (added conditionally below)
        "categories": ",".join(CUISINE_MAPPING[cuisine]),
        "price": str(int(budget_level)),
        "limit": 50,
    }


    if open_at is not None:
        # First, try to respect the meal time. If that leads to no results, we will
        # later rerun the same search logic without this key.
        base_params["open_at"] = open_at

    # Helper: run the standard “strict/relaxed on price & cuisine” chain,
    # optionally with or without open_at.
    def run_search_chain(include_time: bool):
        params = base_params.copy()
        if not include_time:
            params.pop("open_at", None)

        # First attempt: strict search using both cuisine and price filters
        businesses = search(params)

        # Second attempt: if no results, drop the price filter (budget),
        # keeping cuisine and location.
        if not businesses:
            p2 = params.copy()
            p2.pop("price", None)
            businesses = search(p2)

        # Third attempt: if still no results, drop the cuisine filter as well,
        # leaving only location + radius.
        if not businesses:
            p3 = params.copy()
            p3.pop("price", None)
            p3.pop("categories", None)
            businesses = search(p3)

        return businesses

    # 1) Run full chain WITH time constraint (open_at)
    businesses = run_search_chain(include_time=True)

    # 2) If still no businesses and we had open_at, rerun WITHOUT time constraint.
    # This is where we “loosen” opening times while keeping rating and cuisine strict.
    if not businesses and open_at is not None:
        businesses = run_search_chain(include_time=False)

    # We only want to show up to 5 restaurants in the UI (user interface), even if Yelp returns more.
    businesses = businesses[:5]

    results = []

    # Yelp encodes weekdays as integers (0 = Monday, ..., 6 = Sunday).
    # We map them to short, readable labels for display.
    day_map = {0: "Mon", 1: "Tue", 2: "Wed", 3: "Thu", 4: "Fri", 5: "Sat", 6: "Sun"}

    # For each business, optionally fetch more detailed data and normalize it.
    for b in businesses:

        yelp_aliases = [c.get("alias", "").lower() for c in b.get("categories", [])]
        mapped_cuisine = map_yelp_category(yelp_aliases)
        if mapped_cuisine.lower() != cuisine.lower():
            continue

        biz_id = b.get("id")
        detail = {}

        # If we have a business ID, call the detail endpoint to get richer data
        if biz_id:
            try:
                detail_resp = requests.get(f"{DETAIL_URL}{biz_id}", headers=headers, timeout=5)
                detail_resp.raise_for_status()
                detail = detail_resp.json()
            except requests.RequestException:
                detail = {}

        # Prefer detail endpoint fields, but fall back to search results if missing.
        # This ensures we always have something sensible to show in the UI.
        name = detail.get("name") or b.get("name")
        rating = detail.get("rating") or b.get("rating")
        rating_emoji = rating_to_emoji(rating)
        phone = detail.get("display_phone") or b.get("display_phone")
        url = detail.get("url") or b.get("url")

        # Construct a single address string from the location object.
        # We filter out None values and join the remaining parts by commas.
        location = detail.get("location") or b.get("location", {})
        address_parts = [
            location.get("address1"),
            location.get("address2"),
            location.get("address3"),
            location.get("zip_code"),
            location.get("city"),
        ]
        address = ", ".join([part for part in address_parts if part])

        # --- Opening hours block ---
        # Yelp returns hours as a list of "open" entries
        # We convert that structure into a human-readable multi-line string,
        # like:
        #   Mon: 11:00–22:00
        opening_hours = None
        hours_list = detail.get("hours")
        if hours_list:
            open_entries = hours_list[0].get("open", [])

            # We now group all intervals per day so that each day is shown on a single line.
            # The current weekday (based on the server time) is underlined to highlight "today".
            day_intervals = {i: [] for i in range(7)}

            for entry in open_entries:
                # Map numeric day to label; fall back to raw number as string if unknown.
                day_index = entry.get("day")
                day = day_map.get(day_index, str(day_index))
                start = entry.get("start", "")
                end = entry.get("end", "")

                # Convert "HHMM" format to "HH:MM" if we have exactly 4 chars.
                if len(start) == 4:
                    start = f"{start[:2]}:{start[2:]}"
                if len(end) == 4:
                    end = f"{end[:2]}:{end[2:]}"

                # Collect each interval string under its day index so we can merge multiple intervals.
                if day_index in day_intervals:
                    day_intervals[day_index].append(f"{start}–{end}")

            # Determine today's weekday (0 = Monday, ..., 6 = Sunday)
            today_index = datetime.today().weekday()

            lines = []
            for day_index, intervals in day_intervals.items():
                if not intervals:
                    # Skip days without opening intervals
                    continue

                day_label = day_map.get(day_index, str(day_index))
                interval_str = ", ".join(intervals)

                # Build one line per opening interval
                line = f"{day_label}: {interval_str}"

                # Underline the current day to make it visually stand out on the website.
                if day_index == today_index:
                    line = f"**{line}** (today)"

                lines.append(line)

            # Join all lines into a single multi-line string if we collected any
            if lines:
                opening_hours = "\n".join(lines)

        # Build the final normalized restaurant record that the Streamlit UI expects.
        results.append({
            "name": name,
            "rating": rating,
            "rating_emoji": rating_emoji,
            "address": address,
            "phone": phone,
            "website": url,
            "opening_hours": opening_hours,
        })

    return results