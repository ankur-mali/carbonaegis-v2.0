import streamlit as st
import pandas as pd
import numpy as np
import re

def read_excel_file(file):
    """
    Read uploaded Excel file into a pandas DataFrame
    
    Parameters:
    -----------
    file : UploadedFile
        The Excel file uploaded by the user
        
    Returns:
    --------
    pd.DataFrame
        DataFrame containing the imported data
    """
    try:
        # First save the uploaded file to a temporary location
        import tempfile
        import os
        
        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp_file:
            # Write the uploaded file data to the temporary file
            tmp_file.write(file.getvalue())
            tmp_path = tmp_file.name
        
        # Now read from the temporary file
        df = pd.read_excel(tmp_path)
        
        # Clean up by removing the temporary file
        os.unlink(tmp_path)
        
        return df
    except Exception as e:
        st.error(f"Error reading Excel file: {str(e)}")
        return None

def connect_to_google_sheet(sheet_id):
    """
    Connect to a Google Sheet and read its data
    
    Parameters:
    -----------
    sheet_id : str
        The ID of the Google Sheet to connect to
        
    Returns:
    --------
    pd.DataFrame
        DataFrame containing the imported data
    """
    try:
        import requests
        import io
        
        # URL format for Google Sheets export as CSV
        url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
        
        # Use requests to get the data with appropriate headers
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers)
        
        # Check if successful
        if response.status_code == 200:
            # Convert content to pandas DataFrame
            csv_data = io.StringIO(response.content.decode('utf-8'))
            return pd.read_csv(csv_data)
        else:
            st.error(f"Error accessing Google Sheet: HTTP Status {response.status_code}")
            st.info("Make sure the sheet is publicly accessible (at least to 'Anyone with the link') or provide a valid access token.")
            return None
    except Exception as e:
        st.error(f"Error connecting to Google Sheet: {str(e)}")
        st.info("Make sure your sheet ID is correct and that the sheet is publicly accessible.")
        return None

def detect_column_types(df):
    """
    Automatically detect the likely content of each column based on patterns
    
    Parameters:
    -----------
    df : pd.DataFrame
        The data to analyze
        
    Returns:
    --------
    dict
        Mapping of column names to likely type (fuel, energy, transport, etc.)
    """
    column_types = {}
    
    # Regular expressions for pattern matching
    patterns = {
        'fuel': re.compile(r'fuel|diesel|gasoline|petrol|liters?|gallons?', re.IGNORECASE),
        'electricity': re.compile(r'electricity|energy|kwh|mwh|power', re.IGNORECASE),
        'transport': re.compile(r'travel|transport|vehicle|flight|distance|km|miles', re.IGNORECASE),
        'waste': re.compile(r'waste|landfill|recycl|compost', re.IGNORECASE),
        'water': re.compile(r'water|m3|cubic|consumption', re.IGNORECASE),
        'refrigerant': re.compile(r'refrigerant|coolant|air condition|hfc|r-\d+', re.IGNORECASE),
        'amount': re.compile(r'amount|quantity|volume|weight', re.IGNORECASE),
        'unit': re.compile(r'unit|measure', re.IGNORECASE),
        'date': re.compile(r'date|time|period|month|year', re.IGNORECASE),
        'category': re.compile(r'category|type|class|scope', re.IGNORECASE)
    }
    
    # Check each column
    for column in df.columns:
        col_str = str(column).lower()
        matched = False
        
        # Check against patterns
        for category, pattern in patterns.items():
            if pattern.search(col_str):
                column_types[column] = category
                matched = True
                break
        
        # Also try to detect based on content
        if not matched and not df[column].empty:
            sample = str(df[column].iloc[0]).lower() if not pd.isna(df[column].iloc[0]) else ""
            
            # Check if column contains dates
            if df[column].dtype == 'datetime64[ns]' or 'date' in sample:
                column_types[column] = 'date'
            # Check if column contains numeric values (likely amounts)
            elif pd.api.types.is_numeric_dtype(df[column]):
                column_types[column] = 'amount'
            # Default to 'unknown'
            else:
                column_types[column] = 'unknown'
    
    return column_types

def map_to_emission_categories(df, column_mappings):
    """
    Map the imported data to emission categories based on user-confirmed mappings
    
    Parameters:
    -----------
    df : pd.DataFrame
        The data to map
    column_mappings : dict
        User-confirmed mappings from column names to emission categories
        
    Returns:
    --------
    dict
        Dictionary with data structured for the Carbon Aegis application
    """
    # Initialize the structured data
    structured_data = {
        'scope1': [],
        'scope2': [],
        'scope3': []
    }
    
    # Determine emission scope for each row
    for _, row in df.iterrows():
        emission_type = None
        scope = None
        
        # Extract information from the row based on column mappings
        row_data = {}
        
        # Map known columns based on confirmed mappings
        for column, mapping in column_mappings.items():
            if mapping['category'] != 'ignore' and column in df.columns:
                row_data[mapping['category']] = row[column]
        
        # Determine scope and emission type based on mappings
        if 'category' in row_data:
            category = str(row_data['category']).lower()
            
            # Fuel and refrigerant are Scope 1
            if 'fuel' in category or 'refrigerant' in category or 'diesel' in category or 'petrol' in category or 'gas' in category:
                scope = 'scope1'
                emission_type = 'fuel'
                if 'refrigerant' in category:
                    emission_type = 'refrigerant'
            
            # Electricity is Scope 2
            elif 'electricity' in category or 'energy' in category or 'power' in category:
                scope = 'scope2'
                emission_type = 'electricity'
            
            # Travel, waste, water are typically Scope 3
            elif 'travel' in category or 'flight' in category or 'transport' in category:
                scope = 'scope3'
                emission_type = 'transport'
            elif 'waste' in category:
                scope = 'scope3'
                emission_type = 'waste'
            elif 'water' in category:
                scope = 'scope3'
                emission_type = 'water'
        
        # If the scope is still not determined but we have a category mapping for the emission type
        if scope is None:
            for key, value in row_data.items():
                if key == 'fuel' or key == 'refrigerant':
                    scope = 'scope1'
                    emission_type = key
                    break
                elif key == 'electricity':
                    scope = 'scope2'
                    emission_type = key
                    break
                elif key in ['transport', 'waste', 'water']:
                    scope = 'scope3'
                    emission_type = key
                    break
        
        # If we've determined a scope and emission type, add to structured data
        if scope and emission_type:
            structured_data[scope].append({
                'type': emission_type,
                'data': row_data,
                'original_row': row.to_dict()
            })
    
    return structured_data

def generate_emission_factors_table():
    """
    Generate a table of common emission factors for different categories
    
    Returns:
    --------
    dict
        Dictionary of emission factors by category
    """
    return {
        'fuel': {
            'Petrol/Gasoline': 2.31,  # kg CO2e per liter
            'Diesel': 2.68,           # kg CO2e per liter
            'LPG/Propane': 1.51,      # kg CO2e per liter
            'Natural Gas': 2.02,      # kg CO2e per m3
            'Biodiesel': 1.79,        # kg CO2e per liter
            'E85 (Ethanol)': 1.56     # kg CO2e per liter
        },
        'electricity': {
            'Northeast': 0.35,        # kg CO2e per kWh
            'Southeast': 0.42,        # kg CO2e per kWh
            'Midwest': 0.53,          # kg CO2e per kWh
            'Southwest': 0.38,        # kg CO2e per kWh
            'West': 0.22,             # kg CO2e per kWh
            'Europe Average': 0.29,   # kg CO2e per kWh
            'Asia Average': 0.63,     # kg CO2e per kWh
            'Global Average': 0.48    # kg CO2e per kWh
        },
        'transport': {
            'Car (Petrol/Gasoline)': 0.19,  # kg CO2e per km
            'Car (Diesel)': 0.17,           # kg CO2e per km
            'Car (Hybrid)': 0.11,           # kg CO2e per km
            'Bus': 0.10,                    # kg CO2e per km
            'Train': 0.04,                  # kg CO2e per km
            'Flight (Short-haul)': 0.15,    # kg CO2e per km
            'Flight (Long-haul)': 0.11      # kg CO2e per km
        },
        'waste': {
            'Landfill (Mixed)': 0.45,       # kg CO2e per kg
            'Recycled': 0.02,               # kg CO2e per kg
            'Composted': 0.01               # kg CO2e per kg
        },
        'water': {
            'Municipal Supply': 0.34,       # kg CO2e per m3
            'Recycled Water': 0.05          # kg CO2e per m3
        },
        'refrigerant': {
            'R-410A': 2088,                 # GWP (Global Warming Potential)
            'R-22': 1810,                   # GWP
            'R-134a': 1430,                 # GWP
            'R-404A': 3922                  # GWP
        }
    }

def calculate_emissions_from_mapped_data(structured_data, emission_factors=None):
    """
    Calculate emissions based on mapped data
    
    Parameters:
    -----------
    structured_data : dict
        Structured data with scope and emission type information
    emission_factors : dict, optional
        Custom emission factors to use
        
    Returns:
    --------
    dict
        Dictionary with calculated emissions by scope and category
    """
    if emission_factors is None:
        emission_factors = generate_emission_factors_table()
    
    results = {
        'scope1': {'total': 0.0, 'categories': {}},
        'scope2': {'total': 0.0, 'categories': {}},
        'scope3': {'total': 0.0, 'categories': {}},
        'total': 0.0,
        'line_items': []
    }
    
    # Process each scope
    for scope, items in structured_data.items():
        for item in items:
            emission_type = item['type']
            data = item['data']
            
            # Calculate emissions based on emission type and data
            emissions = 0.0
            calculation_explanation = ""
            
            if emission_type == 'fuel' and 'amount' in data:
                fuel_type = data.get('fuel', 'Diesel')  # Default to Diesel if not specified
                amount = float(data.get('amount', 0))
                
                # Get the appropriate emission factor
                ef = emission_factors['fuel'].get(fuel_type, 2.68)  # Default to Diesel EF if not found
                
                # Calculate emissions
                emissions = amount * ef
                calculation_explanation = f"{amount} (amount) × {ef} (emission factor for {fuel_type}) = {emissions:.2f} kg CO2e"
            
            elif emission_type == 'electricity' and 'amount' in data:
                amount = float(data.get('amount', 0))
                region = data.get('region', 'Global Average')
                
                # Get the appropriate emission factor
                ef = emission_factors['electricity'].get(region, 0.48)  # Default to global average if not found
                
                # Calculate emissions
                emissions = amount * ef
                calculation_explanation = f"{amount} kWh × {ef} (emission factor for {region}) = {emissions:.2f} kg CO2e"
            
            elif emission_type == 'transport' and 'amount' in data:
                transport_type = data.get('transport', 'Car (Petrol/Gasoline)')
                amount = float(data.get('amount', 0))
                
                # Get the appropriate emission factor
                ef = emission_factors['transport'].get(transport_type, 0.19)  # Default to petrol car if not found
                
                # Calculate emissions
                emissions = amount * ef
                calculation_explanation = f"{amount} km × {ef} (emission factor for {transport_type}) = {emissions:.2f} kg CO2e"
            
            elif emission_type == 'waste' and 'amount' in data:
                waste_type = data.get('waste', 'Landfill (Mixed)')
                amount = float(data.get('amount', 0))
                
                # Get the appropriate emission factor
                ef = emission_factors['waste'].get(waste_type, 0.45)  # Default to landfill if not found
                
                # Calculate emissions
                emissions = amount * ef
                calculation_explanation = f"{amount} kg × {ef} (emission factor for {waste_type}) = {emissions:.2f} kg CO2e"
            
            elif emission_type == 'water' and 'amount' in data:
                water_type = data.get('water', 'Municipal Supply')
                amount = float(data.get('amount', 0))
                
                # Get the appropriate emission factor
                ef = emission_factors['water'].get(water_type, 0.34)  # Default to municipal if not found
                
                # Calculate emissions
                emissions = amount * ef
                calculation_explanation = f"{amount} m³ × {ef} (emission factor for {water_type}) = {emissions:.2f} kg CO2e"
            
            elif emission_type == 'refrigerant' and 'amount' in data:
                refrigerant_type = data.get('refrigerant', 'R-410A')
                amount = float(data.get('amount', 0))
                
                # Get the appropriate emission factor (GWP)
                ef = emission_factors['refrigerant'].get(refrigerant_type, 2088)  # Default to R-410A if not found
                
                # Calculate emissions (convert kg to tonnes and multiply by GWP)
                emissions = amount * ef / 1000
                calculation_explanation = f"{amount} kg × {ef} (GWP for {refrigerant_type}) ÷ 1000 = {emissions:.2f} tonnes CO2e"
            
            # Add emissions to the corresponding category
            if emission_type not in results[scope]['categories']:
                results[scope]['categories'][emission_type] = 0.0
            
            results[scope]['categories'][emission_type] += emissions
            results[scope]['total'] += emissions
            results['total'] += emissions
            
            # Add line item for detailed breakdown
            results['line_items'].append({
                'scope': scope,
                'type': emission_type,
                'data': data,
                'emissions': emissions,
                'calculation': calculation_explanation,
                'original_row': item.get('original_row', {})
            })
    
    return results

def convert_uploaded_data_to_app_format(structured_data, calculation_results):
    """
    Convert the structured data and calculation results to the format expected by the application
    
    Parameters:
    -----------
    structured_data : dict
        Structured data with scope and emission type information
    calculation_results : dict
        Results of emission calculations
        
    Returns:
    --------
    dict
        Dictionary in the format expected by the application for calculations
    """
    # Create a data structure matching what the application expects
    app_data = {
        'time_period': st.session_state.get('time_period', 'Annually'),
        'calculation_method': st.session_state.get('calculation_method', 'Exact (measured data)'),
        'distance_unit': st.session_state.get('distance_unit', 'Kilometers'),
        'volume_unit': st.session_state.get('volume_unit', 'Liters'),
        
        # Initialize with zeros
        'fuel_amount': 0.0,
        'vehicle_distance': 0.0,
        'flight_distance': 0.0,
        'electricity': 0.0,
        'heating_amount': 0.0,
        'waste_amount': 0.0,
        'water_amount': 0.0,
        'material_amount': 0.0,
        'refrigerant_amount': 0.0,
        
        # Add calculation results
        'emissions_data': {
            'scope1': calculation_results['scope1']['categories'],
            'scope2': calculation_results['scope2']['categories'],
            'scope3': calculation_results['scope3']['categories']
        },
        'scope1_total': calculation_results['scope1']['total'],
        'scope2_total': calculation_results['scope2']['total'],
        'scope3_total': calculation_results['scope3']['total'],
        'total_emissions': calculation_results['total'],
        
        # Add line items for detailed breakdown
        'imported_line_items': calculation_results['line_items']
    }
    
    # Add data from structured data
    for scope, items in structured_data.items():
        for item in items:
            emission_type = item['type']
            data = item['data']
            
            if emission_type == 'fuel' and 'amount' in data:
                app_data['fuel_amount'] += float(data.get('amount', 0))
                if 'fuel' in data:
                    app_data['fuel_type'] = data['fuel']
            
            elif emission_type == 'transport' and 'amount' in data:
                if 'transport' in data and 'flight' in str(data['transport']).lower():
                    app_data['flight_distance'] += float(data.get('amount', 0))
                    app_data['flight_type'] = 'Short-haul (<1,500 km)'
                else:
                    app_data['vehicle_distance'] += float(data.get('amount', 0))
                    if 'transport' in data:
                        app_data['vehicle_type'] = data['transport']
            
            elif emission_type == 'electricity' and 'amount' in data:
                app_data['electricity'] += float(data.get('amount', 0))
                app_data['electricity_unit'] = 'kWh'
                
            elif emission_type == 'waste' and 'amount' in data:
                app_data['waste_amount'] += float(data.get('amount', 0))
                if 'waste' in data:
                    app_data['waste_type'] = data['waste']
                
            elif emission_type == 'water' and 'amount' in data:
                app_data['water_amount'] += float(data.get('amount', 0))
                if 'water' in data:
                    app_data['water_type'] = data['water']
                    
            elif emission_type == 'refrigerant' and 'amount' in data:
                app_data['refrigerant_amount'] += float(data.get('amount', 0))
                if 'refrigerant' in data:
                    app_data['refrigerant_type'] = data['refrigerant']
    
    return app_data