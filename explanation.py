import streamlit as st

# === Alex: AI integration setup (Groq) – START ===
try:
    from groq import Groq

    # Alex: read API key from Streamlit secrets. This must be set in Streamlit Cloud.
    GROQ_API_KEY = st.secrets.get("GROQ_API_KEY")
    if GROQ_API_KEY:
        groq_client = Groq(api_key=GROQ_API_KEY)
        HAVE_GROQ = True
    else:
        groq_client = None
        HAVE_GROQ = False
except Exception as e:
    groq_client = None
    HAVE_GROQ = False
    GROQ_INIT_ERROR = e  # Alex: stored only for debugging if ever needed
# === Alex: AI integration setup (Groq) – END ===


# Alex: simple fallback texts in case the HuggingFace model is not available
def _fallback_group_summary(taste_profile: dict) -> str:
    cluster = taste_profile.get("cluster_name", "your group")
    cuisine = taste_profile.get("top_cuisine_group", "your favourite cuisines")
    budget = taste_profile.get("budget_symbol_group", "$$")
    walk = taste_profile.get("walking_distance_label_group", "your usual walking distance")

    return (
        f"Tonight you're rolling with the **{cluster}** – a group that loves {cuisine} "
        f"and feels comfortable at a {budget} budget level. "
        f"With about {walk} in you before dinner, we’ll look for spots that feel close enough to reach "
        "without complaints but still like a little outing."
    )


def _fallback_restaurant_summary(restaurant: dict) -> str:
    name = restaurant.get("name", "this place")
    cuisine = restaurant.get("categories", "the chosen cuisine")
    return (
        f"**{name}** is one of the restaurants that best fits your group's profile. "
        f"It lines up with your budget, location and taste for {cuisine}, "
        "making it a strong pick for tonight’s crew."
    )


# === Alex: AI-generated group summary (Groq) – START ===
def generate_group_summary(taste_profile: dict) -> str:
    """
    Alex: Creates a fun, friendly 2–3 sentence summary of the group's food preferences.
    Uses a Groq-hosted Llama 3 model if available, otherwise falls back to a static but sensible text.
    """
    # If the Groq client is not available → use fallback
    if not HAVE_GROQ or groq_client is None:
        return _fallback_group_summary(taste_profile)

    # Build a compact, human-readable description of the data for the prompt
    cluster_name = taste_profile.get("cluster_name", "this group")
     # cluster_id = taste_profile.get("cluster_id") # We noticed that it doesn't need the cluster id because 
     # it already gets the cluster name. 
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
- Budget (average): {budget} → symbol {budget_symbol}
- Top cuisine: {cuisine}
- Preferred walking distance label: {walk}
"""

    try:
        # Alex: generate text using Groq (Llama 3)
        response = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a friendly assistant that writes short, playful summaries "
                        "of a group's restaurant preferences for a dinner-planning app."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            max_tokens=130,
            temperature=0.9,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        # Alex: never crash the app – show fallback instead, but show a small debug hint
        st.warning(f"Groq group summary error: {e}")
        return _fallback_group_summary(taste_profile)
# === Alex: AI-generated group summary (Groq) – END ===


# === Alex: AI-generated restaurant description (Groq) – START ===
def generate_restaurant_summary(restaurant: dict) -> str:
    """
    Alex: Produces a playful, witty 2–3 sentence description for a single restaurant.
    Uses a Groq-hosted Llama 3 model when possible, otherwise returns a static but meaningful text.
    """
    if not HAVE_GROQ or groq_client is None:
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
        response = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a helpful assistant that writes short, fun descriptions of restaurants "
                        "for a group dinner recommendation app."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            max_tokens=130,
            temperature=0.95,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        # Alex: fall back to a clean static description if anything goes wrong, with a small debug hint
        st.warning(f"Groq restaurant summary error: {e}")
        return _fallback_restaurant_summary(restaurant)
# === Alex: AI-generated restaurant description (Groq) – END ===