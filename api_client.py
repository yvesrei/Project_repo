import streamlit as st
import requests

    
API_KEY = "DWAyru0_dEUX8E3nQ679ka2iv8cj24u3Pl4ZCpcU_O1ciClu-HziLNSmqMItE5P22aApBVkLwVfkNqR0v6X9K8DcuyqZBycjrPixxx9-DQen0SeR0Qp2yjaTD4UlaXYx"

# Coordinates for Zurich (BY NOW we ONLY search around this location)
ZURICH_LAT = 47.3769
ZURICH_LON = 8.5417

# Base URLs for Yelp
SEARCH_URL = "https://api.yelp.com/v3/businesses/search"
DETAIL_URL = "https://api.yelp.com/v3/businesses/"


# Main function used by the Streamlit app to get restaurant matches
def api_access(latitude, longitude, open_at, radius, budget_level, cuisine):
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
    """

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

    # Helper function to execute a Yelp search request and return the "businesses" list
    # Yelp wraps actual hits under "businesses". If missing, default to empty list.
    def search(params):
        resp = requests.get(SEARCH_URL, headers=headers, params=params)
        data = resp.json()
        return data.get("businesses", [])

    # Base search parameters: strict filter (Zurich + radius + cuisine + price)
    # - We ignore the latitude/longitude arguments and hard-code Zurich coordinates.
    # - "categories" is the mapped cuisine.
    # - "price" is a string "1", "2", "3", etc. (Yelp expects a string, not an int).
    params = {
        "latitude": ZURICH_LAT,
        "longitude": ZURICH_LON,
        "radius": radius,
        # "open_at": open_at,          # Can be re-enabled if you want time-based filtering
        "categories": cuisine_alias,
        "price": str(budget_level),
        "limit": 20,
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
            detail_resp = requests.get(f"{DETAIL_URL}{biz_id}", headers=headers)
            detail = detail_resp.json()

        # Prefer detail endpoint fields, but fall back to search results if missing.
        # This ensures we always have something sensible to show in the UI.
        name = detail.get("name") or b.get("name")
        rating = detail.get("rating") or b.get("rating")
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
        results.append({
            "name": name,
            "rating": rating,
            "address": address,
            "phone": phone,
            "website": url,
            "opening_hours": opening_hours,
            "menu_url": menu_url,
        })

    # Return the list with up to 3 processed restaurant entries
    return results