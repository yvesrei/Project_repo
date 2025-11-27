import streamlit as st
from Questionnaire import show_questionnaire

def render(back_button):
    back_button()
    show_questionnaire()
