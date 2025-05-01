import pandas as pd
import numpy as np
import os
import io
import base64
from datetime import datetime

def main():
    print("Carbon Aegis CLI Version")
    print("A simple GHG emissions calculator")
    print("-" * 50)
    
    # Menu
    while True:
        print("\nMain Menu:")
        print("1. Process Excel File")
        print("2. View Sample Data")
        print("3. Exit")
        
        choice = input("Enter your choice (1-3): ")
        
        if choice == '1':
            file_path = input("Enter the path to Excel file: ")
            process_excel_file(file_path)
        elif choice == '2':
            view_sample_data()
        elif choice == '3':
            print("Exiting Carbon Aegis CLI. Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

def process_excel_file(file_path):
    try:
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            return
            
        print(f"Processing file: {file_path}")
        df = pd.read_excel(file_path)
        
        print(f"Successfully read Excel file. Shape: {df.shape}")
        print("\nFirst 5 rows:")
        print(df.head())
        
        # Detect column types
        column_types = detect_column_types(df)
        print("\nDetected column types:")
        for col, type_name in column_types.items():
            print(f"  {col}: {type_name}")
            
        # Calculate emissions (simplified)
        results = calculate_emissions(df, column_types)
        print("\nEmissions calculation results:")
        print(f"Total emissions: {results['total_emissions']:.2f} kg CO2e")
        print("Emissions by scope:")
        for scope, value in results['by_scope'].items():
            print(f"  {scope}: {value:.2f} kg CO2e")
            
    except Exception as e:
        print(f"Error processing Excel file: {e}")

def view_sample_data():
    print("Sample GHG Emissions Data")
    print("-" * 30)
    
    # Create sample data
    data = {
        'Date': ['2024-01-01', '2024-01-02', '2024-01-03', '2024-01-04', '2024-01-05'],
        'Activity': ['Electricity', 'Natural Gas', 'Vehicle Fuel', 'Air Travel', 'Waste'],
        'Amount': [1000, 500, 200, 5000, 100],
        'Unit': ['kWh', 'kWh', 'liters', 'km', 'kg'],
        'Emission Factor': [0.45, 0.18, 2.3, 0.15, 0.5],
        'Scope': ['Scope 2', 'Scope 1', 'Scope 1', 'Scope 3', 'Scope 3']
    }
    
    df = pd.DataFrame(data)
    print(df)
    
    # Calculate simple emissions
    df['Emissions (kg CO2e)'] = df['Amount'] * df['Emission Factor']
    total = df['Emissions (kg CO2e)'].sum()
    
    print(f"\nTotal Emissions: {total:.2f} kg CO2e")

def detect_column_types(df):
    """Detect column types in the DataFrame"""
    column_types = {}
    
    # Define patterns to look for
    patterns = {
        'date': ['date', 'year', 'month', 'period', 'time'],
        'activity': ['activity', 'description', 'type', 'source', 'category'],
        'amount': ['amount', 'quantity', 'volume', 'consumption', 'usage'],
        'unit': ['unit', 'uom', 'measure'],
        'emission_factor': ['factor', 'ef', 'emission'],
        'scope': ['scope']
    }
    
    # Check column names for matches
    for col in df.columns:
        col_lower = str(col).lower()
        for category, keywords in patterns.items():
            if any(keyword in col_lower for keyword in keywords):
                column_types[col] = category
                break
    
    # For columns not matched by name, try to infer from content
    for col in df.columns:
        if col not in column_types:
            # Check if it's a date column
            if df[col].dtype == 'datetime64[ns]':
                column_types[col] = 'date'
            # Check if it's a numeric column (likely amount)
            elif pd.api.types.is_numeric_dtype(df[col]):
                if 'amount' not in column_types.values():
                    column_types[col] = 'amount'
                elif 'emission_factor' not in column_types.values():
                    column_types[col] = 'emission_factor'
            # Check if it contains scope information
            elif all(isinstance(val, str) and 'scope' in val.lower() for val in df[col].dropna()):
                column_types[col] = 'scope'
            # If still not categorized, check if it contains mostly text (likely activity)
            elif df[col].dtype == 'object' and 'activity' not in column_types.values():
                column_types[col] = 'activity'
    
    return column_types

def calculate_emissions(df, column_mappings):
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
    
    # Default emission factors (simplified)
    default_factors = {
        'electricity': 0.45,  # kg CO2e per kWh
        'natural_gas': 0.18,  # kg CO2e per kWh
        'vehicle_fuel': 2.3,  # kg CO2e per liter
        'air_travel': 0.15,   # kg CO2e per km
        'waste': 0.5,         # kg CO2e per kg
        'default': 1.0        # Generic factor
    }
    
    # Identify the relevant columns
    amount_col = next((col for col, cat in column_mappings.items() if cat == 'amount'), None)
    activity_col = next((col for col, cat in column_mappings.items() if cat == 'activity'), None)
    scope_col = next((col for col, cat in column_mappings.items() if cat == 'scope'), None)
    ef_col = next((col for col, cat in column_mappings.items() if cat == 'emission_factor'), None)
    
    if not amount_col:
        print("No amount column identified")
        return results
    
    # Process each row
    for idx, row in df.iterrows():
        # Get the amount
        amount = row[amount_col]
        if not pd.api.types.is_numeric_dtype(type(amount)):
            continue
            
        # Determine activity type
        activity = row[activity_col] if activity_col else "Unknown"
        
        # Determine emission factor
        ef = row[ef_col] if ef_col else None
        if ef is None or not pd.api.types.is_numeric_dtype(type(ef)):
            # Try to assign a default factor based on activity
            activity_lower = str(activity).lower()
            ef = next((factor for key, factor in default_factors.items() 
                      if key in activity_lower), default_factors['default'])
        
        # Calculate emissions for this line item
        emissions = amount * ef
        
        # Determine scope
        scope = "Scope 3"  # Default
        if scope_col and not pd.isna(row[scope_col]):
            scope_value = str(row[scope_col]).lower()
            if '1' in scope_value:
                scope = "Scope 1"
            elif '2' in scope_value:
                scope = "Scope 2"
            elif '3' in scope_value:
                scope = "Scope 3"
                
        # Update results
        results['total_emissions'] += emissions
        results['by_scope'][scope] += emissions
        
        # Update category breakdown
        category = str(activity)[:50]  # Truncate long activity names
        if category not in results['by_category']:
            results['by_category'][category] = 0
        results['by_category'][category] += emissions
        
        # Add line item
        results['line_items'].append({
            'activity': activity,
            'amount': amount,
            'emission_factor': ef,
            'emissions': emissions,
            'scope': scope
        })
    
    return results

if __name__ == "__main__":
    main()