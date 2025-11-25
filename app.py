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

    st.title("Matching Restaurants in Zürich!")

    # Call the Yelp API via api_access()
    results = api_access(
        latitude=47.3769,   # ignored internally, we always use Zurich in api_client
        longitude=8.5417,
        open_at=1700000000,
        radius=2000,
        budget_level=st.session_state["group_budget_numeric"],
        cuisine=st.session_state["group_cuisine"]
    )

    if not results:
        st.warning("No restaurants found even after relaxing filters.")
        return

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

