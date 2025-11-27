import streamlit as st
from session_init import init_session
init_session()

from Show_homepage import show_homepage

# Homepage does not need a back button
show_homepage()

    