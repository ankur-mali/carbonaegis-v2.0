import streamlit as st

st.title("Carbon Aegis - Simple Test")
st.write("This is a simple test of the Streamlit environment.")

st.header("About Carbon Aegis")
st.write("""
Carbon Aegis is a comprehensive web application for calculating, analyzing, and visualizing 
greenhouse gas (GHG) emissions across multiple operational scopes.
""")

if st.button("Click me!"):
    st.success("Button clicked!")