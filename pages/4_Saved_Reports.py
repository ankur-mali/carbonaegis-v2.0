import streamlit as st
import pandas as pd
from datetime import datetime
from utils.data_manager import init_session_state, load_emission_data, get_saved_calculations
from utils.database import get_all_emission_data

# Initialize session state if needed
init_session_state()

st.title("Saved Emissions Data and Reports")

# Get all saved calculations
saved_records = get_saved_calculations()

if not saved_records:
    st.info("No saved emission data found in the database.")
else:
    st.subheader("Saved Emission Calculations")
    
    # Create a DataFrame for display
    records_data = {
        "ID": [],
        "Organization": [],
        "Year": [],
        "Time Period": [],
        "Calculation Method": [],
        "Scope 1 (tCO₂e)": [],
        "Scope 2 (tCO₂e)": [],
        "Scope 3 (tCO₂e)": [],
        "Total (tCO₂e)": [],
        "Created Date": []
    }
    
    # Fill the DataFrame with records
    for record in saved_records:
        records_data["ID"].append(record.get('id'))
        records_data["Organization"].append(record.get('organization_name', 'Unknown'))
        records_data["Year"].append(record.get('report_year', 'N/A'))
        records_data["Time Period"].append(record.get('time_period', 'Annually'))
        records_data["Calculation Method"].append(record.get('calculation_method', 'Exact'))
        records_data["Scope 1 (tCO₂e)"].append(round(record.get('scope1_emissions', 0.0), 2))
        records_data["Scope 2 (tCO₂e)"].append(round(record.get('scope2_emissions', 0.0), 2))
        records_data["Scope 3 (tCO₂e)"].append(round(record.get('scope3_emissions', 0.0), 2))
        records_data["Total (tCO₂e)"].append(round(record.get('total_emissions', 0.0), 2))
        # Handle different date formats
        created_at = record.get('created_at', datetime.now())
        if isinstance(created_at, str):
            date = created_at
        else:
            date = created_at.strftime('%Y-%m-%d %H:%M')
        
        records_data["Created Date"].append(date)
    
    # Create and display DataFrame
    records_df = pd.DataFrame(records_data)
    st.dataframe(records_df, use_container_width=True)
    
    # Allow loading selected record
    selected_id = st.selectbox(
        "Select a record to load:", 
        options=[0] + records_data["ID"],
        format_func=lambda x: f"Select a record..." if x == 0 else f"ID: {x} - {records_data['Organization'][records_data['ID'].index(x)]} ({records_data['Year'][records_data['ID'].index(x)]})"
    )
    
    if selected_id != 0:
        if st.button("Load Selected Record"):
            success = load_emission_data(selected_id)
            if success:
                st.success(f"Successfully loaded record #{selected_id}. Navigate to Dashboard to view details.")
                # Redirect to dashboard
                st.switch_page("pages/2_Dashboard.py")
            else:
                st.error("Failed to load the selected record.")

# Execute SQL query to check reports table
try:
    from utils.database import get_db_engine
    
    st.subheader("Saved Reports")
    
    # Query for saved reports using SQLAlchemy engine
    engine = get_db_engine()
    with engine.connect() as connection:
        report_results = connection.execute("""
            SELECT r.id, r.report_name, r.report_type, r.organization_name, 
                  r.report_year, r.prepared_by, r.report_date, r.created_at, 
                  e.total_emissions
            FROM reports r
            JOIN emission_data e ON r.emission_data_id = e.id
            ORDER BY r.created_at DESC
        """).fetchall()
    
    if not report_results:
        st.info("No saved reports found in the database.")
    else:
        # Create a DataFrame for display
        reports_data = {
            "ID": [],
            "Report Name": [],
            "Type": [],
            "Organization": [],
            "Year": [],
            "Total Emissions (tCO₂e)": [],
            "Created Date": []
        }
        
        # Fill the DataFrame with records
        for report in report_results:
            reports_data["ID"].append(report[0])
            reports_data["Report Name"].append(report[1])
            reports_data["Type"].append(report[2].upper())
            reports_data["Organization"].append(report[3] or 'Unknown')
            reports_data["Year"].append(report[4] or 'N/A')
            reports_data["Total Emissions (tCO₂e)"].append(round(report[8] or 0.0, 2))
            
            # Format date
            created_date = report[7]
            if isinstance(created_date, str):
                reports_data["Created Date"].append(created_date)
            else:
                reports_data["Created Date"].append(created_date.strftime('%Y-%m-%d %H:%M') if created_date else 'Unknown')
        
        # Create and display DataFrame
        reports_df = pd.DataFrame(reports_data)
        st.dataframe(reports_df, use_container_width=True)
        
except Exception as e:
    st.error(f"Error retrieving reports: {str(e)}")

# Navigation
st.markdown("## Navigation")
col1, col2 = st.columns(2)
with col1:
    if st.button("⬅️ Return to Dashboard"):
        st.switch_page("pages/2_Dashboard.py")
with col2:
    if st.button("🏠 Go to Home"):
        st.switch_page("app.py")