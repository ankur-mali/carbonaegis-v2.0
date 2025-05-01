import streamlit as st
import json
from datetime import datetime
from utils.database import save_emission_data, get_emission_data, get_all_emission_data

def init_session_state():
    """
    Initialize session state variables if they don't exist.
    """
    # Check if we need to initialize
    if 'initialized' not in st.session_state:
        # Settings variables
        if 'time_period' not in st.session_state:
            st.session_state.time_period = 'Annually'
        if 'calculation_method' not in st.session_state:
            st.session_state.calculation_method = 'Exact (measured data)'
        if 'distance_unit' not in st.session_state:
            st.session_state.distance_unit = 'Kilometers'
        if 'volume_unit' not in st.session_state:
            st.session_state.volume_unit = 'Liters'
            
        # Transportation variables
        if 'fuel_type' not in st.session_state:
            st.session_state.fuel_type = 'Petrol/Gasoline'
        if 'fuel_unit' not in st.session_state:
            st.session_state.fuel_unit = 'Liters'
        if 'fuel_amount' not in st.session_state:
            st.session_state.fuel_amount = 0.0
        if 'vehicle_type' not in st.session_state:
            st.session_state.vehicle_type = 'Car (Petrol/Gasoline)'
        if 'distance_unit_vehicle' not in st.session_state:
            st.session_state.distance_unit_vehicle = 'Kilometers'
        if 'vehicle_distance' not in st.session_state:
            st.session_state.vehicle_distance = 0.0
        if 'flight_type' not in st.session_state:
            st.session_state.flight_type = 'Short-haul (<1,500 km)'
        if 'flight_class' not in st.session_state:
            st.session_state.flight_class = 'Economy'
        if 'flight_distance' not in st.session_state:
            st.session_state.flight_distance = 0.0
        if 'num_passengers' not in st.session_state:
            st.session_state.num_passengers = 1
        if 'transport_type' not in st.session_state:
            st.session_state.transport_type = 'Bus'
        if 'transport_distance_unit' not in st.session_state:
            st.session_state.transport_distance_unit = 'Kilometers'
        if 'transport_distance' not in st.session_state:
            st.session_state.transport_distance = 0.0
        if 'zero_emission_type' not in st.session_state:
            st.session_state.zero_emission_type = 'Walking'
        if 'zero_emission_distance' not in st.session_state:
            st.session_state.zero_emission_distance = 0.0
            
        # Energy variables
        if 'electricity' not in st.session_state:
            st.session_state.electricity = 0.0
        if 'electricity_unit' not in st.session_state:
            st.session_state.electricity_unit = 'kWh'
        if 'grid_region' not in st.session_state:
            st.session_state.grid_region = 'Northeast'
        if 'renewable_percentage' not in st.session_state:
            st.session_state.renewable_percentage = 0
        if 'heating_type' not in st.session_state:
            st.session_state.heating_type = 'Natural Gas'
        if 'heating_unit' not in st.session_state:
            st.session_state.heating_unit = 'kWh'
        if 'heating_amount' not in st.session_state:
            st.session_state.heating_amount = 0.0
            
        # Other sources variables
        if 'waste_type' not in st.session_state:
            st.session_state.waste_type = 'Landfill (Mixed)'
        if 'waste_amount' not in st.session_state:
            st.session_state.waste_amount = 0.0
        if 'water_type' not in st.session_state:
            st.session_state.water_type = 'Municipal Supply'
        if 'water_amount' not in st.session_state:
            st.session_state.water_amount = 0.0
        if 'material_type' not in st.session_state:
            st.session_state.material_type = 'Paper'
        if 'material_amount' not in st.session_state:
            st.session_state.material_amount = 0.0
        if 'refrigerant_type' not in st.session_state:
            st.session_state.refrigerant_type = 'R-410A'
        if 'refrigerant_amount' not in st.session_state:
            st.session_state.refrigerant_amount = 0.0
            
        # Legacy variables - maintained for compatibility
        if 'natural_gas' not in st.session_state:
            st.session_state.natural_gas = 0.0
        if 'diesel_stationary' not in st.session_state:
            st.session_state.diesel_stationary = 0.0
        if 'gasoline' not in st.session_state:
            st.session_state.gasoline = 0.0
        if 'diesel_mobile' not in st.session_state:
            st.session_state.diesel_mobile = 0.0
        if 'purchased_steam' not in st.session_state:
            st.session_state.purchased_steam = 0.0
        if 'purchased_heat' not in st.session_state:
            st.session_state.purchased_heat = 0.0
        if 'air_travel_short' not in st.session_state:
            st.session_state.air_travel_short = 0.0
        if 'air_travel_long' not in st.session_state:
            st.session_state.air_travel_long = 0.0
        if 'hotel_stays' not in st.session_state:
            st.session_state.hotel_stays = 0.0
        if 'rental_car' not in st.session_state:
            st.session_state.rental_car = 0.0
        if 'car_commute' not in st.session_state:
            st.session_state.car_commute = 0.0
        if 'public_transit' not in st.session_state:
            st.session_state.public_transit = 0.0
        if 'landfill_waste' not in st.session_state:
            st.session_state.landfill_waste = 0.0
        if 'recycled_waste' not in st.session_state:
            st.session_state.recycled_waste = 0.0
        if 'paper_consumption' not in st.session_state:
            st.session_state.paper_consumption = 0.0
        if 'water_consumption' not in st.session_state:
            st.session_state.water_consumption = 0.0
        
        # Results variables
        if 'emissions_data' not in st.session_state:
            st.session_state.emissions_data = {
                'scope1': {},
                'scope2': {},
                'scope3': {}
            }
        if 'scope1_total' not in st.session_state:
            st.session_state.scope1_total = 0.0
        if 'scope2_total' not in st.session_state:
            st.session_state.scope2_total = 0.0
        if 'scope3_total' not in st.session_state:
            st.session_state.scope3_total = 0.0
        if 'total_emissions' not in st.session_state:
            st.session_state.total_emissions = 0.0
        
        # State tracking variables
        if 'has_data' not in st.session_state:
            st.session_state.has_data = False
        
        # Framework Finder variables
        if 'framework_finder_step' not in st.session_state:
            st.session_state.framework_finder_step = 1
        if 'framework_size' not in st.session_state:
            st.session_state.framework_size = "Medium"
        if 'framework_listed' not in st.session_state:
            st.session_state.framework_listed = False
        if 'framework_turnover' not in st.session_state:
            st.session_state.framework_turnover = 1000000
        if 'framework_employees' not in st.session_state:
            st.session_state.framework_employees = 50
        if 'framework_sector' not in st.session_state:
            st.session_state.framework_sector = "Manufacturing"
        if 'framework_country' not in st.session_state:
            st.session_state.framework_country = "Germany"
        if 'framework_recommendations' not in st.session_state:
            st.session_state.framework_recommendations = None
            
        # ESG Dashboard variables
        if 'annual_revenue' not in st.session_state:
            st.session_state.annual_revenue = 0
        if 'currency' not in st.session_state:
            st.session_state.currency = "EUR (€)"
        if 'target_year' not in st.session_state:
            st.session_state.target_year = 2030
        if 'reduction_target' not in st.session_state:
            st.session_state.reduction_target = 30
        
        # Mark as initialized
        st.session_state.initialized = True

def save_input_data(input_data, save_to_db=True, organization_name=None, report_year=None):
    """
    Save input data to session state and optionally to the database.
    
    Args:
        input_data (dict): Dictionary containing input data
        save_to_db (bool, optional): Whether to save the data to the database
        organization_name (str, optional): Organization name for the report
        report_year (int, optional): Year for the report
        
    Returns:
        int or None: ID of the database record if saved to database, None otherwise
    """
    # Save to session state
    for key, value in input_data.items():
        st.session_state[key] = value
    
    # Save to database if requested
    if save_to_db:
        try:
            # Check if we have calculated emissions data
            if st.session_state.get('has_data'):
                # Create a copy of the input data for database storage
                db_data = input_data.copy()
                
                # Add emissions results to the data
                db_data['emissions_data'] = st.session_state.get('emissions_data', {})
                db_data['scope1_total'] = st.session_state.get('scope1_total', 0.0)
                db_data['scope2_total'] = st.session_state.get('scope2_total', 0.0)
                db_data['scope3_total'] = st.session_state.get('scope3_total', 0.0)
                db_data['total_emissions'] = st.session_state.get('total_emissions', 0.0)
                
                # Save to database
                record_id = save_emission_data(db_data, organization_name, report_year)
                
                # Store the record ID in session state for future reference
                st.session_state.current_record_id = record_id
                
                return record_id
        except Exception as e:
            st.error(f"Failed to save data to database: {str(e)}")
    
    return None

def load_emission_data(record_id):
    """
    Load emission data from the database into session state.
    
    Args:
        record_id (int): ID of the record to load
        
    Returns:
        bool: True if data was loaded successfully, False otherwise
    """
    try:
        db_data = get_emission_data(record_id)
        
        if not db_data:
            st.error(f"No data found with ID {record_id}")
            return False
        
        # Load input data into session state
        input_data = db_data.get('input_data', {})
        for key, value in input_data.items():
            # Skip emissions_data as it's stored separately
            if key not in ['emissions_data', 'scope1_total', 'scope2_total', 
                          'scope3_total', 'total_emissions']:
                st.session_state[key] = value
        
        # Load emissions results into session state
        if 'emissions_data' in input_data:
            st.session_state.emissions_data = input_data.get('emissions_data', {})
        
        # Update emission totals
        st.session_state.scope1_total = input_data.get('scope1_total', 0.0)
        st.session_state.scope2_total = input_data.get('scope2_total', 0.0)
        st.session_state.scope3_total = input_data.get('scope3_total', 0.0)
        st.session_state.total_emissions = input_data.get('total_emissions', 0.0)
        
        # Update state tracking
        st.session_state.has_data = True
        st.session_state.current_record_id = record_id
        
        return True
    except Exception as e:
        st.error(f"Failed to load data from database: {str(e)}")
        return False

def get_saved_calculations():
    """
    Get a list of all saved emission calculations from the database.
    
    Returns:
        list: List of dictionaries containing emission data records
    """
    try:
        return get_all_emission_data()
    except Exception as e:
        st.error(f"Failed to retrieve saved calculations: {str(e)}")
        return []

def clear_data():
    """
    Clear all data from session state.
    """
    # Reset all numeric input variables
    for key in [
        # Transportation
        'fuel_amount', 'vehicle_distance', 'flight_distance', 
        'transport_distance', 'zero_emission_distance',
        
        # Energy
        'electricity', 'heating_amount', 'renewable_percentage',
        
        # Other sources
        'waste_amount', 'water_amount', 'material_amount', 'refrigerant_amount',
        
        # Legacy variables
        'natural_gas', 'diesel_stationary', 'gasoline', 'diesel_mobile',
        'purchased_steam', 'purchased_heat', 'air_travel_short', 'air_travel_long', 
        'hotel_stays', 'rental_car', 'car_commute', 'public_transit', 
        'landfill_waste', 'recycled_waste', 'paper_consumption', 'water_consumption'
    ]:
        st.session_state[key] = 0.0
    
    # Reset integer inputs
    if 'num_passengers' in st.session_state:
        st.session_state.num_passengers = 1
    
    # Reset results
    st.session_state.emissions_data = {
        'scope1': {},
        'scope2': {},
        'scope3': {}
    }
    st.session_state.scope1_total = 0.0
    st.session_state.scope2_total = 0.0
    st.session_state.scope3_total = 0.0
    st.session_state.total_emissions = 0.0
    
    # Update state tracking
    st.session_state.has_data = False
