import streamlit as st
from statistics import mode
from Show_homepage import show_homepage
from Questionnaire import show_questionnaire
from spider_chart import group_taste_profile
from About_us import show_about_us
from api_client import api_access


import streamlit as st
from streamlit import Page

st.set_page_config(page_title="FoodMingle", layout="wide")

st.navigation(
    {
        "FoodMingle": [
            Page("pages/1_Homepage.py", title="Homepage"),
            Page("pages/2_Questionnaire.py", title="Questionnaire"),
            Page("pages/3_Result.py", title="Result"),
            Page("pages/4_API_Results.py", title="Restaurant Matches"),
            Page("pages/5_About_Us.py", title="About Us"),
        ]
    }
).run()


# --- Keep your API function here, unchanged ---
from api_client import api_access

def show_api_results():

    if "group_budget_numeric" not in st.session_state or "group_cuisine" not in st.session_state:
        st.error("Please go through the questionnaire and results page first.")
        return

    city = st.selectbox(
        "Choose your city",
        ["Zurich", "Basel", "Geneva", "Lausanne", "Winterthur",
         "St. Gallen", "Lugano", "Bern", "Luzern"]
    )

    st.title(f"Matching Restaurants in {city}!")

    results = api_access(
        city=city,
        radius=2000,
        budget_level=st.session_state["group_budget_numeric"],
        cuisine=st.session_state["group_cuisine"],
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
            st.text(r["opening_hours"])

        if r["menu_url"]:
            st.markdown(f"[Menu]({r['menu_url']})")

        st.markdown("---")
