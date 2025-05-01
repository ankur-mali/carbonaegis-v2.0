import streamlit as st
import pandas as pd
import numpy as np
import os
import io
import tempfile
import re
import json
from datetime import datetime

# Initialize session state for storing data
if 'has_data' not in st.session_state:
    st.session_state.has_data = False
if 'emissions_data' not in st.session_state:
    st.session_state.emissions_data = {}
if 'input_data' not in st.session_state:
    st.session_state.input_data = {}
if 'organization_name' not in st.session_state:
    st.session_state.organization_name = "My Organization"
if 'report_year' not in st.session_state:
    st.session_state.report_year = 2025

# Set up OpenAI client if available
openai_api_key = os.environ.get("OPENAI_API_KEY")
has_openai = openai_api_key is not None and openai_api_key != ""

if has_openai:
    try:
        from openai import OpenAI
        openai_client = OpenAI(api_key=openai_api_key)
    except ImportError:
        has_openai = False
        st.warning("OpenAI package not installed. AI-powered detection will be disabled.")
    except Exception as e:
        has_openai = False
        st.warning(f"Error initializing OpenAI client: {str(e)}")

# Default emission factors
EMISSION_FACTORS = {
    'fuel': {
        'Petrol/Gasoline': 2.31,  # kg CO2e per liter
        'Diesel': 2.68,           # kg CO2e per liter
        'LPG/Propane': 1.51,      # kg CO2e per liter
        'Natural Gas': 2.02,      # kg CO2e per m3
        'Biodiesel': 1.79,        # kg CO2e per liter
        'E85 (Ethanol)': 1.56     # kg CO2e per liter
    },
    'electricity': {
        'UK': 0.19,              # kg CO2e per kWh (UK, 2024)
        'EU Average': 0.23,      # kg CO2e per kWh
        'US Average': 0.38,      # kg CO2e per kWh
        'China': 0.55,           # kg CO2e per kWh
        'India': 0.71,           # kg CO2e per kWh
        'Global Average': 0.48,  # kg CO2e per kWh
        'Northeast': 0.35,       # kg CO2e per kWh
        'Northwest': 0.32,       # kg CO2e per kWh
        'Southeast': 0.42,       # kg CO2e per kWh
        'Southwest': 0.40,       # kg CO2e per kWh
        'Midwest': 0.45          # kg CO2e per kWh
    },
    'transport': {
        'Car (Petrol/Gasoline)': 0.19,  # kg CO2e per km
        'Car (Diesel)': 0.17,           # kg CO2e per km
        'Car (Hybrid)': 0.11,           # kg CO2e per km
        'Car (Electric)': 0.05,         # kg CO2e per km
        'Bus': 0.10,                    # kg CO2e per km
        'Train': 0.04,                  # kg CO2e per km
        'Flight (Short-haul)': 0.16,    # kg CO2e per km
        'Flight (Medium-haul)': 0.14,   # kg CO2e per km
        'Flight (Long-haul)': 0.15      # kg CO2e per km
    },
    'waste': {
        'Landfill (Mixed)': 0.45,      # kg CO2e per kg
        'Recycled Paper': 0.02,        # kg CO2e per kg
        'Recycled Plastic': 0.04,      # kg CO2e per kg
        'Recycled Glass': 0.01,        # kg CO2e per kg
        'Recycled Metal': 0.02,        # kg CO2e per kg
        'Composted': 0.01,             # kg CO2e per kg
        'Incineration': 0.22           # kg CO2e per kg
    },
    'water': {
        'Supply': 0.34,                # kg CO2e per m3
        'Treatment': 0.71,             # kg CO2e per m3
        'Recycled': 0.05               # kg CO2e per m3
    },
    'refrigerant': {
        'R-410A': 2088,                # GWP (Global Warming Potential)
        'R-22': 1810,                  # GWP
        'R-134a': 1430,                # GWP
        'R-404A': 3922,                # GWP
        'R-407C': 1774,                # GWP
        'R-32': 675                    # GWP
    }
}

# Define utility functions
def analyze_column_with_ai(column_name, sample_values=None):
    """Use OpenAI to analyze a column name and sample values to determine the emission category"""
    if not has_openai:
        return None
    
    try:
        # Create a prompt for analysis
        prompt = f"Analyze this column from an emissions data spreadsheet and classify it into one of these categories: 'fuel', 'electricity', 'transport', 'waste', 'water', 'refrigerant', 'amount', 'unit', 'date', 'category', 'notes', 'location'.\n\nColumn name: '{column_name}'"
        
        if sample_values and len(sample_values) > 0:
            sample_str = ", ".join([str(v) for v in sample_values if v is not None and pd.notna(v)])
            if sample_str:
                prompt += f"\nSample values: {sample_str}"
        
        prompt += "\n\nRespond in JSON format with these fields: 'category' (one of the categories listed above), 'scope' (1, 2, or 3, or null if not applicable), 'unit' (the measurement unit if detectable, or null), 'confidence' (0-1 score of confidence in the classification)."
        
        # Call the OpenAI API
        response = openai_client.chat.completions.create(
            model="gpt-4o",  # Use the newest model
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        
        # Parse the response
        result = response.choices[0].message.content
        return result
    except Exception as e:
        st.warning(f"AI analysis error: {str(e)}")
        return None

def read_excel_file(uploaded_file):
    """Read and process an uploaded Excel file"""
    try:
        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_path = tmp_file.name
        
        # Try to read the file
        try:
            df = pd.read_excel(tmp_path)
        except Exception:
            try:
                df = pd.read_excel(tmp_path, sheet_name=0)
            except Exception:
                try:
                    dfs = pd.read_excel(tmp_path, sheet_name=None)
                    if len(dfs) > 0:
                        for sheet_name, sheet_df in dfs.items():
                            if not sheet_df.empty:
                                df = sheet_df
                                break
                    else:
                        raise ValueError("No data found in Excel file")
                except Exception as e:
                    st.error(f"Could not read Excel file: {str(e)}")
                    os.unlink(tmp_path)
                    return None
        
        # Clean up
        os.unlink(tmp_path)
        
        # Clean column names
        df.columns = [str(col).strip() for col in df.columns]
        
        # Replace NaN with None
        df = df.replace({np.nan: None})
        
        return df
    except Exception as e:
        st.error(f"Error reading Excel file: {str(e)}")
        return None

def detect_column_types(df, use_ai=False):
    """Detect the types of columns in the DataFrame"""
    column_types = {}
    
    # Regular expressions for pattern matching
    patterns = {
        'fuel': re.compile(r'(?i)fuel|diesel|gasoline|petrol|gas|oil|litre|liter|gallon|combustion|fleet|vehicle fuel|natural gas|lpg|propane|biodiesel'),
        'electricity': re.compile(r'(?i)electric|energy|kwh|mwh|power|consumption|generation|grid|renewable|solar|wind|hydroelectric'),
        'transport': re.compile(r'(?i)travel|transport|vehicle|flight|distance|km|mile|commute|business travel|train|bus|taxi|airplane|ship|ferry|logistics'),
        'waste': re.compile(r'(?i)waste|landfill|recycl|compost|garbage|trash|disposal|incineration|hazardous|scrap|sewage'),
        'water': re.compile(r'(?i)water|m3|cubic|consumption|treatment|wastewater|effluent|discharge|irrigation|potable'),
        'refrigerant': re.compile(r'(?i)refrigerant|coolant|air condition|hfc|r-\d+|leak|fugitive|cooling|hvac|chiller'),
        'amount': re.compile(r'(?i)amount|quantity|volume|weight|total|consumption|usage|value|count|number|sum'),
        'unit': re.compile(r'(?i)unit|measure|uom|metric|kwh|kg|ton|liter|gallon|km|mile|m3'),
        'date': re.compile(r'(?i)date|time|period|month|year|quarter|week|day|fiscal|calendar|report'),
        'category': re.compile(r'(?i)category|type|class|scope|classification|group|source|activity'),
        'location': re.compile(r'(?i)location|site|facility|building|office|plant|region|country|city|address|geography'),
        'notes': re.compile(r'(?i)note|comment|description|detail|additional|info|remark')
    }
    
    # Check column names against patterns
    for column in df.columns:
        col_str = str(column).lower()
        matched = False
        
        # Check against patterns
        for category, pattern in patterns.items():
            if pattern.search(col_str):
                column_types[column] = {
                    'category': category,
                    'confidence': 0.8,
                    'scope': get_scope_for_category(category),
                    'unit': detect_unit(df[column]) if category in ['amount', 'unit'] else None
                }
                matched = True
                break
        
        # If no match found by name, try to infer from content
        if not matched:
            matched = infer_from_content(df, column, column_types)
        
        # If still no match and AI is enabled, use OpenAI
        if not matched and use_ai and has_openai:
            # Get sample values
            sample_values = df[column].dropna().head(3).tolist()
            
            try:
                ai_result = analyze_column_with_ai(column, sample_values)
                if ai_result:
                    ai_analysis = json.loads(ai_result)
                    column_types[column] = {
                        'category': ai_analysis.get('category', 'unknown'),
                        'confidence': ai_analysis.get('confidence', 0.5),
                        'scope': ai_analysis.get('scope'),
                        'unit': ai_analysis.get('unit')
                    }
                    matched = True
            except Exception as e:
                st.warning(f"AI analysis failed for column '{column}': {str(e)}")
        
        # If still no match, mark as unknown
        if not matched:
            column_types[column] = {
                'category': 'unknown',
                'confidence': 0.1,
                'scope': None,
                'unit': None
            }
    
    return column_types

def get_scope_for_category(category):
    """Get the emissions scope for a category"""
    scope_mapping = {
        'fuel': 1,
        'refrigerant': 1,
        'electricity': 2,
        'transport': 3,
        'waste': 3,
        'water': 3
    }
    
    return scope_mapping.get(category)

def detect_unit(column):
    """Detect the unit from a column of values"""
    # Skip if column is empty
    if column.empty or column.isna().all():
        return None
    
    # Check if all values are numbers
    if pd.api.types.is_numeric_dtype(column):
        # Try to infer from column name
        col_str = str(column.name).lower()
        
        # Common units
        if any(unit in col_str for unit in ['kwh', 'kw-h', 'kilowatt']):
            return 'kWh'
        elif any(unit in col_str for unit in ['mwh', 'mw-h', 'megawatt']):
            return 'MWh'
        elif any(unit in col_str for unit in ['kg', 'kilo', 'weight']):
            return 'kg'
        elif any(unit in col_str for unit in ['ton', 'tonne']):
            return 'tonnes'
        elif any(unit in col_str for unit in ['l', 'liter', 'litre']):
            return 'litres'
        elif any(unit in col_str for unit in ['gal', 'gallon']):
            return 'gallons'
        elif any(unit in col_str for unit in ['km', 'kilometer']):
            return 'km'
        elif any(unit in col_str for unit in ['mi', 'mile']):
            return 'miles'
        elif any(unit in col_str for unit in ['m3', 'cubic']):
            return 'm³'
    
    # If string column, check for units in values
    elif pd.api.types.is_string_dtype(column):
        # Sample values
        sample_values = column.dropna().astype(str).str.lower().head(5).tolist()
        
        # Check for units in the values
        units = {
            'kwh': 'kWh',
            'kilowatt': 'kWh',
            'mwh': 'MWh',
            'megawatt': 'MWh',
            'kg': 'kg',
            'kilo': 'kg',
            'ton': 'tonnes',
            'tonne': 'tonnes',
            'liter': 'litres',
            'litre': 'litres',
            'gallon': 'gallons',
            'km': 'km',
            'kilometer': 'km',
            'mile': 'miles',
            'm3': 'm³',
            'cubic meter': 'm³'
        }
        
        for value in sample_values:
            for unit_str, unit_value in units.items():
                if unit_str in value:
                    return unit_value
    
    return None

def infer_from_content(df, column, column_types):
    """Infer column type from content"""
    # Skip if column is empty
    if df[column].empty or df[column].isna().all():
        return False
    
    # Check if column contains dates
    if pd.api.types.is_datetime64_any_dtype(df[column]):
        column_types[column] = {
            'category': 'date',
            'confidence': 0.9,
            'scope': None,
            'unit': None
        }
        return True
    
    # Check for numeric columns - likely amounts
    if pd.api.types.is_numeric_dtype(df[column]):
        # Get range and check if values are small (0-100) - might be percentages
        try:
            min_val = df[column].min()
            max_val = df[column].max()
            
            # Check for percentages
            if 0 <= min_val <= 100 and 0 <= max_val <= 100:
                column_types[column] = {
                    'category': 'amount',
                    'confidence': 0.6,
                    'scope': None,
                    'unit': '%'
                }
                return True
            
            # Otherwise just a general amount
            column_types[column] = {
                'category': 'amount',
                'confidence': 0.7,
                'scope': None,
                'unit': detect_unit(df[column])
            }
            return True
        except:
            pass
    
    # Check for common keywords in values
    if pd.api.types.is_string_dtype(df[column]):
        sample_values = df[column].dropna().astype(str).str.lower().tolist()
        
        # Check for scope indicators
        if any('scope 1' in str(v).lower() for v in sample_values):
            column_types[column] = {
                'category': 'category',
                'confidence': 0.8,
                'scope': 1,
                'unit': None
            }
            return True
        elif any('scope 2' in str(v).lower() for v in sample_values):
            column_types[column] = {
                'category': 'category',
                'confidence': 0.8,
                'scope': 2,
                'unit': None
            }
            return True
        elif any('scope 3' in str(v).lower() for v in sample_values):
            column_types[column] = {
                'category': 'category',
                'confidence': 0.8,
                'scope': 3,
                'unit': None
            }
            return True
        
        # Check for common units
        units = ['kwh', 'mwh', 'kg', 'ton', 'tonnes', 'liter', 'litre', 'gallon', 'km', 'mile', 'm3']
        for unit in units:
            if any(unit in str(v).lower() for v in sample_values):
                column_types[column] = {
                    'category': 'unit',
                    'confidence': 0.7,
                    'scope': None,
                    'unit': unit
                }
                return True
        
        # Check for fuel types
        fuel_types = ['diesel', 'gasoline', 'petrol', 'natural gas', 'lpg', 'propane']
        if any(any(fuel in str(v).lower() for fuel in fuel_types) for v in sample_values):
            column_types[column] = {
                'category': 'fuel',
                'confidence': 0.8,
                'scope': 1,
                'unit': None
            }
            return True
    
    return False

def map_to_emission_categories(df, column_mappings, use_ai=False):
    """Map DataFrame to emission categories"""
    # Initialize the structured data
    structured_data = {
        'scope1': [],
        'scope2': [],
        'scope3': []
    }
    
    # Get amount and unit columns
    amount_columns = [col for col, mapping in column_mappings.items() 
                      if mapping['category'] == 'amount' and col in df.columns]
    unit_columns = [col for col, mapping in column_mappings.items() 
                    if mapping['category'] == 'unit' and col in df.columns]
    category_columns = [col for col, mapping in column_mappings.items() 
                        if mapping['category'] == 'category' and col in df.columns]
    
    # Process each row
    for _, row in df.iterrows():
        emission_type = None
        scope = None
        amount = None
        unit = None
        category_value = None
        
        # Extract category if available
        if category_columns:
            for col in category_columns:
                if pd.notna(row[col]):
                    category_value = str(row[col]).lower()
                    break
        
        # Extract amount
        if amount_columns:
            for col in amount_columns:
                if pd.notna(row[col]):
                    try:
                        amount = float(row[col])
                        break
                    except:
                        pass
        
        # Extract unit
        if unit_columns:
            for col in unit_columns:
                if pd.notna(row[col]):
                    unit = str(row[col])
                    break
        
        # Determine emission type and scope from available columns
        for col, mapping in column_mappings.items():
            if col in df.columns and mapping['category'] not in ['amount', 'unit', 'date', 'notes', 'unknown']:
                value = row[col]
                if pd.notna(value):
                    if mapping['category'] in ['fuel', 'refrigerant', 'electricity', 'transport', 'waste', 'water']:
                        emission_type = mapping['category']
                        scope = mapping['scope']
                        
                        # If we found a primary category, break
                        if emission_type and scope:
                            break
        
        # If still no emission type but we have a category value, try to determine from that
        if not emission_type and category_value:
            if any(keyword in category_value for keyword in ['fuel', 'diesel', 'gasoline', 'petrol']):
                emission_type = 'fuel'
                scope = 1
            elif any(keyword in category_value for keyword in ['refrigerant', 'coolant', 'r-']):
                emission_type = 'refrigerant'
                scope = 1
            elif any(keyword in category_value for keyword in ['electric', 'power', 'energy']):
                emission_type = 'electricity'
                scope = 2
            elif any(keyword in category_value for keyword in ['transport', 'travel', 'vehicle', 'flight']):
                emission_type = 'transport'
                scope = 3
            elif any(keyword in category_value for keyword in ['waste', 'landfill', 'recycl']):
                emission_type = 'waste'
                scope = 3
            elif any(keyword in category_value for keyword in ['water']):
                emission_type = 'water'
                scope = 3
        
        # If we have a scope explicitly mentioned in a column, use that
        for col, mapping in column_mappings.items():
            if col in df.columns and mapping['scope'] is not None:
                value = row[col]
                if pd.notna(value):
                    # This might override the previously determined scope
                    scope = mapping['scope']
                    break
        
        # If we can determine a scope from the category value, use that
        if category_value and not scope:
            if 'scope 1' in category_value:
                scope = 1
            elif 'scope 2' in category_value:
                scope = 2
            elif 'scope 3' in category_value:
                scope = 3
        
        # If we have amount, unit, emission type, and scope, add to structured data
        if amount is not None and emission_type and scope:
            # Determine which scope list to add to
            scope_key = f'scope{scope}'
            
            # Create a data dictionary for this row
            data = {
                'amount': amount,
                'unit': unit,
                'category': category_value,
                emission_type: True  # Mark that this is this type of emission
            }
            
            # Collect all other relevant data from the row
            for col, mapping in column_mappings.items():
                if col in df.columns and mapping['category'] not in ['unknown', 'ignore']:
                    value = row[col]
                    if pd.notna(value):
                        data[mapping['category']] = value
            
            # Add to the appropriate scope
            structured_data[scope_key].append({
                'type': emission_type,
                'data': data,
                'original_row': row.to_dict()
            })
    
    return structured_data

def calculate_emissions(structured_data, emission_factors=None):
    """Calculate emissions based on structured data"""
    if emission_factors is None:
        emission_factors = EMISSION_FACTORS
    
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
                # Determine fuel type if available
                fuel_type = None
                for key, value in data.items():
                    if isinstance(value, str) and any(keyword in value.lower() for keyword in ['diesel', 'gasoline', 'petrol', 'natural gas', 'lpg']):
                        fuel_type = value
                        break
                
                # Default to Diesel if not specified
                if not fuel_type:
                    fuel_type = 'Diesel'
                
                amount = float(data.get('amount', 0))
                
                # Get the appropriate emission factor
                # Find the closest matching fuel type in the emission factors
                ef = None
                for factor_name, factor_value in emission_factors['fuel'].items():
                    if fuel_type.lower() in factor_name.lower():
                        ef = factor_value
                        break
                
                # If no match, use default Diesel
                if ef is None:
                    ef = emission_factors['fuel'].get('Diesel', 2.68)
                
                # Calculate emissions
                emissions = amount * ef
                calculation_explanation = f"{amount} (amount) × {ef} (emission factor for {fuel_type}) = {emissions:.2f} kg CO2e"
            
            elif emission_type == 'electricity' and 'amount' in data:
                amount = float(data.get('amount', 0))
                
                # Determine region if available
                region = None
                for key, value in data.items():
                    if isinstance(value, str) and any(keyword in value.lower() for keyword in ['uk', 'us', 'eu', 'china', 'india', 'northeast', 'northwest', 'southeast', 'southwest', 'midwest']):
                        region = value
                        break
                
                # Default to Global Average if not specified
                if not region:
                    region = 'Global Average'
                
                # Get the appropriate emission factor
                # Find the closest matching region in the emission factors
                ef = None
                for factor_name, factor_value in emission_factors['electricity'].items():
                    if region.lower() in factor_name.lower():
                        ef = factor_value
                        break
                
                # If no match, use Global Average
                if ef is None:
                    ef = emission_factors['electricity'].get('Global Average', 0.48)
                
                # Calculate emissions
                emissions = amount * ef
                calculation_explanation = f"{amount} kWh × {ef} (emission factor for {region}) = {emissions:.2f} kg CO2e"
            
            elif emission_type == 'transport' and 'amount' in data:
                # Determine transport type if available
                transport_type = None
                for key, value in data.items():
                    if isinstance(value, str) and any(keyword in value.lower() for keyword in ['car', 'bus', 'train', 'flight', 'plane']):
                        transport_type = value
                        break
                
                # Default to Car (Petrol/Gasoline) if not specified
                if not transport_type:
                    transport_type = 'Car (Petrol/Gasoline)'
                
                amount = float(data.get('amount', 0))
                
                # Get the appropriate emission factor
                # Find the closest matching transport type in the emission factors
                ef = None
                for factor_name, factor_value in emission_factors['transport'].items():
                    if transport_type.lower() in factor_name.lower():
                        ef = factor_value
                        break
                
                # If no match, use Car (Petrol/Gasoline)
                if ef is None:
                    ef = emission_factors['transport'].get('Car (Petrol/Gasoline)', 0.19)
                
                # Calculate emissions
                emissions = amount * ef
                calculation_explanation = f"{amount} km × {ef} (emission factor for {transport_type}) = {emissions:.2f} kg CO2e"
            
            elif emission_type == 'waste' and 'amount' in data:
                # Determine waste type if available
                waste_type = None
                for key, value in data.items():
                    if isinstance(value, str) and any(keyword in value.lower() for keyword in ['landfill', 'recycled', 'composted', 'incineration']):
                        waste_type = value
                        break
                
                # Default to Landfill (Mixed) if not specified
                if not waste_type:
                    waste_type = 'Landfill (Mixed)'
                
                amount = float(data.get('amount', 0))
                
                # Get the appropriate emission factor
                # Find the closest matching waste type in the emission factors
                ef = None
                for factor_name, factor_value in emission_factors['waste'].items():
                    if waste_type.lower() in factor_name.lower():
                        ef = factor_value
                        break
                
                # If no match, use Landfill (Mixed)
                if ef is None:
                    ef = emission_factors['waste'].get('Landfill (Mixed)', 0.45)
                
                # Calculate emissions
                emissions = amount * ef
                calculation_explanation = f"{amount} kg × {ef} (emission factor for {waste_type}) = {emissions:.2f} kg CO2e"
            
            elif emission_type == 'water' and 'amount' in data:
                # Determine water type if available
                water_type = None
                for key, value in data.items():
                    if isinstance(value, str) and any(keyword in value.lower() for keyword in ['supply', 'treatment', 'recycled']):
                        water_type = value
                        break
                
                # Default to Supply if not specified
                if not water_type:
                    water_type = 'Supply'
                
                amount = float(data.get('amount', 0))
                
                # Get the appropriate emission factor
                # Find the closest matching water type in the emission factors
                ef = None
                for factor_name, factor_value in emission_factors['water'].items():
                    if water_type.lower() in factor_name.lower():
                        ef = factor_value
                        break
                
                # If no match, use Supply
                if ef is None:
                    ef = emission_factors['water'].get('Supply', 0.34)
                
                # Calculate emissions
                emissions = amount * ef
                calculation_explanation = f"{amount} m³ × {ef} (emission factor for {water_type}) = {emissions:.2f} kg CO2e"
            
            elif emission_type == 'refrigerant' and 'amount' in data:
                # Determine refrigerant type if available
                refrigerant_type = None
                for key, value in data.items():
                    if isinstance(value, str) and any(keyword in value.lower() for keyword in ['r-', 'hfc', 'refrigerant']):
                        refrigerant_type = value
                        break
                
                # Default to R-410A if not specified
                if not refrigerant_type:
                    refrigerant_type = 'R-410A'
                
                amount = float(data.get('amount', 0))
                
                # Get the appropriate emission factor (GWP)
                # Find the closest matching refrigerant type in the emission factors
                ef = None
                for factor_name, factor_value in emission_factors['refrigerant'].items():
                    if refrigerant_type.lower() in factor_name.lower():
                        ef = factor_value
                        break
                
                # If no match, use R-410A
                if ef is None:
                    ef = emission_factors['refrigerant'].get('R-410A', 2088)
                
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

def convert_to_app_format(structured_data, calculation_results):
    """Convert structured data and calculation results to app format"""
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
                transport_str = str(data.get('category', '')).lower()
                if 'flight' in transport_str or 'plane' in transport_str or 'air' in transport_str:
                    app_data['flight_distance'] += float(data.get('amount', 0))
                    
                    # Try to determine flight type
                    if 'short' in transport_str:
                        app_data['flight_type'] = 'Short-haul (<1,500 km)'
                    elif 'medium' in transport_str:
                        app_data['flight_type'] = 'Medium-haul (1,500-3,700 km)'
                    elif 'long' in transport_str:
                        app_data['flight_type'] = 'Long-haul (>3,700 km)'
                    else:
                        app_data['flight_type'] = 'Short-haul (<1,500 km)'
                else:
                    app_data['vehicle_distance'] += float(data.get('amount', 0))
                    
                    # Try to determine vehicle type
                    if 'category' in data:
                        vehicle_str = str(data.get('category', '')).lower()
                        if 'car' in vehicle_str and 'petrol' in vehicle_str:
                            app_data['vehicle_type'] = 'Car (Petrol/Gasoline)'
                        elif 'car' in vehicle_str and 'diesel' in vehicle_str:
                            app_data['vehicle_type'] = 'Car (Diesel)'
                        elif 'car' in vehicle_str and 'hybrid' in vehicle_str:
                            app_data['vehicle_type'] = 'Car (Hybrid)'
                        elif 'car' in vehicle_str and 'electric' in vehicle_str:
                            app_data['vehicle_type'] = 'Car (Electric)'
                        elif 'bus' in vehicle_str:
                            app_data['vehicle_type'] = 'Bus'
                        elif 'train' in vehicle_str:
                            app_data['transport_type'] = 'Train (Intercity)'
                        else:
                            app_data['vehicle_type'] = 'Car (Petrol/Gasoline)'
            
            elif emission_type == 'electricity' and 'amount' in data:
                app_data['electricity'] += float(data.get('amount', 0))
                app_data['electricity_unit'] = 'kWh'
                
            elif emission_type == 'waste' and 'amount' in data:
                app_data['waste_amount'] += float(data.get('amount', 0))
                if 'category' in data:
                    waste_str = str(data.get('category', '')).lower()
                    if 'landfill' in waste_str:
                        app_data['waste_type'] = 'Landfill (Mixed)'
                    elif 'recycled' in waste_str and 'paper' in waste_str:
                        app_data['waste_type'] = 'Recycled Paper'
                    elif 'recycled' in waste_str and 'plastic' in waste_str:
                        app_data['waste_type'] = 'Recycled Plastic'
                    elif 'recycled' in waste_str and 'glass' in waste_str:
                        app_data['waste_type'] = 'Recycled Glass'
                    elif 'recycled' in waste_str and 'metal' in waste_str:
                        app_data['waste_type'] = 'Recycled Metal'
                    elif 'compost' in waste_str or 'organic' in waste_str:
                        app_data['waste_type'] = 'Organic/Compost'
                    elif 'electronic' in waste_str:
                        app_data['waste_type'] = 'Electronic Waste'
                    else:
                        app_data['waste_type'] = 'Landfill (Mixed)'
                
            elif emission_type == 'water' and 'amount' in data:
                app_data['water_amount'] += float(data.get('amount', 0))
                if 'category' in data:
                    water_str = str(data.get('category', '')).lower()
                    if 'municipal' in water_str:
                        app_data['water_type'] = 'Municipal Supply'
                    elif 'well' in water_str:
                        app_data['water_type'] = 'Well Water'
                    elif 'rain' in water_str:
                        app_data['water_type'] = 'Harvested Rainwater'
                    elif 'recycled' in water_str:
                        app_data['water_type'] = 'Recycled Water'
                    else:
                        app_data['water_type'] = 'Municipal Supply'
                    
            elif emission_type == 'refrigerant' and 'amount' in data:
                app_data['refrigerant_amount'] += float(data.get('amount', 0))
                if 'category' in data:
                    ref_str = str(data.get('category', '')).lower()
                    if 'r-410a' in ref_str:
                        app_data['refrigerant_type'] = 'R-410A'
                    elif 'r-22' in ref_str:
                        app_data['refrigerant_type'] = 'R-22'
                    elif 'r-134a' in ref_str:
                        app_data['refrigerant_type'] = 'R-134a'
                    elif 'r-404a' in ref_str:
                        app_data['refrigerant_type'] = 'R-404A'
                    elif 'r-407c' in ref_str:
                        app_data['refrigerant_type'] = 'R-407C'
                    elif 'r-32' in ref_str:
                        app_data['refrigerant_type'] = 'R-32'
                    else:
                        app_data['refrigerant_type'] = 'R-410A'
    
    return app_data

def save_to_session_state(data):
    """Save data to session state for persistence"""
    st.session_state.has_data = True
    st.session_state.input_data = data
    
    # Generate an ID if we need to identify the record (even though we're not using a DB)
    import random
    import time
    record_id = int(time.time() * 1000) + random.randint(1, 1000)
    st.session_state.current_record_id = record_id
    
    return record_id

def clear_data():
    """Clear all data from session state"""
    # Clear individual data points
    data_keys = ['fuel_amount', 'vehicle_distance', 'flight_distance', 'electricity',
                'heating_amount', 'waste_amount', 'water_amount', 'material_amount',
                'refrigerant_amount', 'emissions_data', 'input_data']
    
    for key in data_keys:
        if key in st.session_state:
            del st.session_state[key]
    
    # Clear calculation results
    calc_keys = ['scope1_total', 'scope2_total', 'scope3_total', 'total_emissions']
    for key in calc_keys:
        if key in st.session_state:
            del st.session_state[key]
    
    # Clear all imported data
    if 'smart_imported_data' in st.session_state:
        del st.session_state.smart_imported_data
    if 'smart_column_mappings' in st.session_state:
        del st.session_state.smart_column_mappings
    if 'smart_structured_data' in st.session_state:
        del st.session_state.smart_structured_data
    if 'smart_calculation_results' in st.session_state:
        del st.session_state.smart_calculation_results
    
    # Reset flags
    st.session_state.has_data = False
    st.session_state.smart_import_step = 1

# CSS for better formatting
def add_custom_css():
    st.markdown("""
    <style>
    .category-header {
        background-color: #eef6f0;
        padding: 10px;
        border-radius: 5px;
        border-left: 5px solid #2E8B57;
        margin-bottom: 10px;
    }
    .action-container {
        background-color: #f0f8f4;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #2E8B57;
    }
    .nav-container {
        background-color: #f0f8f4;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #2E8B57;
        margin-bottom: 20px;
    }
    .help-container {
        background-color: #f5f7fa;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #3498db;
    }
    .step-box {
        border: 1px solid #ddd;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 15px;
    }
    .step-box.active {
        border-color: #2E8B57;
        box-shadow: 0 0 10px rgba(46, 139, 87, 0.2);
    }
    .result-box {
        background-color: #f9f9f9;
        border: 1px solid #ddd;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 15px;
    }
    .download-button {
        background-color: #2E8B57;
        color: white;
        padding: 10px 20px;
        text-align: center;
        text-decoration: none;
        display: inline-block;
        font-size: 16px;
        margin: 4px 2px;
        cursor: pointer;
        border-radius: 5px;
        border: none;
    }
    </style>
    """, unsafe_allow_html=True)

# MAIN APP
def main():
    add_custom_css()
    
    # Add page title and branding
    col1, col2 = st.columns([1, 5])
    with col1:
        # logo_path = "assets/logo.png"
        # if os.path.exists(logo_path):
        #     st.image(logo_path, width=100)
        # else:
        st.markdown("🌿")
    with col2:
        st.title("Carbon Aegis - Data Input")
    
    # Create tabs for different input methods
    tabs = st.tabs(["Manual Input", "Smart Data Import", "Settings"])
    
    # MANUAL INPUT TAB
    with tabs[0]:
        st.header("Manual Data Entry")
        st.markdown("""
        Enter your activity data categorized by emission scope. All calculations follow the GHG Protocol Corporate Standard.
        
        * **Scope 1**: Direct emissions from owned or controlled sources
        * **Scope 2**: Indirect emissions from purchased electricity, steam, heating, and cooling
        * **Scope 3**: All other indirect emissions in a company's value chain
        """)
        
        # Create tabs for different scopes
        scope_tabs = st.tabs(["Scope 1: Direct", "Scope 2: Energy Indirect", "Scope 3: Other Indirect"])
        
        # SCOPE 1 - Direct emissions
        with scope_tabs[0]:
            st.header("Scope 1: Direct Emissions")
            st.markdown("""
            Direct GHG emissions from sources owned or controlled by your organization.
            """)
            
            # Fuel Consumption 
            st.subheader("Fuel Consumption")
            with st.expander("Vehicle Fuel Usage", expanded=True):
                st.markdown("Enter details about your vehicle fuel consumption:")
                
                # First row - Fuel Type and Amount
                col1, col2, col3 = st.columns(3)
                with col1:
                    fuel_type = st.selectbox(
                        "Fuel Type", 
                        ["Petrol/Gasoline", "Diesel", "LPG/Propane", "Biodiesel", "E85 (Ethanol)", "CNG", "Other"],
                        key="fuel_type_select"
                    )
                
                with col2:
                    fuel_unit = st.selectbox(
                        "Unit", 
                        ["Liters", "Gallons", "kg"],
                        key="fuel_unit_select"
                    )
                
                with col3:
                    fuel_amount = st.number_input(
                        f"Amount ({fuel_unit})", 
                        min_value=0.0, 
                        value=st.session_state.get('fuel_amount', 0.0),
                        help=f"Enter the amount of {fuel_type} consumed"
                    )
            
            # Vehicle Types
            st.subheader("Vehicle Transportation")
            with st.expander("Vehicle Travel", expanded=True):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    vehicle_type = st.selectbox(
                        "Vehicle Type", 
                        ["Car (Petrol/Gasoline)", "Car (Diesel)", "Car (Hybrid)", "Car (Electric)", 
                         "Motorcycle", "Bus", "Truck (Light)", "Truck (Heavy)", "Other"],
                        key="vehicle_type_select"
                    )
                
                with col2:
                    distance_unit_vehicle = st.selectbox(
                        "Distance Unit", 
                        ["Kilometers", "Miles"],
                        key="distance_unit_vehicle_select"
                    )
                
                with col3:
                    vehicle_distance = st.number_input(
                        f"Distance ({distance_unit_vehicle})", 
                        min_value=0.0, 
                        value=st.session_state.get('vehicle_distance', 0.0),
                        help=f"Enter the distance traveled by {vehicle_type}"
                    )
            
            # Refrigerants
            st.subheader("Refrigerants")
            with st.expander("Refrigerant Leakage", expanded=True):
                col1, col2 = st.columns(2)
                
                with col1:
                    refrigerant_type = st.selectbox(
                        "Refrigerant Type", 
                        ["R-410A", "R-22", "R-134a", "R-404A", "R-407C", "R-32", "Other"],
                        key="refrigerant_type_select"
                    )
                
                with col2:
                    refrigerant_amount = st.number_input(
                        "Amount (kg)", 
                        min_value=0.0, 
                        value=st.session_state.get('refrigerant_amount', 0.0),
                        help=f"Enter the amount of {refrigerant_type} leaked"
                    )
        
        # SCOPE 2 - Energy Indirect Emissions
        with scope_tabs[1]:
            st.header("Scope 2: Energy Indirect Emissions")
            st.markdown("""
            Indirect GHG emissions from purchased electricity, steam, heating and cooling consumed by your organization.
            """)
            
            # Electricity
            st.subheader("Electricity Consumption")
            with st.expander("Electricity", expanded=True):
                col1, col2, col3 = st.columns(3)
                with col1:
                    electricity = st.number_input(
                        "Electricity Consumption", 
                        min_value=0.0, 
                        value=st.session_state.get('electricity', 0.0),
                        help="Enter the total electricity consumption"
                    )
                
                with col2:
                    electricity_unit = st.selectbox(
                        "Unit", 
                        ["kWh", "MWh"],
                        key="electricity_unit_select"
                    )
                
                with col3:
                    grid_regions = ["UK", "EU Average", "US Average", "China", "India", "Global Average", 
                                   "Northeast", "Northwest", "Southeast", "Southwest", "Midwest"]
                    grid_region = st.selectbox(
                        "Electricity Grid Region", 
                        grid_regions,
                        key="grid_region_select"
                    )
                
                # Renewable energy percentage
                col1, col2 = st.columns(2)
                with col1:
                    renewable_percentage = st.slider(
                        "Renewable Energy Percentage", 
                        min_value=0, 
                        max_value=100,
                        value=st.session_state.get('renewable_percentage', 0),
                        help="Percentage of electricity from renewable sources"
                    )
            
            # Heating and Cooling
            st.subheader("Heating and Cooling")
            with st.expander("Heating and Cooling Systems", expanded=True):
                col1, col2, col3 = st.columns(3)
                with col1:
                    heating_type = st.selectbox(
                        "Heating Type", 
                        ["Natural Gas", "Heating Oil", "Propane", "Electric Heating", "District Heating", "Biomass", "Other"],
                        key="heating_type_select"
                    )
                
                with col2:
                    heating_unit = st.selectbox(
                        "Unit", 
                        ["kWh", "MJ", "BTU", "m³", "liters", "gallons"],
                        key="heating_unit_select"
                    )
                
                with col3:
                    heating_amount = st.number_input(
                        f"Amount ({heating_unit})", 
                        min_value=0.0, 
                        value=st.session_state.get('heating_amount', 0.0),
                        help=f"Enter the amount of {heating_type} consumed for heating"
                    )
        
        # SCOPE 3 - Other Indirect Emissions
        with scope_tabs[2]:
            st.header("Scope 3: Other Indirect Emissions")
            st.markdown("""
            All other indirect emissions from your value chain, including business travel, employee commuting, waste, etc.
            """)
            
            # Business Travel
            st.subheader("Business Travel")
            with st.expander("Air Travel", expanded=True):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    flight_type = st.selectbox(
                        "Flight Type", 
                        ["Short-haul (<1,500 km)", "Medium-haul (1,500-3,700 km)", "Long-haul (>3,700 km)"],
                        key="flight_type_select"
                    )
                
                with col2:
                    flight_class = st.selectbox(
                        "Travel Class", 
                        ["Economy", "Premium Economy", "Business", "First"],
                        key="flight_class_select"
                    )
                
                with col3:
                    distance_unit = st.session_state.get('distance_unit', 'Kilometers')
                    flight_distance = st.number_input(
                        f"Distance ({distance_unit})", 
                        min_value=0.0, 
                        value=st.session_state.get('flight_distance', 0.0),
                        help=f"Enter the total flight distance"
                    )
            
            # Waste
            st.subheader("Waste Generation")
            with st.expander("Waste Disposal", expanded=True):
                col1, col2 = st.columns(2)
                with col1:
                    waste_type = st.selectbox(
                        "Waste Type", 
                        ["Landfill (Mixed)", "Recycled Paper", "Recycled Plastic", "Recycled Glass", 
                         "Recycled Metal", "Organic/Compost", "Electronic Waste", "Other"],
                        key="waste_type_select"
                    )
                
                with col2:
                    waste_amount = st.number_input(
                        "Amount (kg)", 
                        min_value=0.0, 
                        value=st.session_state.get('waste_amount', 0.0),
                        help=f"Enter the weight of {waste_type}"
                    )
            
            # Water
            st.subheader("Water Consumption")
            with st.expander("Water Usage", expanded=True):
                col1, col2 = st.columns(2)
                with col1:
                    water_type = st.selectbox(
                        "Water Source", 
                        ["Municipal Supply", "Well Water", "Harvested Rainwater", "Recycled Water", "Other"],
                        key="water_type_select"
                    )
                
                with col2:
                    water_amount = st.number_input(
                        "Amount (m³)", 
                        min_value=0.0, 
                        value=st.session_state.get('water_amount', 0.0),
                        help=f"Enter the volume of {water_type} consumed"
                    )
    
    # SMART DATA IMPORT TAB - AI-Enhanced Import
    with tabs[1]:
        st.header("Smart Data Import")
        st.markdown("""
        Upload Excel files with your emissions data, and Carbon Aegis will intelligently map the contents
        to appropriate emission categories and calculate your carbon footprint.
        """)
        
        # Initialize session state variables for smart import
        if 'smart_import_step' not in st.session_state:
            st.session_state.smart_import_step = 1
        if 'smart_imported_data' not in st.session_state:
            st.session_state.smart_imported_data = None
        if 'smart_column_mappings' not in st.session_state:
            st.session_state.smart_column_mappings = {}
        if 'smart_structured_data' not in st.session_state:
            st.session_state.smart_structured_data = None
        if 'smart_calculation_results' not in st.session_state:
            st.session_state.smart_calculation_results = None
        
        # Progress indicator
        progress_steps = ["Upload File", "Review Mappings", "Preview Results", "Save Data"]
        progress_cols = st.columns(len(progress_steps))
        
        for i, step in enumerate(progress_steps):
            with progress_cols[i]:
                if i + 1 < st.session_state.smart_import_step:
                    st.markdown(f"### ✅ **{i+1}. {step}**")
                elif i + 1 == st.session_state.smart_import_step:
                    st.markdown(f"### 🔄 **{i+1}. {step}**")
                else:
                    st.markdown(f"### {i+1}. {step}")
        
        # Step 1: Upload File
        if st.session_state.smart_import_step == 1:
            st.markdown('<div class="step-box active">', unsafe_allow_html=True)
            st.subheader("Step 1: Upload Your Data")
            
            # Add AI enhancement option
            use_ai = False
            if has_openai:
                use_ai = st.checkbox("Use AI for Enhanced Column Detection", value=True, 
                                  help="Uses OpenAI to better understand ambiguous column names")
            else:
                st.info("💡 For even better results, you can add an OpenAI API key to enable AI-powered column detection.")
            
            # File uploader
            uploaded_file = st.file_uploader(
                "Upload Excel File with Emissions Data",
                type=["xlsx", "xls"],
                help="Upload any Excel file with your emission data. Carbon Aegis will automatically detect columns."
            )
            
            if uploaded_file:
                if st.button("Process File", type="primary"):
                    with st.spinner("Analyzing your data..."):
                        try:
                            # Read the Excel file
                            df = read_excel_file(uploaded_file)
                            
                            if df is not None and not df.empty:
                                # Detect column types
                                column_mappings = detect_column_types(df, use_ai=use_ai)
                                
                                # Store results in session state
                                st.session_state.smart_imported_data = df
                                st.session_state.smart_column_mappings = column_mappings
                                st.session_state.smart_import_step = 2
                                
                                st.success(f"Successfully analyzed {len(df)} rows and {len(df.columns)} columns.")
                                st.rerun()
                            else:
                                st.error("Could not read data from the Excel file. Please check the file format.")
                        except Exception as e:
                            st.error(f"Error processing file: {str(e)}")
            
            # Add example file download
            st.markdown("### Need a Template?")
            st.markdown("""
            You can use any Excel file with your emissions data - no need for a specific template.
            Carbon Aegis will intelligently detect columns related to:
            
            * Fuel consumption (diesel, gasoline, etc.)
            * Electricity usage
            * Transport and travel
            * Waste generation
            * Water consumption
            * Refrigerants
            
            For best results, include columns with activity data, amounts, units, and categories.
            """)
            
            # Create sample file for download
            with st.expander("Download Sample Excel Template"):
                # Create a sample DataFrame
                sample_data = pd.DataFrame({
                    'Category': ['Electricity', 'Diesel Fuel', 'Natural Gas', 'Company Car', 'Refrigerant R-410A', 
                                 'Business Flight', 'Waste (Landfill)', 'Waste (Recycled)', 'Water'],
                    'Amount': [10500, 450, 2300, 15000, 2.5, 3500, 750, 500, 350],
                    'Unit': ['kWh', 'liters', 'm³', 'km', 'kg', 'km', 'kg', 'kg', 'm³'],
                    'Scope': ['Scope 2', 'Scope 1', 'Scope 1', 'Scope 1', 'Scope 1', 
                              'Scope 3', 'Scope 3', 'Scope 3', 'Scope 3'],
                    'Location': ['Main Office', 'Warehouse', 'Factory', 'Sales Fleet', 'HVAC Systems', 
                                 'International', 'All Facilities', 'All Facilities', 'All Facilities'],
                    'Date': ['2025-01-15', '2025-01-20', '2025-01-22', '2025-01-25', '2025-01-28',
                             '2025-02-05', '2025-02-10', '2025-02-10', '2025-02-15']
                })
                
                # Create Excel file
                buffer = io.BytesIO()
                with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                    sample_data.to_excel(writer, sheet_name='Emissions Data', index=False)
                    
                    # Add a documentation sheet
                    workbook = writer.book
                    doc_sheet = workbook.add_worksheet('Documentation')
                    
                    # Format for headers
                    header_format = workbook.add_format({
                        'bold': True,
                        'font_size': 12,
                        'font_color': 'white',
                        'bg_color': '#2E8B57',
                        'border': 1
                    })
                    
                    # Add documentation content
                    doc_sheet.write(0, 0, 'Carbon Aegis - Sample Emissions Data', header_format)
                    doc_sheet.write(1, 0, 'Instructions:')
                    doc_sheet.write(2, 0, '1. This is a SAMPLE file - customize it with your own data')
                    doc_sheet.write(3, 0, '2. Add or remove columns as needed - the AI will detect the content')
                    doc_sheet.write(4, 0, '3. Our flexible import system works with almost any Excel format')
                    doc_sheet.write(6, 0, 'Column Descriptions:')
                    doc_sheet.write(7, 0, 'Category - Type of emission activity (e.g., Electricity, Diesel)')
                    doc_sheet.write(8, 0, 'Amount - Quantity of the activity (numeric values)')
                    doc_sheet.write(9, 0, 'Unit - Measurement unit (e.g., kWh, liters, km)')
                    doc_sheet.write(10, 0, 'Scope - GHG Protocol scope (1, 2, or 3)')
                    doc_sheet.write(11, 0, 'Location - Where the activity occurred')
                    doc_sheet.write(12, 0, 'Date - When the activity occurred')
                    
                    # Format column width
                    doc_sheet.set_column('A:A', 50)
                
                # Offer download
                st.download_button(
                    label="📥 Download Sample Excel Template",
                    data=buffer.getvalue(),
                    file_name="carbon_aegis_sample_data.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Step 2: Review Mappings
        elif st.session_state.smart_import_step == 2 and st.session_state.smart_imported_data is not None:
            st.markdown('<div class="step-box active">', unsafe_allow_html=True)
            st.subheader("Step 2: Review Column Mappings")
            
            # Display data preview
            st.markdown("### Data Preview")
            st.dataframe(st.session_state.smart_imported_data.head(5))
            
            # Create form for adjusting mappings
            st.markdown("### Adjust Column Mappings")
            st.markdown("""
            Carbon Aegis has automatically detected what each column represents. 
            You can adjust these mappings if needed before proceeding.
            """)
            
            with st.form("column_mapping_form"):
                # Create tabs for different types of mappings
                mapping_tabs = st.tabs(["Primary Categories", "Units & Amounts", "Metadata"])
                
                # Primary emission categories
                with mapping_tabs[0]:
                    st.markdown("### Primary Emission Categories")
                    st.markdown("These columns determine the type of emissions (fuel, electricity, etc.)")
                    
                    # Get the primary category columns
                    primary_cols = [col for col, mapping in st.session_state.smart_column_mappings.items() 
                                   if mapping['category'] in ['fuel', 'electricity', 'transport', 'waste', 'water', 'refrigerant']]
                    
                    if primary_cols:
                        cols = st.columns(3)
                        for i, col in enumerate(primary_cols):
                            mapping = st.session_state.smart_column_mappings[col]
                            with cols[i % 3]:
                                # Show sample values
                                samples = ", ".join(str(v) for v in st.session_state.smart_imported_data[col].dropna().head(2).tolist())
                                if len(samples) > 30:
                                    samples = samples[:30] + "..."
                                st.markdown(f"**{col}** (samples: {samples})")
                                
                                # Category selection
                                selected_category = st.selectbox(
                                    f"Category for '{col}':",
                                    options=['fuel', 'electricity', 'transport', 'waste', 'water', 'refrigerant', 
                                            'amount', 'unit', 'date', 'category', 'location', 'notes', 'ignore'],
                                    index=['fuel', 'electricity', 'transport', 'waste', 'water', 'refrigerant', 
                                          'amount', 'unit', 'date', 'category', 'location', 'notes', 'ignore'].index(mapping['category']),
                                    key=f"primary_{col}"
                                )
                                
                                # Scope selection
                                scope_options = [None, 1, 2, 3]
                                scope_index = scope_options.index(mapping['scope']) if mapping['scope'] in scope_options else 0
                                selected_scope = st.selectbox(
                                    f"Scope for '{col}':",
                                    options=['Not Applicable', 'Scope 1', 'Scope 2', 'Scope 3'],
                                    index=scope_index,
                                    key=f"scope_{col}"
                                )
                                
                                # Update mapping
                                st.session_state.smart_column_mappings[col]['category'] = selected_category
                                st.session_state.smart_column_mappings[col]['scope'] = None if selected_scope == 'Not Applicable' else int(selected_scope[-1])
                    else:
                        st.info("No primary emission categories detected. Please adjust the mappings in the other tabs.")
                
                # Amounts and units
                with mapping_tabs[1]:
                    st.markdown("### Amounts and Units")
                    st.markdown("These columns contain the quantities and measurement units")
                    
                    # Get the amount and unit columns
                    amount_unit_cols = [col for col, mapping in st.session_state.smart_column_mappings.items() 
                                       if mapping['category'] in ['amount', 'unit']]
                    
                    if amount_unit_cols:
                        cols = st.columns(3)
                        for i, col in enumerate(amount_unit_cols):
                            mapping = st.session_state.smart_column_mappings[col]
                            with cols[i % 3]:
                                # Show sample values
                                samples = ", ".join(str(v) for v in st.session_state.smart_imported_data[col].dropna().head(2).tolist())
                                if len(samples) > 30:
                                    samples = samples[:30] + "..."
                                st.markdown(f"**{col}** (samples: {samples})")
                                
                                # Category selection
                                selected_category = st.selectbox(
                                    f"Category for '{col}':",
                                    options=['amount', 'unit', 'fuel', 'electricity', 'transport', 'waste', 'water', 
                                            'refrigerant', 'date', 'category', 'location', 'notes', 'ignore'],
                                    index=['amount', 'unit', 'fuel', 'electricity', 'transport', 'waste', 'water', 
                                          'refrigerant', 'date', 'category', 'location', 'notes', 'ignore'].index(mapping['category']),
                                    key=f"amount_unit_{col}"
                                )
                                
                                # Unit selection if it's an amount column
                                if selected_category == 'amount':
                                    unit_options = ['kWh', 'MWh', 'litres', 'gallons', 'kg', 'tonnes', 'km', 'miles', 'm³', 'None']
                                    current_unit = mapping.get('unit') if mapping.get('unit') else 'None'
                                    unit_index = unit_options.index(current_unit) if current_unit in unit_options else unit_options.index('None')
                                    selected_unit = st.selectbox(
                                        f"Unit for '{col}':",
                                        options=unit_options,
                                        index=unit_index,
                                        key=f"unit_{col}"
                                    )
                                    
                                    st.session_state.smart_column_mappings[col]['unit'] = None if selected_unit == 'None' else selected_unit
                                
                                # Update mapping
                                st.session_state.smart_column_mappings[col]['category'] = selected_category
                    else:
                        st.info("No amount or unit columns detected. Please adjust the mappings in the other tabs.")
                
                # Metadata columns
                with mapping_tabs[2]:
                    st.markdown("### Metadata")
                    st.markdown("These columns contain supporting information like dates, locations, etc.")
                    
                    # Get the metadata columns
                    metadata_cols = [col for col, mapping in st.session_state.smart_column_mappings.items() 
                                    if mapping['category'] in ['date', 'category', 'location', 'notes', 'unknown', 'ignore']]
                    
                    if metadata_cols:
                        cols = st.columns(3)
                        for i, col in enumerate(metadata_cols):
                            mapping = st.session_state.smart_column_mappings[col]
                            with cols[i % 3]:
                                # Show sample values
                                samples = ", ".join(str(v) for v in st.session_state.smart_imported_data[col].dropna().head(2).tolist())
                                if len(samples) > 30:
                                    samples = samples[:30] + "..."
                                st.markdown(f"**{col}** (samples: {samples})")
                                
                                # Category selection
                                selected_category = st.selectbox(
                                    f"Category for '{col}':",
                                    options=['category', 'date', 'location', 'notes', 'fuel', 'electricity', 'transport', 
                                            'waste', 'water', 'refrigerant', 'amount', 'unit', 'ignore'],
                                    index=['category', 'date', 'location', 'notes', 'fuel', 'electricity', 'transport', 
                                          'waste', 'water', 'refrigerant', 'amount', 'unit', 'ignore', 'unknown'].index(mapping['category']),
                                    key=f"metadata_{col}"
                                )
                                
                                # Scope selection if it's a category column
                                if selected_category == 'category':
                                    scope_options = [None, 1, 2, 3]
                                    scope_index = scope_options.index(mapping['scope']) if mapping['scope'] in scope_options else 0
                                    selected_scope = st.selectbox(
                                        f"Scope for '{col}':",
                                        options=['Not Applicable', 'Scope 1', 'Scope 2', 'Scope 3'],
                                        index=scope_index,
                                        key=f"meta_scope_{col}"
                                    )
                                    
                                    st.session_state.smart_column_mappings[col]['scope'] = None if selected_scope == 'Not Applicable' else int(selected_scope[-1])
                                
                                # Update mapping
                                st.session_state.smart_column_mappings[col]['category'] = selected_category
                    else:
                        st.info("No metadata columns detected. Please adjust the mappings in the other tabs.")
                
                # Navigation buttons
                col1, col2, col3 = st.columns([1, 1, 2])
                with col1:
                    back_button = st.form_submit_button("⬅️ Back", help="Return to file upload")
                with col2:
                    reset_button = st.form_submit_button("🔄 Reset Mappings", help="Reset to detected mappings")
                with col3:
                    next_button = st.form_submit_button("Next: Preview Results ➡️", type="primary")
            
            # Handle form actions
            if back_button:
                st.session_state.smart_import_step = 1
                st.rerun()
            
            if reset_button:
                use_ai = has_openai
                # Re-detect column types
                st.session_state.smart_column_mappings = detect_column_types(st.session_state.smart_imported_data, use_ai=use_ai)
                st.success("Column mappings reset to detected values.")
                st.rerun()
            
            if next_button:
                # Process the data with the mappings
                with st.spinner("Processing your data..."):
                    try:
                        # Map to emission categories
                        structured_data = map_to_emission_categories(
                            st.session_state.smart_imported_data,
                            st.session_state.smart_column_mappings,
                            use_ai=has_openai
                        )
                        
                        # Calculate emissions
                        calculation_results = calculate_emissions(structured_data)
                        
                        # Store results in session state
                        st.session_state.smart_structured_data = structured_data
                        st.session_state.smart_calculation_results = calculation_results
                        st.session_state.smart_import_step = 3
                        
                        st.success("Data processed successfully!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error processing data: {str(e)}")
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Step 3: Preview Results
        elif st.session_state.smart_import_step == 3 and st.session_state.smart_structured_data and st.session_state.smart_calculation_results:
            st.markdown('<div class="step-box active">', unsafe_allow_html=True)
            st.subheader("Step 3: Preview Results")
            
            # Display a summary of findings
            results = st.session_state.smart_calculation_results
            
            # Summary metrics
            st.markdown("### Emissions Summary")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Scope 1", f"{results['scope1']['total']:.2f} kg CO₂e")
            with col2:
                st.metric("Scope 2", f"{results['scope2']['total']:.2f} kg CO₂e")
            with col3:
                st.metric("Scope 3", f"{results['scope3']['total']:.2f} kg CO₂e")
            with col4:
                st.metric("Total", f"{results['total']:.2f} kg CO₂e")
            
            # Tabs for detailed results
            detail_tabs = st.tabs(["Scope 1", "Scope 2", "Scope 3", "Calculation Details"])
            
            # Scope 1 details
            with detail_tabs[0]:
                st.markdown("### Scope 1: Direct Emissions")
                
                # Check if we have scope 1 data
                if results['scope1']['total'] > 0:
                    # Create a DataFrame for display
                    scope1_items = [item for item in results['line_items'] if item['scope'] == 'scope1']
                    
                    if scope1_items:
                        scope1_df = pd.DataFrame([{
                            'Type': item['type'].capitalize(),
                            'Amount': item['data'].get('amount', 0),
                            'Unit': item['data'].get('unit', ''),
                            'Emissions (kg CO₂e)': f"{item['emissions']:.2f}",
                            'Category': item['data'].get('category', '')
                        } for item in scope1_items])
                        
                        st.dataframe(scope1_df)
                        
                        # Show breakdown by category
                        st.markdown("#### Breakdown by Category")
                        for category, value in results['scope1']['categories'].items():
                            st.markdown(f"**{category.capitalize()}**: {value:.2f} kg CO₂e")
                    else:
                        st.info("No Scope 1 emissions identified in the data.")
                else:
                    st.info("No Scope 1 emissions identified in the data.")
            
            # Scope 2 details
            with detail_tabs[1]:
                st.markdown("### Scope 2: Energy Indirect Emissions")
                
                # Check if we have scope 2 data
                if results['scope2']['total'] > 0:
                    # Create a DataFrame for display
                    scope2_items = [item for item in results['line_items'] if item['scope'] == 'scope2']
                    
                    if scope2_items:
                        scope2_df = pd.DataFrame([{
                            'Type': item['type'].capitalize(),
                            'Amount': item['data'].get('amount', 0),
                            'Unit': item['data'].get('unit', ''),
                            'Emissions (kg CO₂e)': f"{item['emissions']:.2f}",
                            'Category': item['data'].get('category', '')
                        } for item in scope2_items])
                        
                        st.dataframe(scope2_df)
                        
                        # Show breakdown by category
                        st.markdown("#### Breakdown by Category")
                        for category, value in results['scope2']['categories'].items():
                            st.markdown(f"**{category.capitalize()}**: {value:.2f} kg CO₂e")
                    else:
                        st.info("No Scope 2 emissions identified in the data.")
                else:
                    st.info("No Scope 2 emissions identified in the data.")
            
            # Scope 3 details
            with detail_tabs[2]:
                st.markdown("### Scope 3: Other Indirect Emissions")
                
                # Check if we have scope 3 data
                if results['scope3']['total'] > 0:
                    # Create a DataFrame for display
                    scope3_items = [item for item in results['line_items'] if item['scope'] == 'scope3']
                    
                    if scope3_items:
                        scope3_df = pd.DataFrame([{
                            'Type': item['type'].capitalize(),
                            'Amount': item['data'].get('amount', 0),
                            'Unit': item['data'].get('unit', ''),
                            'Emissions (kg CO₂e)': f"{item['emissions']:.2f}",
                            'Category': item['data'].get('category', '')
                        } for item in scope3_items])
                        
                        st.dataframe(scope3_df)
                        
                        # Show breakdown by category
                        st.markdown("#### Breakdown by Category")
                        for category, value in results['scope3']['categories'].items():
                            st.markdown(f"**{category.capitalize()}**: {value:.2f} kg CO₂e")
                    else:
                        st.info("No Scope 3 emissions identified in the data.")
                else:
                    st.info("No Scope 3 emissions identified in the data.")
            
            # Calculation details
            with detail_tabs[3]:
                st.markdown("### Calculation Details")
                st.markdown("This shows exactly how each emission value was calculated")
                
                # Create a DataFrame with calculation details
                if results['line_items']:
                    calc_df = pd.DataFrame([{
                        'Scope': item['scope'].capitalize().replace('scope', 'Scope '),
                        'Type': item['type'].capitalize(),
                        'Calculation': item['calculation'],
                        'Emissions (kg CO₂e)': f"{item['emissions']:.2f}"
                    } for item in results['line_items']])
                    
                    st.dataframe(calc_df)
                else:
                    st.info("No calculations performed.")
            
            # Export results to CSV
            if results['line_items']:
                st.markdown("### Export Results")
                
                # Create CSV for export
                csv_data = io.StringIO()
                export_df = pd.DataFrame([{
                    'Scope': item['scope'].capitalize().replace('scope', 'Scope '),
                    'Type': item['type'].capitalize(),
                    'Amount': item['data'].get('amount', 0),
                    'Unit': item['data'].get('unit', ''),
                    'Category': item['data'].get('category', ''),
                    'Emissions (kg CO₂e)': item['emissions'],
                    'Calculation': item['calculation']
                } for item in results['line_items']])
                
                export_df.to_csv(csv_data, index=False)
                
                # Offer download
                st.download_button(
                    label="📥 Download Results as CSV",
                    data=csv_data.getvalue(),
                    file_name="carbon_aegis_results.csv",
                    mime="text/csv"
                )
            
            # Navigation buttons
            col1, col2, col3 = st.columns([1, 1, 2])
            with col1:
                if st.button("⬅️ Back to Mappings"):
                    st.session_state.smart_import_step = 2
                    st.rerun()
            
            with col2:
                if st.button("🔄 Start Over"):
                    st.session_state.smart_import_step = 1
                    st.session_state.smart_imported_data = None
                    st.session_state.smart_column_mappings = {}
                    st.session_state.smart_structured_data = None
                    st.session_state.smart_calculation_results = None
                    st.rerun()
            
            with col3:
                if st.button("Save Results ➡️", type="primary"):
                    st.session_state.smart_import_step = 4
                    st.rerun()
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Step 4: Save Data
        elif st.session_state.smart_import_step == 4 and st.session_state.smart_structured_data and st.session_state.smart_calculation_results:
            st.markdown('<div class="step-box active">', unsafe_allow_html=True)
            st.subheader("Step 4: Save Results")
            
            # Show a summary
            results = st.session_state.smart_calculation_results
            
            st.markdown("### Data Ready to Save")
            st.markdown(f"""
            You've successfully processed your emissions data:
            
            * **Total Emissions**: {results['total']:.2f} kg CO₂e
            * **Scope 1**: {results['scope1']['total']:.2f} kg CO₂e
            * **Scope 2**: {results['scope2']['total']:.2f} kg CO₂e
            * **Scope 3**: {results['scope3']['total']:.2f} kg CO₂e
            * **Line Items**: {len(results['line_items'])} emission activities
            
            Save this data to continue analyzing it in Carbon Aegis.
            """)
            
            # Form for save options
            with st.form("save_options_form"):
                col1, col2 = st.columns(2)

                with col1:
                    organization_name = st.text_input(
                        "Organization Name",
                        value=st.session_state.get('organization_name', ''),
                        placeholder="Enter your organization's name"
                    )
                
                with col2:
                    report_year = st.number_input(
                        "Reporting Year",
                        min_value=2000,
                        max_value=2050,
                        value=st.session_state.get('report_year', datetime.now().year)
                    )
                
                col1, col2 = st.columns([1, 3])
                with col1:
                    cancel_button = st.form_submit_button("⬅️ Back", help="Return to preview")
                with col2:
                    save_button = st.form_submit_button("💾 Save Data and Continue", type="primary")


            # Handle form actions
            if cancel_button:
                st.session_state.smart_import_step = 3
                st.rerun()
            
            if save_button:
                # Convert to app format
                app_data = convert_to_app_format(
                    st.session_state.smart_structured_data,
                    st.session_state.smart_calculation_results
                )
                
                # Save to session state
                with st.spinner("Saving data..."):
                    try:
                        # Update organization info
                        st.session_state.organization_name = organization_name
                        st.session_state.report_year = report_year
                        
                        # Save the data to session state
                        record_id = save_to_session_state(app_data)
                        
                        # Update session state with calculation results directly
                        st.session_state.emissions_data = app_data['emissions_data']
                        st.session_state.scope1_total = app_data['scope1_total']
                        st.session_state.scope2_total = app_data['scope2_total']
                        st.session_state.scope3_total = app_data['scope3_total']
                        st.session_state.total_emissions = app_data['total_emissions']
                        
                        # Show success message
                        st.success(f"Data saved successfully with record ID: {record_id}")
                        
                        # Navigation options
                        st.markdown("### What would you like to do next?")
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            if st.button("📊 View Dashboard", use_container_width=True):
                                st.switch_page("pages/2_Dashboard.py")
                        
                        with col2:
                            if st.button("📑 Generate Report", use_container_width=True):
                                st.switch_page("pages/3_Report.py")
                        
                        with col3:
                            if st.button("🔄 Import More Data", use_container_width=True):
                                st.session_state.smart_import_step = 1
                                st.session_state.smart_imported_data = None
                                st.session_state.smart_column_mappings = {}
                                st.session_state.smart_structured_data = None
                                st.session_state.smart_calculation_results = None
                                st.rerun()
                    except Exception as e:
                        st.error(f"Error saving data: {str(e)}")
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    # SETTINGS TAB
    with tabs[2]:
        st.header("Settings")
        
        st.subheader("Reporting Period")
        col1, col2 = st.columns(2)
        with col1:
            time_period = st.selectbox(
                "Time Period", 
                ["Daily", "Weekly", "Monthly", "Quarterly", "Annually"],
                index=4 if 'time_period' not in st.session_state else 
                      ["Daily", "Weekly", "Monthly", "Quarterly", "Annually"].index(st.session_state.time_period),
                key="time_period_select"
            )
        
        st.subheader("Calculation Method")
        calculation_method = st.selectbox(
            "Accuracy Level", 
            ["Exact (measured data)", "Average (based on typical values)", "Estimate (approximated)"],
            index=0 if 'calculation_method' not in st.session_state else 
                  ["Exact (measured data)", "Average (based on typical values)", "Estimate (approximated)"].index(st.session_state.calculation_method),
            key="calculation_method_select"
        )
        
        st.subheader("Preferred Units")
        col1, col2 = st.columns(2)
        with col1:
            distance_unit = st.selectbox(
                "Distance Unit", 
                ["Kilometers", "Miles"],
                index=0 if 'distance_unit' not in st.session_state else 
                      ["Kilometers", "Miles"].index(st.session_state.distance_unit),
                key="distance_unit_select"
            )
        with col2:
            volume_unit = st.selectbox(
                "Volume Unit", 
                ["Liters", "Gallons"],
                index=0 if 'volume_unit' not in st.session_state else 
                      ["Liters", "Gallons"].index(st.session_state.volume_unit),
                key="volume_unit_select"
            )
        
        # OpenAI API Status section
        st.subheader("AI Enhancement Status")
        if has_openai:
            st.success("✅ OpenAI API is configured and available for enhanced column detection")
        else:
            st.warning("⚠️ OpenAI API is not configured. AI-powered features will be limited.")
            st.info("Add an OpenAI API key to your environment variables to enable AI-powered features.")
            
        st.info("These settings affect how your emissions are calculated and displayed across the application.")
    
    # Action buttons in a styled container
    st.markdown("---")
    st.subheader("📋 Actions")
    
    with st.container():
        st.markdown('<div class="action-container">', unsafe_allow_html=True)
        
        # Create three columns for the buttons
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            save_button = st.button("💾 Save and Calculate", use_container_width=True)
        with col2:
            export_button = st.button("📤 Export Data", use_container_width=True)
        with col3:
            clear_button = st.button("🗑️ Clear All Data", use_container_width=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Handle button clicks
    if save_button:
        # Gather all the input data
        input_data = {
            # Settings
            'time_period': time_period,
            'calculation_method': calculation_method,
            'distance_unit': distance_unit,
            'volume_unit': volume_unit,
            
            # Fuel & Transport data
            'fuel_type': fuel_type,
            'fuel_unit': fuel_unit,
            'fuel_amount': fuel_amount,
            'vehicle_type': vehicle_type,
            'distance_unit_vehicle': distance_unit_vehicle,
            'vehicle_distance': vehicle_distance,
            'flight_type': flight_type,
            'flight_class': flight_class,
            'flight_distance': flight_distance,
            'refrigerant_type': refrigerant_type,
            'refrigerant_amount': refrigerant_amount,
            
            # Energy data
            'electricity': electricity,
            'electricity_unit': electricity_unit,
            'grid_region': grid_region,
            'renewable_percentage': renewable_percentage,
            'heating_type': heating_type,
            'heating_unit': heating_unit,
            'heating_amount': heating_amount,
            
            # Other sources data
            'waste_type': waste_type,
            'waste_amount': waste_amount,
            'water_type': water_type,
            'water_amount': water_amount,
        }
        
        # Save to session state
        record_id = save_to_session_state(input_data)
        
        # Display message
        st.success(f"Data saved (Record #{record_id}) and ready for calculation! Navigate to the Dashboard to view your results.")
        st.session_state.has_data = True
    
    # Handle export button
    if export_button and st.session_state.has_data:
        # Create export data
        export_data = {
            "organization": st.session_state.get('organization_name', 'My Organization'),
            "report_year": st.session_state.get('report_year', 2025),
            "emissions_data": st.session_state.get('emissions_data', {}),
            "scope1_total": st.session_state.get('scope1_total', 0),
            "scope2_total": st.session_state.get('scope2_total', 0),
            "scope3_total": st.session_state.get('scope3_total', 0),
            "total_emissions": st.session_state.get('total_emissions', 0),
            "input_data": st.session_state.get('input_data', {})
        }
        
        # Convert to JSON
        json_data = json.dumps(export_data, indent=4)
        
        # Offer download
        st.download_button(
            label="📥 Download Data as JSON",
            data=json_data,
            file_name="carbon_aegis_data.json",
            mime="application/json"
        )
    elif export_button and not st.session_state.has_data:
        st.warning("No data available to export. Please enter data first or import from Excel.")
    
    # Handle clear button
    if clear_button:
        clear_data()
        st.success("All data has been cleared!")
        st.rerun()
    
    # Navigation section
    st.markdown("---")
    st.subheader("📍 Navigation")
    
    # Create a navigation container with styled buttons
    with st.container():
        st.markdown('<div class="nav-container">', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            if st.button("📊 View Dashboard", use_container_width=True):
                st.switch_page("pages/2_Dashboard.py")
        
        with col2:
            if st.button("📑 Generate Report", use_container_width=True):
                st.switch_page("pages/3_Report.py")
                
        with col3:
            if st.button("🏠 Home", use_container_width=True):
                st.switch_page("app.py")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Help section with improved styling
    st.markdown("### ❓ Help & Resources")
    with st.container():
        st.markdown('<div class="help-container">', unsafe_allow_html=True)
        
        st.markdown("""
        ### Carbon Aegis Data Input Guide
        
        **Scope Classification Tips:**
        * **Scope 1**: Direct emissions from sources you own or control
        * **Scope 2**: Purchased electricity, steam, heating, and cooling  
        * **Scope 3**: All other indirect emissions in your value chain
        
        **For Best Results:**
        * Use the Smart Data Import feature for bulk data uploads
        * Upload any Excel file - our AI-powered system will detect emission categories
        * For quick manual entries, use the Manual Input tab
        * Select the appropriate time period and units in Settings tab
        
        **Need Additional Help?**
        Hover over any input field for specific guidance, or contact Carbon Aegis support for assistance.
        """)
        
        st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()