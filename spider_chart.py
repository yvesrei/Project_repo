
import streamlit as st
import numpy as np
import plotly.graph_objects as go


def group_taste_profile(answers):

    st.title("This is your groups taste profile of today!")

    st.subheader("Let's analyze it.")

    budget_dict:{"$":1, "$$":2, "$$$":3}

    budget_scores= []
    budget_weights=[]

    for participant in answers:
        
        budget_value= participant["budget"]

        numeric_budget= budget_dict[budget_value]

        budget_import= participant["budget_importance"]

        weighted_score= numeric_budget * budget_import

        budget_scores.append(weighted_score)

        budget_weights.append(budget_import)



    st.write(st.session_state["answers"])


def create_spiderchart(values):
    x=0

