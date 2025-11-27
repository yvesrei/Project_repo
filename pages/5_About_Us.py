import streamlit as st
from About_us import show_about_us

st.button("⬅️ Back", on_click=lambda: st.session_state.pop("nav_history", None))
show_about_us()

