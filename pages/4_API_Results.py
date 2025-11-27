import streamlit as st
from app import show_api_results

st.button("⬅️ Back", on_click=lambda: st.session_state.pop("nav_history", None))
show_api_results()

