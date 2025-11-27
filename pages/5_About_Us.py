import streamlit as st
from About_us import show_about_us

def render(back_button):
    back_button()
    show_about_us()
