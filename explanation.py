import streamlit as st

# === Alex: AI integration setup (HuggingFace, free) – START ===
try:
    # Alex: use a small, widely available model so it runs reliably on free inference
    from huggingface_hub import InferenceClient

    HF_MODEL_ID = "gpt2"
    hf_client = InferenceClient(HF_MODEL_ID)
    HAVE_HF = True
except Exception as e:
    HF_MODEL_ID = None
    hf_client = None
    HAVE_HF = False
    HF_ERROR = e  # Alex: stored only for debugging if ever needed
# === Alex: AI integration setup (HuggingFace, free) – END ===


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


# === Alex: AI-generated group summary (HuggingFace) – START ===
def generate_group_summary(taste_profile: dict) -> str:
    """
    Alex: Creates a fun, friendly 2–3 sentence summary of the group's food preferences.
    Uses a free HuggingFace model if available, otherwise falls back to a static but sensible text.
    """
    # If the HuggingFace client is not available → use fallback
    if not HAVE_HF or hf_client is None:
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
        # Alex: generate text using a free HuggingFace model
        response = hf_client.text_generation(
            prompt,
            max_new_tokens=130,
            temperature=0.9,
            do_sample=True,
        )
        return response.strip()
    except Exception as e:
        # Alex: never crash the app – show fallback instead, but show a small debug hint
        st.warning(f"HuggingFace group summary error: {e}")
        return _fallback_group_summary(taste_profile)
# === Alex: AI-generated group summary (HuggingFace) – END ===


# === Alex: AI-generated restaurant description (HuggingFace) – START ===
def generate_restaurant_summary(restaurant: dict) -> str:
    """
    Alex: Produces a playful, witty 2–3 sentence description for a single restaurant.
    Uses a free HuggingFace model when possible, otherwise returns a static but meaningful text.
    """
    if not HAVE_HF or hf_client is None:
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
        response = hf_client.text_generation(
            prompt,
            max_new_tokens=130,
            temperature=0.95,
            do_sample=True,
        )
        return response.strip()
    except Exception as e:
        # Alex: fall back to a clean static description if anything goes wrong, with a small debug hint
        st.warning(f"HuggingFace restaurant summary error: {e}")
        return _fallback_restaurant_summary(restaurant)
# === Alex: AI-generated restaurant description (HuggingFace) – END ===