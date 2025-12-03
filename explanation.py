import streamlit as st

# === Alex: AI integration setup (OpenAI) – START ===
try:
    from openai import OpenAI  # Alex: new OpenAI client (requires openai>=1.0.0)
    HAVE_OPENAI = True
except Exception as e:
    HAVE_OPENAI = False
    OPENAI_IMPORT_ERROR = e
    OpenAI = None  # Alex: placeholder so the name exists even if import fails

# Alex: read API key from Streamlit secrets
API_KEY = st.secrets.get("OPENAI_API_KEY", None)

client = None
if HAVE_OPENAI and API_KEY:
    # Alex: create a reusable OpenAI client instance
    client = OpenAI(api_key=API_KEY)
# === Alex: AI integration setup (OpenAI) – END ===


# Alex: simple fallback texts in case OpenAI is not available
def _fallback_group_summary(taste_profile: dict) -> str:
    cluster = taste_profile.get("cluster_name", "your group")
    cuisine = taste_profile.get("top_cuisine_group", "your favourite cuisines")
    budget = taste_profile.get("budget_symbol_group", "$$")
    walk = taste_profile.get("walking_distance_label_group", "your usual walking distance")

    return (
        f"Based on your answers, **{cluster}** looks like a group that enjoys {cuisine}, "
        f"is comfortable around a {budget} budget, and prefers about {walk} of walking. "
        "Once the live AI integration is running, this summary will become even more playful and personalised."
    )


def _fallback_restaurant_summary(restaurant: dict) -> str:
    name = restaurant.get("name", "this place")
    cuisine = restaurant.get("categories", "the chosen cuisine")
    return (
        f"This is one of the restaurants that best fits your group's profile. **{name}** matches your budget, "
        f"location and taste preferences. Once the live AI integration is active, you’ll see a more playful "
        f"description here for {name}."
    )


# === Alex: AI-generated group summary – START ===
def generate_group_summary(taste_profile: dict) -> str:
    """
    Alex: Creates a fun, friendly 2–3 sentence summary of the group's food preferences.
    Uses OpenAI if available, otherwise falls back to a static but sensible text.
    """
    # If OpenAI is not available or no API key or client → use fallback
    if not HAVE_OPENAI or not API_KEY or client is None:
        return _fallback_group_summary(taste_profile)

    # Build a compact, human-readable description of the data for the prompt
    cluster_name = taste_profile.get("cluster_name", "this group")
    cluster_id = taste_profile.get("cluster_id")
    budget = taste_profile.get("numeric_budget_group")
    budget_symbol = taste_profile.get("budget_symbol_group", "$$")
    cuisine = taste_profile.get("top_cuisine_group", "mixed cuisines")
    walk = taste_profile.get("walking_distance_label_group", "their usual walking distance")

    prompt = f"""
You are an assistant that writes short, fun food personality summaries.

Write a playful 2–3 sentence summary of a group's restaurant preferences.
Tone: light, friendly, maybe a bit cheeky, but not cringe and not too long.
Do NOT repeat the raw numbers; describe them in words.

Group info:
- Cluster name: {cluster_name}
- Cluster id: {cluster_id}
- Budget (average): {budget} → symbol {budget_symbol}
- Top cuisine: {cuisine}
- Preferred walking distance label: {walk}
"""

    try:
        # Alex: use OpenAI chat completions via the new client
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=130,
            temperature=0.9,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        # Alex: never crash the app – show fallback instead
        return _fallback_group_summary(taste_profile) + f" (AI error: {e})"
# === Alex: AI-generated group summary – END ===


# === Alex: AI-generated restaurant description – START ===
def generate_restaurant_summary(restaurant: dict) -> str:
    """
    Alex: Produces a playful, witty 2–3 sentence description for a single restaurant.
    Uses OpenAI when possible, otherwise returns a static but meaningful text.
    """
    if not HAVE_OPENAI or not API_KEY or client is None:
        return _fallback_restaurant_summary(restaurant)

    name = restaurant.get("name", "this place")
    rating = restaurant.get("rating", "N/A")
    price = restaurant.get("price", "")
    address = restaurant.get("address", "")
    categories = restaurant.get("categories", "")
    distance = restaurant.get("distance", None)

    prompt = f"""
Write a fun, 2–3 sentence description of a restaurant for a group dinner recommendation app.

Tone: playful, light, maybe slightly cheeky, but not cringe.
Mention:
- What kind of place it feels like
- Cuisine / vibe (use {categories} if helpful)
- Why it could fit a group with these preferences (budget, social vibe etc.)
Avoid repeating raw numbers like exact distance; describe things qualitatively.

Restaurant data:
- Name: {name}
- Rating: {rating}
- Price level: "{price}"
- Address: {address}
- Categories: {categories}
- Distance (meters): {distance}
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=130,
            temperature=0.95,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return _fallback_restaurant_summary(restaurant) + f" (AI error: {e})"
# === Alex: AI-generated restaurant description – END ===