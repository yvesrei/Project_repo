import streamlit as st
from datetime import datetime, time


# Needed for AI implementation: Restaurant descriptions
from api_client import api_access
# Needed for AI implementation: Restaurant descriptions
from explanation import generate_restaurant_summary


# Display restaurant matches based on stored group results from spider web
def show_api_results():

    # Stop if required data from previous steps is missing
    if "group_budget_numeric" not in st.session_state or "group_cuisine" not in st.session_state:
        st.error("Please go through the questionnaire and results page first.")
        return

    # Allow the user to choose what kind of meal they are planning
    meal_choice = st.selectbox(
        "What kind of meal are you planning?",
        ["Breakfast", "Lunch", "Dinner"],
    )

    # For Yelp's open_at we must choose one representative time per meal.
    # We pick times that sit in the middle of typical Swiss/European eating windows
    # so that most places that offer that meal type are actually open.
    MEAL_TIME_MAP = {
        "Breakfast": time(9, 0),   # 09:00 ≈ typical breakfast/brunch time; cafés are usually open by then
        "Lunch": time(13, 0),      # 13:00 sits in the middle of the common lunch service (around 12:00–14:00)
        "Dinner": time(20, 0),     # 20:00 reflects a standard dinner hour; most kitchens are open 18:00–22:00
    }

    today = datetime.now()
    meal_time = MEAL_TIME_MAP[meal_choice]
    meal_dt = datetime(
        year=today.year,
        month=today.month,
        day=today.day,
        hour=meal_time.hour,
        minute=meal_time.minute,
    )
    # Convert the chosen meal time on today's date into a Unix timestamp
    # so Yelp can filter for places that are open at that specific moment.
    open_at_timestamp = int(meal_dt.timestamp())

    # Let the user pick one of the supported cities
    city = st.selectbox(
        "Choose your city",
        ["Zurich", "Basel", "Geneva", "Lausanne", "Winterthur",
         "St. Gallen", "Lugano", "Bern", "Luzern"]
    )

    # Let the user choose the maximum walking distance (radius for Yelp in meters)
    # Default value of slider is the group walking distance value

    default_radius = st.session_state.get("group_walking_radius", 2500)
    radius = st.slider(
        "Maximum walking distance (in meters)",
        min_value=100,
        max_value=5000,
        value=int(default_radius),
        step=250,
    )




    # Page title for the restaurant results view
    st.title(f"Matching Restaurants in {city} for {meal_choice}!")

    results = api_access(
        city=city,
        radius=radius,
        budget_level=st.session_state["group_budget_numeric"],
        cuisine=st.session_state["group_cuisine"],
        open_at=open_at_timestamp,  # Time constraint is now “soft” – api_client will drop it if it kills all results
        
    )

    # Handle the case where no restaurants are returned
    if not results:
        st.warning("No restaurants found even after relaxing filters.")
        return

    # Display each restaurant's key information to the user, including name, rarting, address, phone, 
    # website, opening hours, and menu URL
    for r in results:
        st.subheader(f"{r['name']} {r['rating_emoji']}")

        if r["rating"] is not None:
            st.write(f"{r['rating_emoji']} {r['rating']} / 5")

        if r["address"]:
            st.write(r["address"])

        if r["phone"]:
            st.write(f"📞 {r['phone']}")

        if r["website"]:
            st.markdown(f"[Website]({r['website']})")

        if r["opening_hours"]:
            st.write("🕒 Opening hours:")
            st.text(r["opening_hours"])  # preserves line breaks

        if r.get("menu_url"):

            st.markdown(f"[Menu]({r['menu_url']})")

        # AI implementation: Restaurant Description
        ai_text = generate_restaurant_summary(r)
        st.info(ai_text)
        # Creates Box for AI text

        st.markdown("---")