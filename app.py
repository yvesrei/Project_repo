import streamlit as st
from statistics import mode
from Show_homepage import show_homepage
from Questionnaire import show_questionnaire
from spider_chart import group_taste_profile
from About_us import show_about_us
from api_client import api_access


import streamlit as st
import importlib
from api_client import api_access


# ------------------------------------------------------------
# 1) BASIC CONFIGURATION
# ------------------------------------------------------------
# Streamlit page settings
st.set_page_config(page_title="FoodMingle", layout="wide")

# ------------------------------------------------------------
# 2) PAGE REGISTRY
# ------------------------------------------------------------
# This dictionary maps the visible page names in the navigation
# bar to the matching Python modules inside the /pages folder.
# Each module contains a render(back_button) function.
PAGES = {
    "Homepage": "1_Homepage",
    "Questionnaire": "2_Questionnaire",
    "Result": "3_Result",
    "Restaurant Matches": "4_API_Results",
    "About Us": "5_About_Us",
}


# ------------------------------------------------------------
# 3) SESSION STATE INITIALIZATION
# ------------------------------------------------------------
# We store:
# - current_page: which page the user is on
# - history: to enable a working "Back" button

if "history" not in st.session_state:
    # Holds the navigation history (stack)
    st.session_state.history = []

if "current_page" not in st.session_state:
    # Default start page
    st.session_state.current_page = "Homepage"


# ------------------------------------------------------------
# 4) TOP NAVIGATION BAR
# ------------------------------------------------------------
# This replaces your old manual router. Streamlit now shows
# a native navigation bar at the top, like a real website.

navigation = st.navigation({"FoodMingle": list(PAGES.keys())})
selected_page = navigation.run()


# ------------------------------------------------------------
# 5) HISTORY MANAGEMENT (for BACK BUTTON)
# ------------------------------------------------------------
# Only add to history when changing pages.

if selected_page != st.session_state.current_page:
    st.session_state.history.append(st.session_state.current_page)
    st.session_state.current_page = selected_page


# ------------------------------------------------------------
# 6) BACK BUTTON IMPLEMENTATION
# ------------------------------------------------------------
# This creates a real "Back" button that returns the user to
# the previously visited page, not always to the homepage.

def back_button():
    if st.session_state.history:
        if st.button("⬅️ Back"):
            st.session_state.current_page = st.session_state.history.pop()
            st.rerun()


# ------------------------------------------------------------
# 7) PAGE LOADING
# ------------------------------------------------------------
# We dynamically import the module for the selected page and
# call its render(back_button) function.

module = importlib.import_module(f"pages.{PAGES[st.session_state.current_page]}")
module.render(back_button)


# ------------------------------------------------------------
# 8) API RESULT PAGE FUNCTION (kept from your original code)
# ------------------------------------------------------------
# This function is used inside pages/4_API_Results.py.
# It displays restaurant matches after the taste profile is
# computed in the spider_chart result page.

def show_api_results():

    # Stop if required group results are missing
    if "group_budget_numeric" not in st.session_state or "group_cuisine" not in st.session_state:
        st.error("Please go through the questionnaire and results page first.")
        return

    # Let the user select a supported city
    city = st.selectbox(
        "Choose your city",
        [
            "Zurich", "Basel", "Geneva", "Lausanne", "Winterthur",
            "St. Gallen", "Lugano", "Bern", "Luzern"
        ]
    )

    # Page title
    st.title(f"Matching Restaurants in {city}!")

    # Call the Yelp-like API (your function from api_client.py)
    results = api_access(
        city=city,
        radius=2000,
        budget_level=st.session_state["group_budget_numeric"],
        cuisine=st.session_state["group_cuisine"],
    )

    # Handle empty results
    if not results:
        st.warning("No restaurants found even after relaxing filters.")
        return

    # Display each restaurant's information
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
