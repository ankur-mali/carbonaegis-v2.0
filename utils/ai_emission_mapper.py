import streamlit as st
import pandas as pd
import numpy as np
import re
import os
import tempfile
import io
from openai import OpenAI

# OpenAI API client
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

def has_openai_api():
    """Check if OpenAI API key is available"""
    return OPENAI_API_KEY is not None and OPENAI_API_KEY != ""

def analyze_column_with_ai(column_name, sample_values=None):
    """
    Use OpenAI to analyze a column name and sample values to determine the emission category
    
    Args:
        column_name: The name of the column to analyze
        sample_values: Sample values from the column (optional)
    
    Returns:
        dict: Dictionary with detected category, unit, and scope
    """
    if not has_openai_api():
        return None
    
    try:
        client = OpenAI(api_key=OPENAI_API_KEY)
        
        # Create a prompt based on the column name and sample values
        prompt = f"Analyze this column from an emissions data spreadsheet and classify it into one of these categories: 'fuel', 'electricity', 'transport', 'waste', 'water', 'refrigerant', 'amount', 'unit', 'date', 'category', 'notes', 'location'.\n\nColumn name: '{column_name}'"
        
        if sample_values and len(sample_values) > 0:
            sample_str = ", ".join([str(v) for v in sample_values if v is not None and pd.notna(v)])
            if sample_str:
                prompt += f"\nSample values: {sample_str}"
        
        prompt += "\n\nRespond in JSON format with these fields: 'category' (one of the categories listed above), 'scope' (1, 2, or 3, or null if not applicable), 'unit' (the measurement unit if detectable, or null), 'confidence' (0-1 score of confidence in the classification)."
        
        # Call the OpenAI API
        response = client.chat.completions.create(
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

def read_excel_file(file):
    """
    Read an Excel file into a pandas DataFrame, handling various formats
    
    Args:
        file: The uploaded Excel file
    
    Returns:
        pd.DataFrame: The data from the Excel file
    """
    try:
        # First save the uploaded file to a temporary location
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp_file:
            # Write the uploaded file data to the temporary file
            tmp_file.write(file.getvalue())
            tmp_path = tmp_file.name
        
        # Try to read the file with different settings
        try:
            # Try reading with default settings
            df = pd.read_excel(tmp_path)
        except Exception:
            try:
                # Try reading with sheet_name=0 (first sheet)
                df = pd.read_excel(tmp_path, sheet_name=0)
            except Exception:
                try:
                    # Try reading all sheets and concatenate
                    dfs = pd.read_excel(tmp_path, sheet_name=None)
                    if len(dfs) > 0:
                        # Use the first sheet that has data
                        for sheet_name, sheet_df in dfs.items():
                            if not sheet_df.empty:
                                df = sheet_df
                                break
                    else:
                        raise ValueError("No data found in Excel file")
                except Exception as e:
                    st.error(f"Could not read Excel file: {str(e)}")
                    return None
        
        # Clean up the temporary file
        os.unlink(tmp_path)
        
        # Clean up column names
        df.columns = [str(col).strip() for col in df.columns]
        
        # Replace NaN with None for better handling
        df = df.replace({np.nan: None})
        
        return df
    except Exception as e:
        st.error(f"Error reading Excel file: {str(e)}")
        return None

def detect_column_types(df, use_ai=False):
    """
    Detect the types of columns in the DataFrame
    
    Args:
        df: DataFrame to analyze
        use_ai: Whether to use OpenAI for difficult columns
    
    Returns:
        dict: Detected column types
    """
    column_types = {}
    
    # Regular expressions for pattern matching (extended with more patterns)
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
    
    # First pass: Check column names against patterns
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
        if not matched and use_ai and has_openai_api():
            # Get a few sample values
            sample_values = df[column].dropna().head(3).tolist()
            
            try:
                ai_result = analyze_column_with_ai(column, sample_values)
                if ai_result:
                    import json
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

def infer_from_content(df, column, column_types):
    """
    Infer column type from content
    
    Args:
        df: DataFrame
        column: Column name
        column_types: Current column types dict
    
    Returns:
        bool: Whether a match was found
    """
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

def detect_unit(column):
    """
    Detect the unit from a column of values
    
    Args:
        column: DataFrame column
    
    Returns:
        str: Detected unit or None
    """
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
        # Sample a few values
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

def get_scope_for_category(category):
    """
    Get the emissions scope for a category
    
    Args:
        category: Category name
    
    Returns:
        int: Scope (1, 2, or 3) or None
    """
    scope_mapping = {
        'fuel': 1,
        'refrigerant': 1,
        'electricity': 2,
        'transport': 3,
        'waste': 3,
        'water': 3
    }
    
    return scope_mapping.get(category)

def load_emission_factors(file_path=None):
    """
    Load emission factors from a file or use default values
    
    Args:
        file_path: Path to emission factors file (optional)
    
    Returns:
        dict: Emission factors by category and type
    """
    # Default emission factors if no file is provided
    default_factors = {
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
            'Global Average': 0.48   # kg CO2e per kWh
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
    
    # If a file path is provided, try to load from it
    if file_path:
        try:
            # Determine file type by extension
            if file_path.endswith('.csv'):
                df = pd.read_csv(file_path)
            elif file_path.endswith('.xlsx') or file_path.endswith('.xls'):
                df = pd.read_excel(file_path)
            else:
                st.warning(f"Unsupported file type: {file_path}")
                return default_factors
            
            # TODO: Parse the emission factors from the file
            # This will depend on the specific format of your emission factors file
            
            # For now, just return the default factors
            return default_factors
        except Exception as e:
            st.warning(f"Error loading emission factors: {str(e)}")
            return default_factors
    
    return default_factors

def process_defra_emission_factors(file_path):
    """
    Process DEFRA emission factors from Excel file
    
    Args:
        file_path: Path to DEFRA emission factors file
    
    Returns:
        dict: Processed emission factors
    """
    try:
        # Load the DEFRA file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp_file:
            # Write the uploaded file data to the temporary file
            with open(file_path, 'rb') as src_file:
                tmp_file.write(src_file.read())
            tmp_path = tmp_file.name
        
        # Try to read the file
        try:
            df = pd.read_excel(tmp_path, sheet_name=None)
        except Exception as e:
            st.error(f"Error reading DEFRA file: {str(e)}")
            return None
        
        # Clean up
        os.unlink(tmp_path)
        
        # Process the data based on DEFRA format
        # This will depend on the specific format of your DEFRA file
        
        # For now, return a simple structure
        factors = {
            'fuel': {},
            'electricity': {},
            'transport': {},
            'waste': {},
            'water': {},
            'refrigerant': {}
        }
        
        # TODO: Extract factors from the DEFRA file
        
        return factors
    except Exception as e:
        st.error(f"Error processing DEFRA file: {str(e)}")
        return None

def map_to_emission_categories(df, column_mappings, use_ai=False):
    """
    Map DataFrame to emission categories
    
    Args:
        df: DataFrame to map
        column_mappings: Column mappings
        use_ai: Whether to use AI for difficult mappings
    
    Returns:
        dict: Structured data for Carbon Aegis
    """
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
                if pd.notna(row[col]) and pd.api.types.is_numeric_dtype(type(row[col])):
                    amount = float(row[col])
                    break
        
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
    """
    Calculate emissions based on structured data
    
    Args:
        structured_data: Structured data
        emission_factors: Emission factors to use
    
    Returns:
        dict: Calculation results
    """
    if emission_factors is None:
        emission_factors = load_emission_factors()
    
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
                    if isinstance(value, str) and any(keyword in value.lower() for keyword in ['uk', 'us', 'eu', 'china', 'india']):
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
    """
    Convert structured data and calculation results to app format
    
    Args:
        structured_data: Structured data
        calculation_results: Calculation results
    
    Returns:
        dict: Data in app format
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