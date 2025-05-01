import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

def create_emissions_summary_chart():
    """
    Create a pie chart showing the distribution of emissions by scope.
    
    Returns:
        fig: Plotly figure object
    """
    # Create data for the pie chart
    labels = ['Scope 1', 'Scope 2', 'Scope 3']
    values = [
        st.session_state.scope1_total,
        st.session_state.scope2_total,
        st.session_state.scope3_total
    ]
    
    # Create the pie chart
    fig = px.pie(
        names=labels,
        values=values,
        title="Emissions by Scope",
        color=labels,
        color_discrete_map={
            'Scope 1': '#1e88e5',  # Blue
            'Scope 2': '#43a047',  # Green
            'Scope 3': '#fb8c00'   # Orange
        }
    )
    
    # Update layout
    fig.update_layout(
        legend_title="Scope",
        margin=dict(t=50, b=20, l=20, r=20)
    )
    
    # Add percentages to labels
    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        hovertemplate='%{label}<br>%{value:.2f} tCO₂e<br>%{percent}'
    )
    
    return fig

def create_scope_breakdown_chart(scope):
    """
    Create a pie chart showing the breakdown of emissions within a specific scope.
    
    Args:
        scope (str): The scope to visualize ('scope1', 'scope2', or 'scope3')
        
    Returns:
        fig: Plotly figure object
    """
    if not hasattr(st.session_state, 'emissions_data') or scope not in st.session_state.emissions_data:
        # Return empty figure if no data
        return go.Figure()
    
    # Get data for the selected scope
    scope_data = st.session_state.emissions_data[scope]
    
    if not scope_data:
        # Return empty figure if scope has no data
        return go.Figure()
    
    # Create data for the pie chart
    labels = [source.replace('_', ' ').title() for source in scope_data.keys()]
    values = list(scope_data.values())
    
    # Define a colorscale based on the scope
    if scope == 'scope1':
        colorscale = px.colors.sequential.Blues
    elif scope == 'scope2':
        colorscale = px.colors.sequential.Greens
    else:
        colorscale = px.colors.sequential.Oranges
    
    # Create the pie chart
    fig = px.pie(
        names=labels,
        values=values,
        title=f"{scope.title().replace('_', ' ')} Emissions Breakdown",
        color_discrete_sequence=colorscale
    )
    
    # Update layout
    fig.update_layout(
        legend_title="Emission Source",
        margin=dict(t=50, b=20, l=20, r=20)
    )
    
    # Add percentages to labels
    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        hovertemplate='%{label}<br>%{value:.2f} tCO₂e<br>%{percent}'
    )
    
    return fig

def create_emissions_by_category_chart():
    """
    Create a bar chart showing emissions by category across all scopes.
    
    Returns:
        fig: Plotly figure object
    """
    if not hasattr(st.session_state, 'emissions_data'):
        # Return empty figure if no data
        return go.Figure()
    
    # Prepare data for the chart
    categories = {
        'Stationary Combustion': ['natural_gas', 'diesel_stationary'],
        'Mobile Combustion': ['gasoline', 'diesel_mobile'],
        'Fugitive Emissions': ['refrigerant'],
        'Purchased Electricity': ['electricity'],
        'Purchased Energy': ['purchased_steam', 'purchased_heat'],
        'Business Travel': ['air_travel_short', 'air_travel_long', 'hotel_stays', 'rental_car'],
        'Employee Commuting': ['car_commute', 'public_transit'],
        'Waste': ['landfill_waste', 'recycled_waste'],
        'Purchased Goods & Services': ['paper_consumption', 'water_consumption']
    }
    
    # Map sources to scopes
    scope_mapping = {
        'natural_gas': 'Scope 1',
        'diesel_stationary': 'Scope 1',
        'gasoline': 'Scope 1',
        'diesel_mobile': 'Scope 1',
        'refrigerant': 'Scope 1',
        'electricity': 'Scope 2',
        'purchased_steam': 'Scope 2',
        'purchased_heat': 'Scope 2',
        'air_travel_short': 'Scope 3',
        'air_travel_long': 'Scope 3',
        'hotel_stays': 'Scope 3',
        'rental_car': 'Scope 3',
        'car_commute': 'Scope 3',
        'public_transit': 'Scope 3',
        'landfill_waste': 'Scope 3',
        'recycled_waste': 'Scope 3',
        'paper_consumption': 'Scope 3',
        'water_consumption': 'Scope 3'
    }
    
    # Calculate emissions by category
    chart_data = []
    for category, sources in categories.items():
        category_total = 0
        for source in sources:
            # Check each scope for the source
            for scope, data in st.session_state.emissions_data.items():
                if source in data:
                    category_total += data[source]
        
        if category_total > 0:
            # Determine which scope contributes most to this category
            scope_contributions = {'Scope 1': 0, 'Scope 2': 0, 'Scope 3': 0}
            for source in sources:
                for scope, data in st.session_state.emissions_data.items():
                    if source in data:
                        scope_contributions[scope_mapping[source]] += data[source]
            
            primary_scope = max(scope_contributions, key=scope_contributions.get)
            
            chart_data.append({
                'Category': category,
                'Emissions': category_total,
                'Primary Scope': primary_scope
            })
    
    # Sort data by emissions (descending)
    chart_data = sorted(chart_data, key=lambda x: x['Emissions'], reverse=True)
    
    # Create DataFrame for plotting
    df = pd.DataFrame(chart_data)
    
    if df.empty:
        # Return empty figure if no data after processing
        return go.Figure()
    
    # Create the bar chart
    fig = px.bar(
        df,
        x='Category',
        y='Emissions',
        color='Primary Scope',
        title='Emissions by Category',
        labels={'Emissions': 'Emissions (tCO₂e)'},
        color_discrete_map={
            'Scope 1': '#1e88e5',  # Blue
            'Scope 2': '#43a047',  # Green
            'Scope 3': '#fb8c00'   # Orange
        }
    )
    
    # Update layout
    fig.update_layout(
        xaxis_title="",
        yaxis_title="tCO₂e",
        legend_title="Primary Scope",
        margin=dict(t=50, b=50, l=20, r=20)
    )
    
    # Add data labels
    fig.update_traces(
        texttemplate='%{y:.2f}',
        textposition='outside'
    )
    
    return fig

def create_scope3_breakdown_chart():
    """
    Create a breakdown chart for Scope 3 emissions by category.
    
    Returns:
        fig: Plotly figure object
    """
    if not hasattr(st.session_state, 'emissions_data') or 'scope3' not in st.session_state.emissions_data:
        # Return empty figure if no data
        return go.Figure()
    
    scope3_data = st.session_state.emissions_data['scope3']
    
    if not scope3_data:
        # Return empty figure if scope3 has no data
        return go.Figure()
    
    # Group Scope 3 emissions by category
    categories = {
        'Business Travel': ['air_travel_short', 'air_travel_long', 'hotel_stays', 'rental_car'],
        'Employee Commuting': ['car_commute', 'public_transit'],
        'Waste': ['landfill_waste', 'recycled_waste'],
        'Purchased Goods & Services': ['paper_consumption', 'water_consumption']
    }
    
    # Calculate totals by category
    category_totals = {}
    for category, sources in categories.items():
        category_total = sum(scope3_data.get(source, 0) for source in sources)
        if category_total > 0:
            category_totals[category] = category_total
    
    if not category_totals:
        # Return empty figure if no data after processing
        return go.Figure()
    
    # Create data for the chart
    labels = list(category_totals.keys())
    values = list(category_totals.values())
    
    # Create the pie chart
    fig = px.pie(
        names=labels,
        values=values,
        title="Scope 3 Emissions by Category",
        color_discrete_sequence=px.colors.sequential.Oranges
    )
    
    # Update layout
    fig.update_layout(
        legend_title="Category",
        margin=dict(t=50, b=20, l=20, r=20)
    )
    
    # Add percentages to labels
    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        hovertemplate='%{label}<br>%{value:.2f} tCO₂e<br>%{percent}'
    )
    
    return fig
