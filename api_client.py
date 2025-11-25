#Placeholder
import streamlit as st
import requests

    
API_KEY = "DWAyru0_dEUX8E3nQ679ka2iv8cj24u3Pl4ZCpcU_O1ciClu-HziLNSmqMItE5P22aApBVkLwVfkNqR0v6X9K8DcuyqZBycjrPixxx9-DQen0SeR0Qp2yjaTD4UlaXYx"
ZURICH_LAT = 47.3769
ZURICH_LON = 8.5417


SEARCH_URL = "https://api.yelp.com/v3/businesses/search"
DETAIL_URL = "https://api.yelp.com/v3/businesses/"


def api_access(latitude, longitude, open_at, radius, budget_level, cuisine):
    """
    Returns up to 3 restaurants in Zurich that match budget + cuisine.
    For each restaurant: name, address, rating, phone, website, opening hours, menu_url (if present).
    """

    headers = {
        "Authorization": f"Bearer {API_KEY}"
    }

    # Map your cuisine labels to Yelp category aliases
    cuisine_alias_map = {
        "italian": "italian",
        "greek": "greek",
        "swiss": "swissfood",
        "chinese": "chinese",
        "thai": "thai",
    }
    cuisine_alias = cuisine_alias_map.get(cuisine, cuisine)

    def search(params):
        resp = requests.get(SEARCH_URL, headers=headers, params=params)
        data = resp.json()
        return data.get("businesses", [])

    # Base (strict) search: Zurich + cuisine + price
    params = {
        "latitude": ZURICH_LAT,
        "longitude": ZURICH_LON,
        "radius": radius,
        # "open_at": open_at,          # can re-enable later if you want
        "categories": cuisine_alias,
        "price": str(budget_level),
        "limit": 20,
    }

    businesses = search(params)

    # If nothing for that budget + cuisine, relax filters stepwise
    if not businesses:
        params.pop("price", None)
        businesses = search(params)

    if not businesses:
        params.pop("categories", None)
        businesses = search(params)

    # Only process up to 3
    businesses = businesses[:3]

    results = []

    # Helper to format opening hours
    day_map = {0: "Mon", 1: "Tue", 2: "Wed", 3: "Thu", 4: "Fri", 5: "Sat", 6: "Sun"}

    for b in businesses:
        biz_id = b.get("id")
        detail = {}

        if biz_id:
            detail_resp = requests.get(f"{DETAIL_URL}{biz_id}", headers=headers)
            detail = detail_resp.json()

        # Prefer detailed fields, fall back to search response
        name = detail.get("name") or b.get("name")
        rating = detail.get("rating") or b.get("rating")
        phone = detail.get("display_phone") or b.get("display_phone")
        url = detail.get("url") or b.get("url")

        location = detail.get("location") or b.get("location", {})
        address_parts = [
            location.get("address1"),
            location.get("address2"),
            location.get("address3"),
            location.get("zip_code"),
            location.get("city"),
        ]
        address = ", ".join([part for part in address_parts if part])

        # Opening hours
        opening_hours = None
        hours_list = detail.get("hours")
        if hours_list:
            open_entries = hours_list[0].get("open", [])
            lines = []
            for entry in open_entries:
                day = day_map.get(entry.get("day"), str(entry.get("day")))
                start = entry.get("start", "")
                end = entry.get("end", "")
                if len(start) == 4:
                    start = f"{start[:2]}:{start[2:]}"
                if len(end) == 4:
                    end = f"{end[:2]}:{end[2:]}"
                lines.append(f"{day}: {start}–{end}")
            if lines:
                opening_hours = "\n".join(lines)

        attributes = detail.get("attributes", {}) or {}
        menu_url = attributes.get("menu_url") or attributes.get("menu_url_external") or None

        results.append({
            "name": name,
            "rating": rating,
            "address": address,
            "phone": phone,
            "website": url,
            "opening_hours": opening_hours,
            "menu_url": menu_url,
        })

    return results
    
