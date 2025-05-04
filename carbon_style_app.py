import streamlit as st
import pandas as pd
import numpy as np
import os
from datetime import datetime
import plotly.express as px

# Set page configuration
st.set_page_config(
    page_title="Carbon Aegis",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add custom CSS
def add_custom_css():
    st.markdown("""
    <style>
    .main { padding: 1rem 2rem; }
    .block-container { padding-top: 1rem; }
    h1, h2, h3, h4, h5, h6 { font-family: 'IBM Plex Sans', sans-serif; font-weight: 600; }
    .stButton button { background-color: #0f62fe; color: white; font-weight: 500; border-radius: 4px; border: none; padding: 0.5rem 1rem; }
    .stButton button:hover { background-color: #0353e9; }
    .card { padding: 1.5rem; border-radius: 4px; background: #ffffff; box-shadow: 0 1px 3px rgba(0,0,0,0.1); margin-bottom: 1rem; }
    .metric-card { text-align: center; padding: 1rem; border-radius: 4px; background: #f4f4f4; }
    .metric-value { font-size: 1.8rem; font-weight: 600; margin-bottom: 0.5rem; }
    .metric-label { font-size: 0.9rem; color: #6f6f6f; }
    .logo-container { margin-bottom: 2rem; }
    .logo-container img { max-height: 60px; }
    </style>
    """, unsafe_allow_html=True)

# Initialize session state
def init_session_state():
    defaults = {
        'page': 'home',
        'upload_step': 1,
        'uploaded_file': None,
        'uploaded_data': None,
        'column_mappings': {},
        'processed_data': None,
        'emissions_results': None
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val

# Navigation helper
def navigate_to(page):
    st.session_state.page = page
    if page == 'upload': st.session_state.upload_step = 1

# Format numbers
def format_number(number, precision=2):
    try:
        return f"{number:,.{precision}f}"
    except Exception:
        return number

# Process Excel
def process_excel_file(uploaded_file):
    try:
        return pd.read_excel(uploaded_file, engine='openpyxl')
    except Exception as e:
        st.error(f"Error reading Excel file: {e}")
        return None

# Detect column types
def detect_column_types(df):
    types = {}
    patterns = {
        'date': ['date', 'year', 'month', 'period', 'time'],
        'activity': ['activity', 'description', 'type', 'source', 'category'],
        'amount': ['amount', 'quantity', 'volume', 'consumption', 'usage'],
        'unit': ['unit', 'uom', 'measure'],
        'emission_factor': ['factor', 'ef', 'emission'],
        'scope': ['scope']
    }
    for col in df.columns:
        col_l = str(col).lower()
        for cat, kws in patterns.items():
            if any(kw in col_l for kw in kws):
                types[col] = cat
                break
    for col in df.columns:
        if col in types: continue
        ser = df[col]
        if np.issubdtype(ser.dtype, np.datetime64):
            types[col] = 'date'
        elif pd.api.types.is_numeric_dtype(ser):
            # assign amount if missing, else emission_factor
            if 'amount' not in types.values(): types[col] = 'amount'
            elif 'emission_factor' not in types.values(): types[col] = 'emission_factor'
        elif ser.dropna().apply(lambda x: isinstance(x, str) and 'scope' in x.lower()).all():
            types[col] = 'scope'
        elif ser.dropna().apply(lambda x: isinstance(x, str) and len(x) < 10).all():
            common = ['kg','ton','mt','km','kwh','mwh','liter','gallon','m3']
            if ser.dropna().str.lower().str.contains('|'.join(common)).any():
                types[col] = 'unit'
        else:
            types[col] = 'activity'
    return types

# Calculate emissions
def calculate_emissions(df, mappings):
    amt = next((c for c,m in mappings.items() if m=='amount'), None)
    act = next((c for c,m in mappings.items() if m=='activity'), None)
    scp = next((c for c,m in mappings.items() if m=='scope'), None)
    efc = next((c for c,m in mappings.items() if m=='emission_factor'), None)
    if not amt:
        return {'error': 'No amount column identified'}
    results = {'total_emissions':0, 'by_scope':{'Scope 1':0,'Scope 2':0,'Scope 3':0}, 'by_category':{}, 'line_items':[]}
    defaults = {'electricity':0.45,'natural_gas':0.18,'vehicle_fuel':2.3,'air_travel':0.15,'rail_travel':0.04,'waste':0.5,'default':1.0}
    for _, row in df.iterrows():
        val = row.get(amt)
        if not isinstance(val, (int, float, np.number)): continue
        actv = row.get(act, 'Unknown')
        ef = row.get(efc) if efc else None
        ef = float(ef) if isinstance(ef, (int, float, np.number)) else None
        if ef is None:
            low = str(actv).lower()
            ef = next((f for k,f in defaults.items() if k in low), defaults['default'])
        emis = val * ef
        scope = 'Scope 3'
        if scp and pd.notna(row.get(scp)):
            s = str(row.get(scp)).lower()
            if '1' in s: scope='Scope 1 Emissions'
            elif '2' in s: scope='Scope 2'
            elif '3' in s: scope='Scope 3'

        results['total_emissions'] += emis
        results['by_scope'][scope] += emis
        cat = str(actv)[:50]
        results['by_category'][cat] = results['by_category'].get(cat,0)+emis
        results['line_items'].append({'activity':actv,'amount':val,'emission_factor':ef,'emissions':emis,'scope':scope})
    return results

# Page content functions

def display_home_page():
    st.title("Welcome to Carbon Aegis")
    st.markdown("...", unsafe_allow_html=True)

def display_upload_page(): pass

def display_dashboard_page(): pass

def display_reports_page(): pass

# Main
def main():
    add_custom_css()
    init_session_state()
    with st.sidebar:
        logo = os.path.join('assets', 'logo.png')
        if os.path.exists(logo): st.image(logo, width=180)
        st.markdown("---")
        st.subheader("Navigation")
        for name,page in [('Home','home'),('Upload','upload'),('Dashboard','dashboard'),('Reports','reports')]:
            if st.button(name, use_container_width=True): navigate_to(page)
        st.markdown("---")
        st.caption("© 2025 Carbon Aegis. v1.0")
    if st.session_state.page=='home': display_home_page()
    elif st.session_state.page=='upload': display_upload_page()
    elif st.session_state.page=='dashboard': display_dashboard_page()
    elif st.session_state.page=='reports': display_reports_page()

if __name__ == '__main__':
    main()
