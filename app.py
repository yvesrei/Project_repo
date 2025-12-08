# This is the main Streamlit app file
#  Defines the navigation system (home, questionnaire, result, API, about)
#  Manages session state (participants, answers, current page)
#  Connects the UI to the external restaurant API


import streamlit as st
from statistics import mode
from datetime import datetime, time  
from Show_homepage import show_homepage
from Questionnaire import show_questionnaire
from spider_chart import group_taste_profile
from About_us import show_about_us

# Needed for AI implementation: Restaurant descriptions (Alex)
from api_client import api_access
# Needed for AI implementation: Restaurant descriptions (Alex)
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
        st.subheader(r["name"])

        if r["rating"] is not None:
            st.write(f"⭐ {r['rating']} / 5")

        if r["address"]:
            st.write(r["address"])

        if r["phone"]:
            st.write(f"📞 {r['phone']}")

        if r["website"]:
            st.markdown(f"[Website]({r['website']})")

        if r["opening_hours"]:
            st.write("🕒 Opening hours:")
            st.text(r["opening_hours"])  # preserves line breaks

        if r["menu_url"]:
            st.markdown(f"[Menu]({r['menu_url']})")

        # === Needed for AI implementation: Restaurant Description (Alex) – START ===
        ai_text = generate_restaurant_summary(r)
        st.info(ai_text)
        # === Needed for AI implementation: Restaurant Description (Alex) – END ===

        st.markdown("---")


## 1. Session state initialization
# Streamlit reruns the script on every interaction. We use st.session_state
# to track values across reruns so we know:
# - which page the user is on,
# - how many participants there are,
# - which participant is currently answering the questionnaire,
# - and all collected answers so far.

if "page" not in st.session_state:
    # First run: start the user on the home page.
    st.session_state["page"] = "home"
else:
    # Later runs: keep the current page value so navigation is stable.
    pass

if "num_of_participants" not in st.session_state:
    # Stores the total number of people who will answer the questionnaire.
    # Initially unknown, so set it to None until the user enters it.
    st.session_state["num_of_participants"] = None
else:
    # Once set on the home page, this value is reused across the later pages.
    pass

if "current_participant" not in st.session_state:
    # Tracks which participant is currently filling out the questionnaire.
    # We start counting at 1 for the first participant.
    st.session_state["current_participant"] = 1
else:
    # This counter is typically incremented when one participant finishes.
    pass

if "answers" not in st.session_state:
    # List that holds one answer dictionary per participant.
    # Each element should contain that participant's responses.
    st.session_state["answers"] = []
else:
    # On reruns, we keep all previously collected answers intact.
    pass


## 2. Page navigation (router)
# The "page" key in session_state acts as a simple router.
# Depending on its value, we call exactly one view function.
# Other parts of the app (buttons, etc.) update st.session_state["page"]
# to switch between screens.

 # Gets the page at which the app is at the moment.
 # If "page" exists it returns its value, if not it returns "home".
page = st.session_state.get("page", "home")

if page == "home":
    # Home screen:
    # - Introduces the app
    # - Asks for number of participants
    # - Provides entry point into the questionnaire
    show_homepage()

elif page == "questionnaire":
    # Questionnaire screen:
    # - Collects all answers from the current participant
    # - Uses current_participant and num_of_participants from session_state

    # Back navigation: go back to the main landing page.
    col_home, col_prev_participant = st.columns(2)
    with col_home:
        if st.button("← Back to home"):
            st.session_state["page"] = "home"
            st.rerun()

    # Back navigation between participants:
    # If we are on participant N > 1, allow user to step back to N-1 and re-enter answers.
    with col_prev_participant:
        if st.session_state["current_participant"] > 1:
            if st.button("← Back to previous participant"):
                old_cp = st.session_state["current_participant"]
                new_cp = old_cp - 1
                st.session_state["current_participant"] = new_cp
                # Truncate stored answers so the previous participant's data can be changed cleanly.
                st.session_state["answers"] = st.session_state["answers"][:new_cp]
                st.rerun()

    show_questionnaire()

elif page == "result":
    # Result screen:
    # - Aggregates all participants' answers
    # - Computes and displays the group taste profile

    # Back navigation: allow user to return to the questionnaire to adjust preferences.
    if st.button("← Back to questionnaire"):
        st.session_state["page"] = "questionnaire"
        st.rerun()

    group_taste_profile(st.session_state["answers"])

elif page == "api":
    # API results screen:
    # - Uses the computed group profile values (budget, cuisine, walking distance(radius)
    # - Calls the external API (e.g. Yelp) and displays matching restaurants

    # Back navigation: let user move back to the result page or questionnaire.
    col_back_result, col_back_questionnaire = st.columns(2)
    with col_back_result:
        if st.button("← Back to result"):
            st.session_state["page"] = "result"
            st.rerun()
    with col_back_questionnaire:
        if st.button("← Back to questionnaire"):
            st.session_state["page"] = "questionnaire"
            st.rerun()

    show_api_results()

elif page == "about":
    # About screen:
    # - General information about the app, authors and context

    # Back navigation: go back to the main landing page.
    if st.button("← Back to home"):
        st.session_state["page"] = "home"
        st.rerun()

    show_about_us()

else:
    # Fallback for invalid / unexpected page values:
    # - Reset to home to avoid the app breaking on a bad state
    st.session_state["page"] = "home"
    show_homepage()