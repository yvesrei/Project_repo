#Placeholder

import openai
import streamlit as st

# Load API key (must be stored in Streamlit secrets)
openai.api_key = st.secrets.get("OPENAI_API_KEY", "")

def generate_group_summary(taste_profile: dict) -> str:
    """
    Creates a fun 2–3 sentence summary of the group's taste profile.
    """
    prompt = f"""
    Write a fun, friendly, humorous 3‑sentence summary of this group's food preferences.
    Avoid formal tone. Be playful and creative.
    Taste profile data: {taste_profile}
    """

    try:
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=120,
            temperature=0.9
        )
        return response.choices[0].message["content"].strip()
    except Exception as e:
        return f"(AI summary unavailable: {e})"

def generate_restaurant_summary(restaurant: dict) -> str:
    """
    Creates a playful 2–3 sentence description for a single restaurant.
    Emphasizes vibe, cuisine, atmosphere, and fun commentary.
    """
    prompt = f"""
    Create a playful 2–3 sentence description of this restaurant.
    Tone: fun, light, witty, maybe cheeky.
    Mention why it could be a good fit for the group.
    Restaurant details: {restaurant}
    """

    try:
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=120,
            temperature=0.95
        )
        return response.choices[0].message["content"].strip()
    except Exception as e:
        return f"(AI restaurant description unavailable: {e})"

# TODO: Ensure all pages import from this module and pass correct dict formats.