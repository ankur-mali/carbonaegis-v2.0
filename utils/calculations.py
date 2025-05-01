import pandas as pd
import numpy as np
from data.emission_factors import (
    electricity_factors, fuel_factors, vehicle_factors, 
    refrigerant_factors, waste_factors, business_travel_factors,
    employee_commuting_factors, purchased_goods_factors
)

def calculate_scope1_emissions(fuel_data, vehicle_data, refrigerant_data):
    """
    Calculate Scope 1 emissions (direct emissions from owned or controlled sources)
    
    Parameters:
    -----------
    fuel_data : dict
        Dictionary containing stationary combustion data
    vehicle_data : dict
        Dictionary containing company vehicle data
    refrigerant_data : dict
        Dictionary containing refrigerant leakage data
        
    Returns:
    --------
    dict
        Dictionary with calculated emissions and breakdown
    """
    emissions = {}
    total_scope1 = 0
    
    # Stationary combustion
    stationary_emissions = 0
    fuel_breakdown = {}
    
    for fuel_type, quantity in fuel_data.items():
        if quantity > 0 and fuel_type in fuel_factors:
            emission = quantity * fuel_factors[fuel_type]['factor']
            fuel_breakdown[fuel_type] = emission
            stationary_emissions += emission
    
    # Mobile combustion (company vehicles)
    vehicle_emissions = 0
    vehicle_breakdown = {}
    
    for vehicle_type, distance in vehicle_data.items():
        if distance > 0 and vehicle_type in vehicle_factors:
            emission = distance * vehicle_factors[vehicle_type]['factor']
            vehicle_breakdown[vehicle_type] = emission
            vehicle_emissions += emission
    
    # Refrigerant leakage
    refrigerant_emissions = 0
    refrigerant_breakdown = {}
    
    for refrigerant_type, quantity in refrigerant_data.items():
        if quantity > 0 and refrigerant_type in refrigerant_factors:
            emission = quantity * refrigerant_factors[refrigerant_type]['factor']
            refrigerant_breakdown[refrigerant_type] = emission
            refrigerant_emissions += emission
    
    # Total Scope 1
    total_scope1 = stationary_emissions + vehicle_emissions + refrigerant_emissions
    
    emissions = {
        'total': total_scope1,
        'stationary_combustion': {
            'total': stationary_emissions,
            'breakdown': fuel_breakdown
        },
        'mobile_combustion': {
            'total': vehicle_emissions,
            'breakdown': vehicle_breakdown
        },
        'refrigerants': {
            'total': refrigerant_emissions,
            'breakdown': refrigerant_breakdown
        }
    }
    
    return emissions

def calculate_scope2_emissions(electricity_data, district_energy_data):
    """
    Calculate Scope 2 emissions (indirect emissions from purchased electricity, steam, heating, and cooling)
    
    Parameters:
    -----------
    electricity_data : dict
        Dictionary containing electricity consumption data
    district_energy_data : dict
        Dictionary containing district energy consumption data
        
    Returns:
    --------
    dict
        Dictionary with calculated emissions and breakdown
    """
    emissions = {}
    total_scope2 = 0
    
    # Electricity
    electricity_emissions = 0
    electricity_breakdown = {}
    
    for location, consumption in electricity_data.items():
        if consumption > 0 and location in electricity_factors:
            emission = consumption * electricity_factors[location]['factor']
            electricity_breakdown[location] = emission
            electricity_emissions += emission
    
    # District energy
    district_energy_emissions = sum(district_energy_data.values())
    
    # Total Scope 2
    total_scope2 = electricity_emissions + district_energy_emissions
    
    emissions = {
        'total': total_scope2,
        'electricity': {
            'total': electricity_emissions,
            'breakdown': electricity_breakdown
        },
        'district_energy': {
            'total': district_energy_emissions
        }
    }
    
    return emissions

def calculate_scope3_emissions(
    business_travel_data, employee_commuting_data, waste_data, purchased_goods_data
):
    """
    Calculate Scope 3 emissions (all other indirect emissions in a company's value chain)
    
    Parameters:
    -----------
    business_travel_data : dict
        Dictionary containing business travel data
    employee_commuting_data : dict
        Dictionary containing employee commuting data
    waste_data : dict
        Dictionary containing waste disposal data
    purchased_goods_data : dict
        Dictionary containing purchased goods and services data
        
    Returns:
    --------
    dict
        Dictionary with calculated emissions and breakdown
    """
    emissions = {}
    total_scope3 = 0
    
    # Business travel
    business_travel_emissions = 0
    business_travel_breakdown = {}
    
    for travel_type, distance in business_travel_data.items():
        if distance > 0 and travel_type in business_travel_factors:
            emission = distance * business_travel_factors[travel_type]['factor']
            business_travel_breakdown[travel_type] = emission
            business_travel_emissions += emission
    
    # Employee commuting
    employee_commuting_emissions = 0
    employee_commuting_breakdown = {}
    
    for transport_mode, distance in employee_commuting_data.items():
        if distance > 0 and transport_mode in employee_commuting_factors:
            emission = distance * employee_commuting_factors[transport_mode]['factor']
            employee_commuting_breakdown[transport_mode] = emission
            employee_commuting_emissions += emission
    
    # Waste disposal
    waste_emissions = 0
    waste_breakdown = {}
    
    for waste_type, quantity in waste_data.items():
        if quantity > 0 and waste_type in waste_factors:
            emission = quantity * waste_factors[waste_type]['factor']
            waste_breakdown[waste_type] = emission
            waste_emissions += emission
    
    # Purchased goods and services
    purchased_goods_emissions = 0
    purchased_goods_breakdown = {}
    
    for goods_type, amount in purchased_goods_data.items():
        if amount > 0 and goods_type in purchased_goods_factors:
            emission = amount * purchased_goods_factors[goods_type]['factor']
            purchased_goods_breakdown[goods_type] = emission
            purchased_goods_emissions += emission
    
    # Total Scope 3
    total_scope3 = (
        business_travel_emissions + 
        employee_commuting_emissions + 
        waste_emissions + 
        purchased_goods_emissions
    )
    
    emissions = {
        'total': total_scope3,
        'business_travel': {
            'total': business_travel_emissions,
            'breakdown': business_travel_breakdown
        },
        'employee_commuting': {
            'total': employee_commuting_emissions,
            'breakdown': employee_commuting_breakdown
        },
        'waste': {
            'total': waste_emissions,
            'breakdown': waste_breakdown
        },
        'purchased_goods': {
            'total': purchased_goods_emissions,
            'breakdown': purchased_goods_breakdown
        }
    }
    
    return emissions

def calculate_total_emissions(scope1, scope2, scope3):
    """
    Calculate total emissions across all scopes
    
    Parameters:
    -----------
    scope1 : dict
        Dictionary containing Scope 1 emissions
    scope2 : dict
        Dictionary containing Scope 2 emissions
    scope3 : dict
        Dictionary containing Scope 3 emissions
        
    Returns:
    --------
    float
        Total emissions across all scopes
    """
    return scope1['total'] + scope2['total'] + scope3['total']

def get_emissions_by_category(scope1, scope2, scope3):
    """
    Get emissions breakdown by category for visualization
    
    Parameters:
    -----------
    scope1 : dict
        Dictionary containing Scope 1 emissions
    scope2 : dict
        Dictionary containing Scope 2 emissions
    scope3 : dict
        Dictionary containing Scope 3 emissions
        
    Returns:
    --------
    dict
        Dictionary with emissions by category
    """
    categories = {}
    
    # Scope 1 categories
    categories['Stationary Combustion'] = scope1['stationary_combustion']['total']
    categories['Mobile Combustion'] = scope1['mobile_combustion']['total']
    categories['Refrigerant Leakage'] = scope1['refrigerants']['total']
    
    # Scope 2 categories
    categories['Electricity'] = scope2['electricity']['total']
    categories['District Energy'] = scope2['district_energy']['total']
    
    # Scope 3 categories
    categories['Business Travel'] = scope3['business_travel']['total']
    categories['Employee Commuting'] = scope3['employee_commuting']['total']
    categories['Waste Disposal'] = scope3['waste']['total']
    categories['Purchased Goods & Services'] = scope3['purchased_goods']['total']
    
    return categories

def get_emissions_by_scope(scope1, scope2, scope3):
    """
    Get emissions breakdown by scope for visualization
    
    Parameters:
    -----------
    scope1 : dict
        Dictionary containing Scope 1 emissions
    scope2 : dict
        Dictionary containing Scope 2 emissions
    scope3 : dict
        Dictionary containing Scope 3 emissions
        
    Returns:
    --------
    dict
        Dictionary with emissions by scope
    """
    return {
        'Scope 1': scope1['total'],
        'Scope 2': scope2['total'],
        'Scope 3': scope3['total']
    }
