import streamlit as st


st.write("jeay, we connecetd everyhting" \
         
"")

st.button("Click here to start a dinner")

from Feature_01 import return_even

pist=[i for i in range(10)]

even_list = return_even(pist)
st.write(even_list)

