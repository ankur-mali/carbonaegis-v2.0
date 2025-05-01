import streamlit as st

st.title("Debug App")
st.write("If you can see this, the Streamlit app is working correctly.")

if st.button("Click me"):
    st.success("Button clicked!")