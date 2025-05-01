import streamlit as st
import pandas as pd
import numpy as np
from utils.calculations import (
    calculate_scope1_emissions, calculate_scope2_emissions, 
    calculate_scope3_emissions, calculate_total_emissions
)

def initialize_session_state():
    """Initialize all required session state variables if they don't exist"""
    
    # Organization information
    if 'organization_name' not in st.session_state:
        st.session_state.organization_name = ""
    if 'reporting_year' not in st.session_state:
        st.session_state.reporting_year = 2023
    if 'organization_sector' not in st.session_state:
        st.session_state.organization_sector = ""
    if 'organization_location' not in st.session_state:
        st.session_state.organization_location = ""
        
    # Scope 1 data - Stationary combustion (fuels)
    if 'fuel_data' not in st.session_state:
        st.session_state.fuel_data = {
            'Natural Gas (m³)': 0.0,
            'Diesel (liters)': 0.0,
            'Propane (liters)': 0.0,
            'Heating Oil (liters)': 0.0,
            'Coal (kg)': 0.0,
            'Biomass (kg)': 0.0
        }
    
    # Scope 1 data - Mobile combustion (company vehicles)
    if 'vehicle_data' not in st.session_state:
        st.session_state.vehicle_data = {
            'Gasoline Car (km)': 0.0,
            'Diesel Car (km)': 0.0,
            'Hybrid Car (km)': 0.0,
            'Electric Vehicle (km)': 0.0,
            'Light Duty Truck (km)': 0.0,
            'Heavy Duty Truck (km)': 0.0
        }
    
    # Scope 1 data - Refrigerant leakage
    if 'refrigerant_data' not in st.session_state:
        st.session_state.refrigerant_data = {
            'R-410A (kg)': 0.0,
            'R-134a (kg)': 0.0,
            'R-404A (kg)': 0.0,
            'R-407C (kg)': 0.0
        }
    
    # Scope 2 data - Electricity
    if 'electricity_data' not in st.session_state:
        st.session_state.electricity_data = {
            'Grid Electricity (kWh)': 0.0,
            'Renewable Energy (kWh)': 0.0
        }
    
    # Scope 2 data - District energy
    if 'district_energy_data' not in st.session_state:
        st.session_state.district_energy_data = {
            'District Heating (kWh)': 0.0,
            'District Cooling (kWh)': 0.0
        }
    
    # Scope 3 data - Business travel
    if 'business_travel_data' not in st.session_state:
        st.session_state.business_travel_data = {
            'Air Travel Short Haul (km)': 0.0,
            'Air Travel Medium Haul (km)': 0.0,
            'Air Travel Long Haul (km)': 0.0,
            'Train Travel (km)': 0.0,
            'Taxi Travel (km)': 0.0,
            'Bus Travel (km)': 0.0,
            'Hotel Stays (nights)': 0.0
        }
    
    # Scope 3 data - Employee commuting
    if 'employee_commuting_data' not in st.session_state:
        st.session_state.employee_commuting_data = {
            'Car (km)': 0.0,
            'Public Transport (km)': 0.0,
            'Walking/Cycling (km)': 0.0
        }
    
    # Scope 3 data - Waste
    if 'waste_data' not in st.session_state:
        st.session_state.waste_data = {
            'Landfill (kg)': 0.0,
            'Recycling (kg)': 0.0,
            'Composting (kg)': 0.0,
            'Incineration (kg)': 0.0
        }
    
    # Scope 3 data - Purchased goods and services
    if 'purchased_goods_data' not in st.session_state:
        st.session_state.purchased_goods_data = {
            'Paper Products (kg)': 0.0,
            'IT Equipment (units)': 0.0,
            'Food and Beverages ($)': 0.0,
            'Other Goods ($)': 0.0
        }
    
    # Calculated emissions data
    if 'scope1_emissions' not in st.session_state:
        st.session_state.scope1_emissions = None
    if 'scope2_emissions' not in st.session_state:
        st.session_state.scope2_emissions = None
    if 'scope3_emissions' not in st.session_state:
        st.session_state.scope3_emissions = None
    if 'total_emissions' not in st.session_state:
        st.session_state.total_emissions = None
    
    # Report data
    if 'report_generated' not in st.session_state:
        st.session_state.report_generated = False

def update_calculations():
    """Update all emissions calculations based on current session state data"""
    
    # Calculate Scope 1 emissions
    st.session_state.scope1_emissions = calculate_scope1_emissions(
        st.session_state.fuel_data,
        st.session_state.vehicle_data,
        st.session_state.refrigerant_data
    )
    
    # Calculate Scope 2 emissions
    st.session_state.scope2_emissions = calculate_scope2_emissions(
        st.session_state.electricity_data,
        st.session_state.district_energy_data
    )
    
    # Calculate Scope 3 emissions
    st.session_state.scope3_emissions = calculate_scope3_emissions(
        st.session_state.business_travel_data,
        st.session_state.employee_commuting_data,
        st.session_state.waste_data,
        st.session_state.purchased_goods_data
    )
    
    # Calculate total emissions
    st.session_state.total_emissions = calculate_total_emissions(
        st.session_state.scope1_emissions,
        st.session_state.scope2_emissions,
        st.session_state.scope3_emissions
    )

def format_number(number, precision=2):
    """Format number with thousand separators and specified precision"""
    if number is None:
        return "0.00"
    return f"{number:,.{precision}f}"

def validate_inputs(data_dict):
    """
    Validate all numeric inputs in the dictionary
    
    Parameters:
    -----------
    data_dict : dict
        Dictionary containing input data to validate
        
    Returns:
    --------
    bool
        True if all inputs are valid, False otherwise
    """
    for key, value in data_dict.items():
        if value < 0:
            return False
        
    return True

def get_emission_units():
    """Return the appropriate units for emissions"""
    return "tCO₂e"
