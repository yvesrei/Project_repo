# This file is stored in the pages directory
# Streamlit loads it automatically as an independent page

import streamlit as st
from session_init import init_session
init_session()

# Import the actual homepage function
from Show_homepage import show_homepage

# Show the homepage
show_homepage()

