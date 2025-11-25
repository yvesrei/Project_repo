import streamlit as st
from statistics import mode
from Show_homepage import show_homepage
from Questionnaire import show_questionnaire
from spider_chart import group_taste_profile
from About_us import show_about_us
from api_client import api_access


# Display restaurant matches based on stored group results from spider web
def show_api_results():

    # Stop if required data from previous steps is missing
    if "group_budget_numeric" not in st.session_state or "group_cuisine" not in st.session_state:
        st.error("Please go through the questionnaire and results page first.")
        return

    # Page title for the restaurant results view
    st.title("Matching Restaurants in Zürich!")

    # Call the Yelp API via api_access()
    # Fetch matching restaurants from the Yelp API based on group budget and cuisine
    # NOTE: api_access now expects (city, radius, budget_level, cuisine, open_at=None)
    # We keep Zürich as the fixed city here by passing city="Zurich".
    results = api_access(
        city="Zurich",
        radius=2000,
        budget_level=st.session_state["group_budget_numeric"],
        cuisine=st.session_state["group_cuisine"],
        open_at=1700000000,  # you can still use your fixed timestamp if you like
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

        st.markdown("---")


# --- 1. Session state initialization ---
# Streamlit reruns the script on every interaction. We use st.session_state
# to persist values across reruns so we know:
# - which page the user is on,
# - how many participants there are,
# - which participant is currently answering,
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
    # Once set on the home page, this value is reused across pages.
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


# --- 2. Page navigation (router) ---
# The "page" key in session_state acts as a simple router.
# Depending on its value, we call exactly one view function.
# Other parts of the app (buttons, etc.) update st.session_state["page"]
# to switch between screens.

page = st.session_state.get("page", "home")

if page == "home":
    # Home screen:
    # - Introduces the app
    # - Asks for number of participants
    # - Provides entry point into the questionnaire flow
    show_homepage()

elif page == "questionnaire":
    # Questionnaire screen:
    # - Collects answers for the current participant
    # - Uses current_participant and num_of_participants from session_state
    show_questionnaire()

elif page == "result":
    # Result screen:
    # - Aggregates all participants' answers
    # - Computes and displays the group taste profile
    group_taste_profile(st.session_state["answers"])

elif page == "api":
    # API results screen:
    # - Uses the computed group profile (budget, cuisine)
    # - Calls the external API (e.g. Yelp) and displays matching restaurants
    show_api_results()

elif page == "about":
    # About screen:
    # - Static information about the app, authors, or context
    show_about_us()

else:
    # Fallback for invalid / unexpected page values:
    # - Reset to home to avoid the app breaking on a bad state
    st.session_state["page"] = "home"
    show_homepage()