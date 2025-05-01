import streamlit as st

st.set_page_config(page_title="Carbon Aegis", layout="wide")

# Apply custom styling for a cleaner look
st.markdown("""
<style>
.main {
    padding: 2rem;
}
.block-container {
    max-width: 1200px;
    padding-top: 1rem;
    padding-bottom: 1rem;
}
h1, h2, h3 {
    font-weight: 600;
}
.stButton button {
    border-radius: 4px;
    padding: 0.5rem 1rem;
    font-weight: 500;
}
.stButton button:hover {
    border-color: #106810;
}
</style>
""", unsafe_allow_html=True)

# Header
st.title("Carbon Aegis - Greenhouse Gas Emissions Calculator")
st.write("Welcome to Carbon Aegis, your solution for tracking, calculating, and managing GHG emissions.")

# Create tabs for navigation
tabs = st.tabs(["Home", "Smart Data Import", "About"])

with tabs[0]:
    st.header("Carbon Footprint Management Solution")
    
    cols = st.columns([2, 1])
    
    with cols[0]:
        st.markdown("""
        Carbon Aegis is an advanced web application designed to help organizations 
        comprehensively calculate, analyze, and reduce greenhouse gas (GHG) emissions 
        across multiple operational scopes.
        
        ### Key Features:
        - **Comprehensive Emissions Calculation**: Track emissions across Scope 1, 2, and 3
        - **AI-Powered Data Import**: Upload any Excel sheet and our AI will map it automatically
        - **Interactive Analytics**: Visualize your emissions with detailed breakdowns
        - **Framework Alignment**: Check your compliance with global reporting standards
        """)
        
        if st.button("Launch Smart Data Import", type="primary"):
            st.switch_page("pages/1_Data_Input_clean.py")
    
    with cols[1]:
        st.image("attached_assets/Untitled design.png", width=300)
        st.caption("Carbon Aegis: Empowering businesses to take climate action")

with tabs[1]:
    st.header("Smart Data Import")
    
    st.markdown("""
    Our updated Data Import feature works with any Excel format:
    
    1. **Intelligent Column Detection**: Automatically identifies data types
    2. **No External APIs**: All processing happens locally in your browser
    3. **AI Enhancement**: Optional OpenAI integration for better accuracy
    4. **Interactive Mapping**: Review and adjust before calculation
    5. **Detailed Results**: See exactly how emissions are calculated
    """)
    
    st.markdown("""
    ### How It Works:
    
    1. **Upload** your Excel file with emissions data
    2. **Review** the automatic column mappings
    3. **Calculate** emissions based on GHG Protocol
    4. **Save** results for dashboards and reports
    """)
    
    if st.button("Try Smart Data Import Now", type="primary"):
        st.switch_page("pages/1_Data_Input_clean.py")

with tabs[2]:
    st.header("About Carbon Aegis")
    
    st.markdown("""
    Carbon Aegis helps organizations measure, manage, and reduce their greenhouse gas emissions.
    
    ### Based on Global Standards
    - GHG Protocol Corporate Standard
    - DEFRA Conversion Factors
    - ISO 14064-1:2018
    
    ### Commitment to Accuracy
    Our calculation engine uses up-to-date emission factors from authoritative sources to ensure
    your carbon accounting is accurate and defensible.
    
    ### Support for All Organization Types
    Whether you're a small business just starting your climate journey or a multinational
    corporation with complex reporting needs, Carbon Aegis scales to meet your requirements.
    """)