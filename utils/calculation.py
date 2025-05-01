import streamlit as st
import pandas as pd

# Emission factors (tCO2e per unit)
EMISSION_FACTORS = {
    # Scope 1
    'natural_gas': 0.00205,  # tCO2e per m3
    'diesel_stationary': 0.00270,  # tCO2e per liter
    'gasoline': 0.00233,  # tCO2e per liter
    'diesel_mobile': 0.00267,  # tCO2e per liter
    'refrigerant': {
        'R-410A': 2.088,  # GWP per kg
        'R-134a': 1.43,   # GWP per kg
        'R-404A': 3.922,  # GWP per kg
        'R-32': 0.675,    # GWP per kg
        'Other': 1.5      # Default GWP per kg
    },
    
    # Scope 2
    'electricity': {
        'Northeast': 0.000221,  # tCO2e per kWh
        'Southeast': 0.000389,  # tCO2e per kWh
        'Midwest': 0.000452,   # tCO2e per kWh
        'Southwest': 0.000386,  # tCO2e per kWh
        'West': 0.000279,       # tCO2e per kWh
        'Other': 0.000416       # US average, tCO2e per kWh
    },
    'purchased_steam': 0.00009,  # tCO2e per MJ
    'purchased_heat': 0.00007,   # tCO2e per MJ
    
    # Scope 3
    'air_travel_short': 0.000156,  # tCO2e per passenger-km
    'air_travel_long': 0.000139,   # tCO2e per passenger-km
    'hotel_stays': 0.0218,         # tCO2e per room-night
    'rental_car': 0.000175,        # tCO2e per km
    'car_commute': 0.000175,       # tCO2e per passenger-km
    'public_transit': 0.000067,    # tCO2e per passenger-km
    'landfill_waste': 0.000458,    # tCO2e per kg
    'recycled_waste': 0.000021,    # tCO2e per kg
    'paper_consumption': 0.00139,  # tCO2e per kg
    'water_consumption': 0.000344  # tCO2e per m3
}

def calculate_emissions():
    """
    Calculate emissions based on the activity data in session state
    and update session state with results.
    """
    # Initialize emissions data structure
    emissions_data = {
        'scope1': {},
        'scope2': {},
        'scope3': {}
    }
    
    # Calculate Scope 1 emissions
    
    # Natural gas
    if 'natural_gas' in st.session_state and st.session_state.natural_gas > 0:
        emissions_data['scope1']['natural_gas'] = st.session_state.natural_gas * EMISSION_FACTORS['natural_gas']
    
    # Stationary diesel
    if 'diesel_stationary' in st.session_state and st.session_state.diesel_stationary > 0:
        emissions_data['scope1']['diesel_stationary'] = st.session_state.diesel_stationary * EMISSION_FACTORS['diesel_stationary']
    
    # Gasoline
    if 'gasoline' in st.session_state and st.session_state.gasoline > 0:
        emissions_data['scope1']['gasoline'] = st.session_state.gasoline * EMISSION_FACTORS['gasoline']
    
    # Mobile diesel
    if 'diesel_mobile' in st.session_state and st.session_state.diesel_mobile > 0:
        emissions_data['scope1']['diesel_mobile'] = st.session_state.diesel_mobile * EMISSION_FACTORS['diesel_mobile']
    
    # Refrigerant
    if 'refrigerant_amount' in st.session_state and st.session_state.refrigerant_amount > 0:
        refrigerant_type = st.session_state.get('refrigerant_type', 'Other')
        emissions_data['scope1']['refrigerant'] = st.session_state.refrigerant_amount * EMISSION_FACTORS['refrigerant'].get(refrigerant_type, EMISSION_FACTORS['refrigerant']['Other'])
    
    # Calculate Scope 2 emissions
    
    # Electricity
    if 'electricity' in st.session_state and st.session_state.electricity > 0:
        grid_region = st.session_state.get('grid_region', 'Other')
        emissions_data['scope2']['electricity'] = st.session_state.electricity * EMISSION_FACTORS['electricity'].get(grid_region, EMISSION_FACTORS['electricity']['Other'])
    
    # Purchased steam
    if 'purchased_steam' in st.session_state and st.session_state.purchased_steam > 0:
        emissions_data['scope2']['purchased_steam'] = st.session_state.purchased_steam * EMISSION_FACTORS['purchased_steam']
    
    # Purchased heat
    if 'purchased_heat' in st.session_state and st.session_state.purchased_heat > 0:
        emissions_data['scope2']['purchased_heat'] = st.session_state.purchased_heat * EMISSION_FACTORS['purchased_heat']
    
    # Calculate Scope 3 emissions
    
    # Business Travel
    if 'air_travel_short' in st.session_state and st.session_state.air_travel_short > 0:
        emissions_data['scope3']['air_travel_short'] = st.session_state.air_travel_short * EMISSION_FACTORS['air_travel_short']
    
    if 'air_travel_long' in st.session_state and st.session_state.air_travel_long > 0:
        emissions_data['scope3']['air_travel_long'] = st.session_state.air_travel_long * EMISSION_FACTORS['air_travel_long']
    
    if 'hotel_stays' in st.session_state and st.session_state.hotel_stays > 0:
        emissions_data['scope3']['hotel_stays'] = st.session_state.hotel_stays * EMISSION_FACTORS['hotel_stays']
    
    if 'rental_car' in st.session_state and st.session_state.rental_car > 0:
        emissions_data['scope3']['rental_car'] = st.session_state.rental_car * EMISSION_FACTORS['rental_car']
    
    # Employee Commuting
    if 'car_commute' in st.session_state and st.session_state.car_commute > 0:
        emissions_data['scope3']['car_commute'] = st.session_state.car_commute * EMISSION_FACTORS['car_commute']
    
    if 'public_transit' in st.session_state and st.session_state.public_transit > 0:
        emissions_data['scope3']['public_transit'] = st.session_state.public_transit * EMISSION_FACTORS['public_transit']
    
    # Waste
    if 'landfill_waste' in st.session_state and st.session_state.landfill_waste > 0:
        emissions_data['scope3']['landfill_waste'] = st.session_state.landfill_waste * EMISSION_FACTORS['landfill_waste']
    
    if 'recycled_waste' in st.session_state and st.session_state.recycled_waste > 0:
        emissions_data['scope3']['recycled_waste'] = st.session_state.recycled_waste * EMISSION_FACTORS['recycled_waste']
    
    # Purchased Goods & Services
    if 'paper_consumption' in st.session_state and st.session_state.paper_consumption > 0:
        emissions_data['scope3']['paper_consumption'] = st.session_state.paper_consumption * EMISSION_FACTORS['paper_consumption']
    
    if 'water_consumption' in st.session_state and st.session_state.water_consumption > 0:
        emissions_data['scope3']['water_consumption'] = st.session_state.water_consumption * EMISSION_FACTORS['water_consumption']
    
    # Calculate totals
    scope1_total = sum(emissions_data['scope1'].values())
    scope2_total = sum(emissions_data['scope2'].values())
    scope3_total = sum(emissions_data['scope3'].values())
    total_emissions = scope1_total + scope2_total + scope3_total
    
    # Update session state with emissions data and totals
    st.session_state.emissions_data = emissions_data
    st.session_state.scope1_total = scope1_total
    st.session_state.scope2_total = scope2_total
    st.session_state.scope3_total = scope3_total
    st.session_state.total_emissions = total_emissions
    
    return emissions_data
