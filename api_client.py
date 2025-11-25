import streamlit as st
import requests

    
API_KEY = "DWAyru0_dEUX8E3nQ679ka2iv8cj24u3Pl4ZCpcU_O1ciClu-HziLNSmqMItE5P22aApBVkLwVfkNqR0v6X9K8DcuyqZBycjrPixxx9-DQen0SeR0Qp2yjaTD4UlaXYx"

# Coordinates for Zurich (BY NOW we ONLY search around this location)
ZURICH_LAT = 47.3769
ZURICH_LON = 8.5417

# We now  support the 9 biggest Swiss cities (by population) as search centers,
# using their main train station or an equivalent central point as the reference
# for the radius feature. Multiple common spellings are mapped to the same coords.
CITY_COORDS = {
    # Zurich
    "zurich": (ZURICH_LAT, ZURICH_LON),
    "zürich": (ZURICH_LAT, ZURICH_LON),
    "zuerich": (ZURICH_LAT, ZURICH_LON),
    "zurich hb": (ZURICH_LAT, ZURICH_LON),

    # Basel
    "basel": (47.5474, 7.5890),
    "bâle": (47.5474, 7.5890),
    "basel sbb": (47.5474, 7.5890),

    # Geneva
    "geneva": (46.2102, 6.1424),
    "genève": (46.2102, 6.1424),
    "genf": (46.2102, 6.1424),

    # Lausanne
    "lausanne": (46.5160, 6.6291),
    "lausane": (46.5160, 6.6291),

    # Winterthur
    "winterthur": (47.4998, 8.7243),
    "winterthur hb": (47.4998, 8.7243),

    # St. Gallen (with various spellings)
    "st. gallen": (47.4232, 9.3697),
    "st gallen": (47.4232, 9.3697),
    "sankt gallen": (47.4232, 9.3697),
    "saint gallen": (47.4232, 9.3697),

    # Lugano
    "lugano": (46.0061, 8.9463),

    # Bern
    "bern": (46.9488, 7.4391),
    "berne": (46.9488, 7.4391),

    # Luzern
    "luzern": (47.0502, 8.3102),
    "lucerne": (47.0502, 8.3102),
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
    Returns up to 3 restaurants in Zurich that match budget + cuisine.
    For each restaurant it returns:
    - name
    - address
    - rating
    - phone
    - website
    - opening_hours (multi-line string)
    - menu_url (if available)

    Additional:
    We now support searches centered around the 9 largest Swiss cities, using their
    main train stations or central points as reference for the radius search, because
    these cities are the most relevant across Switzerland. Each result also includes
    an emoji representation of the rating and image URLs retrieved from Yelp.
    """

    if not API_KEY:
        st.error("Yelp API key is missing. Add it to st.secrets['YELP_API_KEY'].")
        return []

    # Build the HTTP header with the Bearer token so Yelp accepts our requests
    headers = {
        "Authorization": f"Bearer {API_KEY}"
    }

    # Map our internal cuisine labels to Yelp's category aliases.
    cuisine_alias_map = {
        "italian": "italian",
        "greek": "greek",
        "swiss": "swissfood",
        "chinese": "chinese",
        "thai": "thai",
    }
    cuisine_alias = cuisine_alias_map.get(cuisine, cuisine)

    # Resolve the chosen city (with many spelling variants) to coordinates.
    city_key = (city or "zurich").strip().lower()
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

        # EXCLUDE restaurants with rating below 4.0.
        # We only keep businesses where the (search-level) rating is >= 4.0.
        businesses = [
            b for b in businesses
            if (b.get("rating") or 0) >= 4.0
        ]
        return businesses

    # Base search parameters: strict filter (Zurich + radius + cuisine + price)
    # - We ignore the latitude/longitude arguments and hard-code Zurich coordinates.
    # - "categories" is the mapped cuisine.
    # - "price" is a string "1", "2", "3", etc. (Yelp expects a string, not an int).
    # Additional: we now use the resolved coordinates of one of the 9 biggest Swiss cities
    # (by population) as the center of the radius search, with Zurich as the default fallback.
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "radius": radius,
        # "open_at": open_at,          # Can be re-enabled if you want time-based filtering
        "categories": cuisine_alias,
        "price": str(budget_level),
        "limit": 50,
    }

    # First attempt: strict search using both cuisine and price filters
    businesses = search(params)

    # Second attempt: if no results, drop the price filter (budget),
    # keeping cuisine and location. This increases the chance of getting some hits.
    if not businesses:
        params.pop("price", None)
        businesses = search(params)

    # Third attempt: if still no results, drop the cuisine filter as well,
    # leaving only location + radius. This is a "last resort" to show something.
    if not businesses:
        params.pop("categories", None)
        businesses = search(params)

    # We only want to show up to 3 restaurants in the UI (user interface), even if Yelp returns more.
    businesses = businesses[:3]

    # This list will hold the normalized restaurant dictionaries that the app uses.
    results = []

    # Yelp encodes weekdays as integers (0 = Monday, ..., 6 = Sunday).
    # We map them to short, readable labels for display.
    day_map = {0: "Mon", 1: "Tue", 2: "Wed", 3: "Thu", 4: "Fri", 5: "Sat", 6: "Sun"}

    # For each business, optionally fetch more detailed data and normalize it.
    for b in businesses:
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

        # Primary image and additional photos pulled from Yelp.
        primary_image_url = detail.get("image_url") or b.get("image_url")
        photos = detail.get("photos") or []

        # --- Opening hours block ---
        # Yelp returns hours as a list of "open" entries with:
        # - day (0–6)
        # - start/end times as "HHMM" strings (e.g. "1100" for 11:00)
        # We convert that structure into a human-readable multi-line string,
        # like:
        #   Mon: 11:00–22:00
        #   Tue: 11:00–22:00
        opening_hours = None
        hours_list = detail.get("hours")
        if hours_list:
            # Use the first hours object (index 0) as Yelp usually puts main hours there.
            open_entries = hours_list[0].get("open", [])
            lines = []

            for entry in open_entries:
                # Map numeric day to label; fall back to raw number as string if unknown.
                day = day_map.get(entry.get("day"), str(entry.get("day")))
                start = entry.get("start", "")
                end = entry.get("end", "")

                # Convert "HHMM" format to "HH:MM" if we have exactly 4 chars.
                if len(start) == 4:
                    start = f"{start[:2]}:{start[2:]}"
                if len(end) == 4:
                    end = f"{end[:2]}:{end[2:]}"

                # Build one line per opening interval
                lines.append(f"{day}: {start}–{end}")

            # Join all lines into a single multi-line string if we collected any
            if lines:
                opening_hours = "\n".join(lines)

        # --- Menu URL block ---
        # Menu information, if available, is typically stored under "attributes".
        # We check multiple possible keys because Yelp may use different fields.
        attributes = detail.get("attributes", {}) or {}
        menu_url = (
            attributes.get("menu_url")
            or attributes.get("menu_url_external")
            or None
        )

        # Build the final normalized restaurant record that the Streamlit UI expects.
        # This keeps all downstream display logic simple and consistent.
        # Additional fields:
        # - rating_emoji: quick emoji representation of the rating (for UI).
        # - image_url / photos: image URLs from Yelp to display pictures of the restaurant.
        results.append({
            "name": name,
            "rating": rating,
            "rating_emoji": rating_emoji,
            "address": address,
            "phone": phone,
            "website": url,
            "opening_hours": opening_hours,
            "menu_url": menu_url,
            "image_url": primary_image_url,
            "photos": photos,
        })

    # Return the list with up to 3 processed restaurant entries
    return results