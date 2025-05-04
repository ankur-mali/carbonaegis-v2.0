import streamlit as st
import pandas as pd
import numpy as np
import os
import io
import sys
from datetime import datetime

# Add parent directory to path to import utils
sys.path.append('..')
from utils.ai_assistant import generate_ai_response

# Page configuration
st.set_page_config(
    page_title="Data Input | Carbon Aegis",
    page_icon="📊",
    layout="wide"
)

# Add custom CSS
def add_custom_css():
    st.markdown("""
    <style>
    .main {
        padding: 1rem 2rem;
    }
    .block-container {
        padding-top: 1rem;
    }
    h1, h2, h3, h4, h5, h6 {
        font-family: 'IBM Plex Sans', sans-serif;
        font-weight: 600;
    }
    .stButton button {
        background-color: #0f62fe;
        color: white;
        font-weight: 500;
        border-radius: 4px;
        border: none;
        padding: 0.5rem 1rem;
    }
    .stButton button:hover {
        background-color: #0353e9;
    }
    .card {
        padding: 1.5rem;
        border-radius: 4px;
        background: #ffffff;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
    }
    .step-container {
        padding: 1rem;
        border-radius: 4px;
        background: #f4f4f4;
        margin-bottom: 1rem;
    }
    .active-step {
        border-left: 5px solid #0f62fe;
        background: #edf5ff;
    }
    .completed-step {
        border-left: 5px solid #42be65;
        background: #defbe6;
    }
    .step-header {
        display: flex;
        align-items: center;
        margin-bottom: 0.5rem;
    }
    .step-number {
        display: flex;
        justify-content: center;
        align-items: center;
        width: 1.5rem;
        height: 1.5rem;
        border-radius: 50%;
        background: #0f62fe;
        color: white;
        margin-right: 0.5rem;
        font-weight: bold;
    }
    .completed-step .step-number {
        background: #42be65;
    }
    .logo-container {
        margin-bottom: 2rem;
    }
    .logo-container img {
        max-height: 60px;
    }
    </style>
    """, unsafe_allow_html=True)

# Initialize session state variables
def init_session_state():
    if 'upload_step' not in st.session_state:
        st.session_state.upload_step = 1
    if 'uploaded_file' not in st.session_state:
        st.session_state.uploaded_file = None
    if 'uploaded_data' not in st.session_state:
        st.session_state.uploaded_data = None
    if 'column_mappings' not in st.session_state:
        st.session_state.column_mappings = {}
    if 'processed_data' not in st.session_state:
        st.session_state.processed_data = None
    if 'emissions_results' not in st.session_state:
        st.session_state.emissions_results = None
    if 'openai_enabled' not in st.session_state:
        # Check if OpenAI API key is available
        api_key = os.environ.get("OPENAI_API_KEY")
        st.session_state.openai_enabled = bool(api_key)

# Function to analyze a column with AI
def analyze_column_with_ai(column_name, sample_values=None):
    """Use OpenAI to analyze a column name and sample values to determine the emission category"""
    if not st.session_state.openai_enabled:
        return None
        
    try:
        # Prepare prompt for OpenAI
        prompt = f"""
        Analyze this column from an emissions data spreadsheet:
        
        Column name: {column_name}
        
        Sample values: {', '.join([str(v) for v in sample_values[:5]]) if sample_values is not None else 'No samples available'}
        
        Determine which of these categories this column most likely represents:
        1. date - A date or time column
        2. activity - Description of the emission activity or source
        3. amount - Numerical value representing quantity or consumption
        4. unit - Unit of measurement
        5. emission_factor - Emission factor used for calculations
        6. scope - Scope classification (1, 2, or 3)
        
        Return only the single most appropriate category name from the list above.
        """
        
        # Call OpenAI API via utility function
        response = generate_ai_response(prompt)
        
        # Clean and validate response
        response = response.strip().lower()
        valid_categories = ['date', 'activity', 'amount', 'unit', 'emission_factor', 'scope','text']
        
        # Extract the category if found in response
        for category in valid_categories:
            if category in response:
                return category
                
        return None
    
    except Exception as e:
        st.error(f"Error using AI to analyze column: {e}")
        return None

# Function to read an Excel file
def read_excel_file(uploaded_file):
    """Read and process an uploaded Excel file"""
    try:
        df = pd.read_excel(uploaded_file, engine='openpyxl')
        return df
    except Exception as e:
        st.error(f"Error reading Excel file: {e}")
        return None

# Detect column types in the DataFrame
def detect_column_types(df, use_ai=False):
    """Detect the types of columns in the DataFrame"""
    column_types = {}
    
    # Define patterns to look for
    patterns = {
        'date': ['date', 'year', 'month', 'period', 'time'],
        'activity': ['activity', 'description', 'type', 'source', 'category'],
        'amount': ['amount', 'quantity', 'volume', 'consumption', 'usage', 'kwh', 'kg', 'liters', 'km'],
        'unit': ['unit', 'uom', 'measure'],
        'emission_factor': ['factor', 'ef', 'emission', 'co2'],
        'scope': ['scope'],
        'text': ['text','name','departments','department','company name'],
    }
    
    # Check column names for matches
    for col in df.columns:
        col_lower = str(col).lower()
        
        # Check for pattern matches in column name
        matched = False
        for category, keywords in patterns.items():
            if any(keyword in col_lower for keyword in keywords):
                column_types[col] = category
                matched = True
                break
        
        # If no match found by name and AI is enabled, try AI analysis
        if not matched and use_ai and st.session_state.openai_enabled:
            sample_values = df[col].dropna().head(5).tolist() if not df[col].empty else None
            ai_category = analyze_column_with_ai(col, sample_values)
            
            if ai_category:
                column_types[col] = ai_category
                matched = True
        
        # If still no match, try to infer from content
        if not matched:
            infer_from_content(df, col, column_types)
    
    return column_types

# Get the emissions scope for a category
def get_scope_for_category(category):
    """Get the emissions scope for a category"""
    # Define category to scope mappings
    category_scopes = {
        'stationary_combustion': 1,
        'mobile_combustion': 1, 
        'fugitive_emissions': 1,
        'process_emissions': 1,
        'electricity': 2,
        'steam': 2,
        'heating': 2,
        'cooling': 2,
        'business_travel': 3,
        'employee_commuting': 3,
        'waste': 3,
        'purchased_goods': 3,
        'transportation': 3,
        'investments': 3
    }
    
    return category_scopes.get(category)

# Detect unit from a column of values
def detect_unit(column):
    """Detect the unit from a column of values"""
    common_units = {
        'kwh': 'kWh',
        'mwh': 'MWh',
        'kg': 'kg',
        'ton': 'tonnes',
        'tons': 'tonnes',
        'km': 'km',
        'miles': 'miles',
        'l': 'liters',
        'liter': 'liters',
        'liters': 'liters',
        'm3': 'm³',
        'cubic meter': 'm³',
        'cubic meters': 'm³',
        'm2': 'm²',
        'square meter': 'm²',
        'square meters': 'm²'
    }
    
    # Take most common unit mentioned
    if column.dtype == 'object':
        for unit_keyword, unit_name in common_units.items():
            if column.str.contains(unit_keyword, case=False, na=False).any():
                return unit_name
    
    return None

# Infer column type from content
def infer_from_content(df, column, column_types):
    """Infer column type from content"""
    # Check if it's a date column
    if pd.api.types.is_datetime64_any_dtype(df[column]):
        column_types[column] = 'date'
        return True
    
    # Check if it contains scope information
    if df[column].dtype == 'object':
        scope_pattern = df[column].astype(str).str.contains('scope', case=False, na=False)
        if scope_pattern.any():
            column_types[column] = 'scope'
            return True
    
    # Check if it's a numeric column (likely amount)
    if pd.api.types.is_numeric_dtype(df[column]):
        if 'amount' not in column_types.values():
            column_types[column] = 'amount'
            return True
        elif 'emission_factor' not in column_types.values():
            column_types[column] = 'emission_factor'
            return True
    
    # Check if it contains units
    if df[column].dtype == 'object':
        unit = detect_unit(df[column])
        if unit:
            column_types[column] = 'unit'
            return True
    
    # If still not categorized, check if it contains mostly text (likely activity)
    if df[column].dtype == 'object' and 'activity' not in column_types.values():
        avg_length = df[column].astype(str).str.len().mean()
        if avg_length > 5:  # Arbitrary threshold for text columns
            column_types[column] = 'activity'
            return True
    
    return False

# Map DataFrame to emission categories
def map_to_emission_categories(df, column_mappings, use_ai=False):
    """Map DataFrame to emission categories"""
    structured_data = {
        'scope1': {},
        'scope2': {},
        'scope3': {},
        'unclassified': {}
    }
    
    # Identify the relevant columns
    amount_col = next((col for col, cat in column_mappings.items() if cat == 'amount'), None)
    activity_col = next((col for col, cat in column_mappings.items() if cat == 'activity'), None)
    scope_col = next((col for col, cat in column_mappings.items() if cat == 'scope'), None)
    date_col = next((col for col, cat in column_mappings.items() if cat == 'date'), None)
    
    if not amount_col:
        return {"error": "No amount column identified"}
    
    # Process each row
    for idx, row in df.iterrows():
        # Get the amount
        amount = row[amount_col]
        if not pd.api.types.is_numeric_dtype(type(amount)):
            continue
            
        # Determine activity and category
        activity = str(row[activity_col]) if activity_col else "Unknown Activity"
        
        # Try to determine category from activity description
        category = "other"
        activity_lower = activity.lower()
        
        # Simple keyword-based categorization
        if any(keyword in activity_lower for keyword in ['electricity', 'power']):
            category = 'electricity'
        elif any(keyword in activity_lower for keyword in ['gas', 'fuel', 'diesel', 'petrol', 'gasoline']):
            category = 'stationary_combustion'
        elif any(keyword in activity_lower for keyword in ['vehicle', 'car', 'transport', 'fleet']):
            category = 'mobile_combustion'
        elif any(keyword in activity_lower for keyword in ['refrigerant', 'leakage', 'fugitive']):
            category = 'fugitive_emissions'
        elif any(keyword in activity_lower for keyword in ['air travel', 'flight']):
            category = 'business_travel'
        elif any(keyword in activity_lower for keyword in ['waste', 'disposal']):
            category = 'waste'
        
        # Determine scope
        scope = None
        
        # If scope column exists, use it
        if scope_col and not pd.isna(row[scope_col]):
            scope_value = str(row[scope_col]).lower()
            if '1' in scope_value:
                scope = 1
            elif '2' in scope_value:
                scope = 2
            elif '3' in scope_value:
                scope = 3
        
        # If scope not found in column, determine from category
        if scope is None:
            scope = get_scope_for_category(category)
        
        # Default to scope 3 if still not determined
        if scope is None:
            scope = 3
            
        # Get date if available
        date = None
        if date_col and not pd.isna(row[date_col]):
            date = row[date_col]
            if isinstance(date, (pd.Timestamp, datetime)):
                date = date.strftime('%Y-%m-%d')
        
        # Structure the data
        scope_key = f'scope{scope}'
        if category not in structured_data[scope_key]:
            structured_data[scope_key][category] = []
        
        # Add to appropriate category
        structured_data[scope_key][category].append({
            'description': activity,
            'amount': float(amount),
            'date': date
        })
    
    return structured_data

# Calculate emissions based on structured data
def calculate_emissions(structured_data, emission_factors=None):
    """Calculate emissions based on structured data"""
    # Default emission factors (simplified)
    default_factors = {
        'electricity': 0.45,  # kg CO2e per kWh
        'stationary_combustion': 0.18,  # kg CO2e per kWh
        'mobile_combustion': 2.3,  # kg CO2e per liter
        'fugitive_emissions': 1800,  # kg CO2e per kg (approximate for common refrigerants)
        'business_travel': 0.15,  # kg CO2e per km
        'employee_commuting': 0.15,  # kg CO2e per km
        'waste': 0.5,  # kg CO2e per kg
        'purchased_goods': 0.8,  # kg CO2e per unit
        'other': 1.0  # Generic factor
    }
    
    # Use provided emission factors if available
    factors = emission_factors if emission_factors else default_factors
    
    results = {
        'total_emissions': 0,
        'by_scope': {
            'Scope 1': 0,
            'Scope 2': 0,
            'Scope 3': 0
        },
        'by_category': {},
        'line_items': []
    }
    
    # Process each scope
    for scope_key, categories in structured_data.items():
        # Skip if not a valid scope
        if scope_key not in ['scope1', 'scope2', 'scope3']:
            continue
            
        # Get scope number for results
        scope_num = int(scope_key[-1])
        scope_name = f'Scope {scope_num}'
        
        # Process each category in this scope
        for category, items in categories.items():
            # Get emission factor for this category
            ef = factors.get(category, factors['other'])
            
            # Calculate emissions for each item
            for item in items:
                amount = item['amount']
                emissions = amount * ef
                
                # Update results
                results['total_emissions'] += emissions
                results['by_scope'][scope_name] += emissions
                
                # Update category breakdown
                if category not in results['by_category']:
                    results['by_category'][category] = 0
                results['by_category'][category] += emissions
                
                # Add line item
                results['line_items'].append({
                    'scope': scope_name,
                    'category': category,
                    'description': item['description'],
                    'amount': amount,
                    'emission_factor': ef,
                    'emissions': emissions,
                    'date': item.get('date')
                })
    
    return results

# Convert structured data to app format
def convert_to_app_format(structured_data, calculation_results):
    """Convert structured data and calculation results to app format"""
    app_data = {
        'total': calculation_results['total_emissions'],
        'by_scope': calculation_results['by_scope'],
        'by_category': calculation_results['by_category'],
        'line_items': pd.DataFrame(calculation_results['line_items'])
    }
    
    return app_data

# Save data to session state
def save_to_session_state(data):
    """Save data to session state for persistence"""
    st.session_state.processed_data = data
    st.session_state.upload_step = 4  # Move to completed state
    
    # Here you would also save to database if needed
    st.success("Data processed and saved successfully!")

# Clear all data
def clear_data():
    """Clear all data from session state"""
    st.session_state.upload_step = 1
    st.session_state.uploaded_file = None
    st.session_state.uploaded_data = None
    st.session_state.column_mappings = {}
    st.session_state.processed_data = None
    st.session_state.emissions_results = None

# Main function
def main():
    add_custom_css()
    init_session_state()
    
    # Display logo
    st.image("assets/logo.png", width=180)
    
    st.title("Data Import and Processing")
    st.write("Upload and process your emissions data.")
    
    # Progress steps visualization
    col1, col2, col3 = st.columns(3)
    
    with col1:
        step_class = "active-step" if st.session_state.upload_step == 1 else ("completed-step" if st.session_state.upload_step > 1 else "step-container")
        st.markdown(f"""
        <div class="step-container {step_class}">
            <div class="step-header">
                <div class="step-number">1</div>
                <strong>Upload Excel File</strong>
            </div>
            <div>Upload your emissions data in Excel format.</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        step_class = "active-step" if st.session_state.upload_step == 2 else ("completed-step" if st.session_state.upload_step > 2 else "step-container")
        st.markdown(f"""
        <div class="step-container {step_class}">
            <div class="step-header">
                <div class="step-number">2</div>
                <strong>Map Columns</strong>
            </div>
            <div>Confirm how columns map to emission categories.</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col3:
        step_class = "active-step" if st.session_state.upload_step == 3 else ("completed-step" if st.session_state.upload_step > 3 else "step-container")
        st.markdown(f"""
        <div class="step-container {step_class}">
            <div class="step-header">
                <div class="step-number">3</div>
                <strong>Calculate Emissions</strong>
            </div>
            <div>Process data and calculate GHG emissions.</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Step 1: Upload Excel file
    if st.session_state.upload_step == 1:
        st.subheader("Step 1: Upload Excel File")
        
        # File uploader for Excel files
        uploaded_file = st.file_uploader("Upload your emissions data", type=["xlsx", "xls"])
        
        # Sample data option
        st.write("Or use a sample dataset:")
        if st.button("Load Sample Data"):
            # Use a sample file from assets directory
            uploaded_file = "attached_assets/GHG_emissions_calculator_ver01.1_web (1) (1).xlsx"
            st.session_state.is_sample = True
        
        if uploaded_file is not None:
            if isinstance(uploaded_file, str):
                # It's a sample file path
                df = pd.read_excel(uploaded_file, engine='openpyxl')
                st.session_state.uploaded_file = uploaded_file
            else:
                # It's an uploaded file
                df = read_excel_file(uploaded_file)
                st.session_state.uploaded_file = uploaded_file
            
            if df is not None:
                st.session_state.uploaded_data = df
                st.write("Preview of uploaded data:")
                st.dataframe(df.head())
                
                # Use AI for column detection if available
                use_ai = st.checkbox("Use AI for enhanced column detection", 
                                     value=st.session_state.openai_enabled,
                                     disabled=not st.session_state.openai_enabled)
                
                if not st.session_state.openai_enabled and use_ai:
                    st.info("AI detection requires an OpenAI API key.")
                
                if st.button("Proceed to Column Mapping", type="primary"):
                    with st.spinner("Analyzing columns..."):
                        st.session_state.column_mappings = detect_column_types(df, use_ai=use_ai)
                        st.session_state.upload_step = 2
                        st.rerun()
    
    # Step 2: Map columns
    elif st.session_state.upload_step == 2:
        st.subheader("Step 2: Map Columns to Emission Categories")
        
        df = st.session_state.uploaded_data
        column_types = st.session_state.column_mappings
        
        st.write("Please confirm or adjust the column mappings:")
        
        # Create a form for mapping columns
        with st.form("column_mapping_form"):
            new_mappings = {}
            
            for col in df.columns:
                suggested_type = column_types.get(col, None)
                options = ['Not Used', 'date', 'activity', 'amount', 'unit', 'emission_factor', 'scope']
                default_index = options.index(suggested_type) if suggested_type in options else 0
                
                new_mappings[col] = st.selectbox(
                    f"Map column: {col}",
                    options=options,
                    index=default_index,
                    key=f"mapping_{col}"
                )
            
            submitted = st.form_submit_button("Confirm Mappings", type="primary")
            
            if submitted:
                # Update mappings, filtering out "Not Used" columns
                st.session_state.column_mappings = {
                    col: mapping for col, mapping in new_mappings.items() if mapping != 'Not Used'
                }
                st.session_state.upload_step = 3
                st.rerun()
        
        if st.button("Back to Upload"):
            st.session_state.upload_step = 1
            st.rerun()
    
    # Step 3: Calculate emissions
    elif st.session_state.upload_step == 3:
        st.subheader("Step 3: Calculate Emissions")
        
        df = st.session_state.uploaded_data
        mappings = st.session_state.column_mappings
        
        st.write("Ready to calculate emissions based on the following mappings:")
        
        # Display the confirmed mappings
        mapping_data = [{"Column": col, "Category": cat} for col, cat in mappings.items()]
        st.table(pd.DataFrame(mapping_data))
        
        if st.button("Calculate Emissions", type="primary"):
            with st.spinner("Processing data and calculating emissions..."):
                # Map data to structured format
                structured_data = map_to_emission_categories(df, mappings, use_ai=st.session_state.openai_enabled)
                
                if "error" in structured_data:
                    st.error(structured_data["error"])
                else:
                    # Calculate emissions
                    results = calculate_emissions(structured_data)
                    st.session_state.emissions_results = results
                    
                    # Convert to app format
                    processed_data = convert_to_app_format(structured_data, results)
                    
                    # Save data
                    save_to_session_state(processed_data)
                    
                    # Show success and summary
                    st.success("Emissions calculated successfully!")
                    st.markdown(f"""
                    ### Summary Results
                    
                    **Total Emissions:** {results['total_emissions']:.2f} kg CO2e
                    
                    **By Scope:**
                    - Scope 1: {results['by_scope']['Scope 1']:.2f} kg CO2e
                    - Scope 2: {results['by_scope']['Scope 2']:.2f} kg CO2e
                    - Scope 3: {results['by_scope']['Scope 3']:.2f} kg CO2e
                    """)
                    
                    # Offer to view dashboard
                    if st.button("View Dashboard"):
                        st.switch_page("pages/2_Dashboard.py")
        
        if st.button("Back to Column Mapping"):
            st.session_state.upload_step = 2
            st.rerun()
    
    # Step 4: Completed
    elif st.session_state.upload_step == 4:
        st.subheader("Data Processing Complete")
        
        st.success("Your emissions data has been processed successfully!")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("View Dashboard"):
                st.switch_page("pages/2_Dashboard.py")
        
        with col2:
            if st.button("Start Over"):
                clear_data()
                st.rerun()

if __name__ == "__main__":
    main()