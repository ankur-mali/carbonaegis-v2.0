import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO

from carbon_style_app import detect_column_types, calculate_emissions


def streamlit_main():
    # ---------- Hero Section ----------
    st.image("assets/logo.png", width=100)
    st.markdown("""
        <style>
            .hero-title {
                font-size: 36px;
                font-weight: 800;
                color: #0f62fe;
                margin-bottom: 0.2em;
            }
            .hero-subtitle {
                font-size: 18px;
                color: #555;
            }
            .section-title {
                font-size: 24px;
                font-weight: 600;
                margin-top: 2em;
                color: #161616;
            }
            .feature-card {
                border: 1px solid #eee;
                border-radius: 12px;
                padding: 1em;
                background-color: #f9f9f9;
            }
        </style>

        <div class="hero-title"> Carbon Aegis</div>
        <div class="hero-subtitle">Your gateway to effortless GHG emissions tracking, reporting, and ESG readiness.</div>
    """, unsafe_allow_html=True)

    st.markdown("## 🚀 Get Started")
    st.write(
        "Upload your Excel file to calculate and visualize your emissions. Our intelligent engine detects scopes and categories automatically.")

    uploaded_file = st.file_uploader("📤 Upload Excel File", type=["xlsx", "xls"])

    if uploaded_file is not None:
        df = pd.read_excel(uploaded_file)
        st.success("✅ Excel file loaded successfully.")
        st.write("### 📊 Raw Data")
        st.dataframe(df)

        column_types = detect_column_types(df)
        results = calculate_emissions(df, column_types)

        st.write("### 🌍 Total Emissions")
        st.metric("Total Emissions (kg CO2e)", f"{results['total_emissions']:.2f}")

        st.write("### 📈 Emissions by Scope")
        st.bar_chart(pd.Series(results['by_scope']))

        st.write("### 📊 Emissions by Category")
        st.bar_chart(pd.Series(results['by_category']))

        st.write("### 🧾 Line Item Details")
        st.dataframe(pd.DataFrame(results['line_items']))

    # ---------- Features Section ----------
    st.markdown("""<div class="section-title">💡 Why Carbon Aegis?</div>""", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(
            """<div class='feature-card'>✅ Easy Emission Upload<br>Drag-and-drop Excel uploads with auto-detection.</div>""",
            unsafe_allow_html=True)
    with col2:
        st.markdown(
            """<div class='feature-card'>📊 Real-time Insights<br>Scope 1, 2, 3 calculations and visual dashboards.</div>""",
            unsafe_allow_html=True)
    with col3:
        st.markdown(
            """<div class='feature-card'>🔒 Secure & Compliant<br>Built for CSRD, GRI and ESG compliance.</div>""",
            unsafe_allow_html=True)

    # ---------- Footer ----------
    st.markdown("""<hr><center>Made with ❤️ by the Carbon Aegis Team</center>""", unsafe_allow_html=True)


# Make sure your detect_column_types and calculate_emissions are also defined in the file

if __name__ == "__main__":
    streamlit_main()