import streamlit as st
from statistics import mode
from Show_homepage import show_homepage
from Questionnaire import show_questionnaire
from spider_chart import group_taste_profile
from About_us import show_about_us
from api_client import api_access


def show_api_results():
    # Make sure we have the group results from spider_chart
    if "group_budget_numeric" not in st.session_state or "group_cuisine" not in st.session_state:
        st.error("Please go through the questionnaire and results page first.")
        return

    st.title("Matching Restaurants")

    # 👉 Call the Yelp API via api_access()
    results = api_access(
        latitude=47.3769,                            # TODO: replace with real latitude
        longitude=8.5417,                            # TODO: replace with real longitude
        open_at=1700000000,                          # TODO: real timestamp (Unix)
        radius=2000,                                 # in meters
        budget_level=st.session_state["group_budget_numeric"],
        cuisine=st.session_state["group_cuisine"]
    )

    if not results:
        st.warning("No restaurants found for these preferences.")
        return

    for r in results:
        st.write(f"### {r['name']}")
        st.write(f"⭐ Rating: {r['rating']}")
        st.write(f"💲 Price: {r['price']}")
        st.write(f"🍽 Categories: {', '.join(r['categories'])}")
        st.markdown("---")


         
## 1. Implement session state
# The Streamlit app reruns on every interaction, so we use:
# st.session_state to remember values between reruns.
# "page" controls which screen the user is on
# "num_of_participants" shows how many people will attend the dinner --> answer the questionnaire
# "current_participant"  --> Tracks which participant is currently filling out the questionnaire
# "answers" is the list in which each participants answers are stored

if "page" not in st.session_state:
        st.session_state["page"] = "home"


if "num_of_participants" not in st.session_state:
        st.session_state["num_of_participants"] = None


if "current_participant" not in st.session_state:
        st.session_state["current_participant"] = 1


if "answers" not in st.session_state:
        st.session_state["answers"] = []

## This block controls the page navigation in the app
# Depending on the value stored in st.session_state["page"],
# the corresponding screen is displayed through accessing the function

if st.session_state["page"] == "home":
    show_homepage()


if st.session_state["page"] == "questionnaire":
    show_questionnaire()


if st.session_state["page"] == "result":
    group_taste_profile(st.session_state["answers"])


if st.session_state["page"] == "api":
    show_api_results()
      


elif st.session_state["page"] == "about":
    show_about_us()

