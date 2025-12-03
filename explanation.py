import streamlit as st

def generate_group_summary(taste_profile: dict) -> str:
    """
    TEMP STUB:
    Simple fake summary so we can check that page navigation works.
    Replace with real OpenAI logic once everything is stable.
    """
    return (
        "This is a temporary test summary of your group's food preferences. "
        "If you are reading this, the AI integration is wired correctly and the app is running."
    )

def generate_restaurant_summary(restaurant: dict) -> str:
    """
    TEMP STUB:
    Simple fake restaurant description so we can verify the AI hook is being called.
    Replace with real OpenAI logic once everything is stable.
    """
    name = restaurant.get("name", "this place")
    return (
        f"This is a temporary description for {name}. "
        "Once the AI integration is fully configured, this text will be generated dynamically."
    )