# This file is stored in the pages directory
# Streamlit loads it automatically as an independent page

import streamlit as st
from session_init import init_session
init_session()

from About_us import show_about_us



show_about_us()
