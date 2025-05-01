import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import sys

# Add parent directory to path to import utils
sys.path.append('..')

# Page configuration
st.set_page_config(
    page_title="Dashboard | Carbon Aegis",
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
    .metric-card {
        text-align: center;
        padding: 1.5rem;
        border-radius: 4px;
        background: #f4f4f4;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
        color: #0f62fe;
    }
    .metric-label {
        font-size: 1rem;
        color: #525252;
    }
    .chart-card {
        padding: 1.5rem;
        border-radius: 4px;
        background: #ffffff;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        margin-bottom: 1.5rem;
    }
    .chart-title {
        font-size: 1.2rem;
        font-weight: 600;
        margin-bottom: 1rem;
        color: #161616;
    }
    .scope-1 {
        color: #0f62fe;
    }
    .scope-2 {
        color: #6929c4;
    }
    .scope-3 {
        color: #1192e8;
    }
    .logo-container {
        margin-bottom: 2rem;
    }
    .logo-container img {
        max-height: 60px;
    }
    </style>
    """, unsafe_allow_html=True)

# Initialize session state
def init_session_state():
    if 'processed_data' not in st.session_state:
        st.session_state.processed_data = None
        
    # Generate sample data if testing/development
    if st.session_state.processed_data is None and 'testing' in st.session_state and st.session_state.testing:
        generate_sample_data()

# Format number with thousand separators
def format_number(number, precision=2):
    """Format number with thousand separators and specified precision"""
    if isinstance(number, (int, float)):
        return f"{number:,.{precision}f}"
    return number

# Return the appropriate units for emissions
def get_emission_units():
    """Return the appropriate units for emissions"""
    if 'emission_unit' in st.session_state:
        return st.session_state.emission_unit
    return "kg CO₂e"  # Default

# Generate sample data for development/testing
def generate_sample_data():
    """Generate sample data for development/testing"""
    # Sample emissions by scope
    by_scope = {
        'Scope 1': 125000,
        'Scope 2': 240000,
        'Scope 3': 580000
    }
    
    # Sample emissions by category
    by_category = {
        'electricity': 220000,
        'stationary_combustion': 85000,
        'mobile_combustion': 40000,
        'business_travel': 180000,
        'employee_commuting': 95000,
        'purchased_goods': 280000,
        'waste': 25000
    }
    
    # Sample line items
    line_items_data = []
    
    # Electricity (Scope 2)
    for month in range(1, 13):
        date_str = f"2024-{month:02d}-01"
        line_items_data.append({
            'scope': 'Scope 2',
            'category': 'electricity',
            'description': 'Electricity consumption',
            'amount': 25000 + 10000 * (month % 3),  # Seasonal variation
            'emission_factor': 0.45,
            'emissions': (25000 + 10000 * (month % 3)) * 0.45,
            'date': date_str
        })
    
    # Stationary combustion (Scope 1)
    for quarter in range(1, 5):
        month = quarter * 3
        date_str = f"2024-{month:02d}-01"
        line_items_data.append({
            'scope': 'Scope 1',
            'category': 'stationary_combustion',
            'description': 'Natural gas consumption',
            'amount': 20000 - 5000 * (quarter % 2),  # Seasonal variation
            'emission_factor': 0.18,
            'emissions': (20000 - 5000 * (quarter % 2)) * 0.18,
            'date': date_str
        })
    
    # Business travel (Scope 3)
    for month in range(1, 13):
        date_str = f"2024-{month:02d}-15"
        line_items_data.append({
            'scope': 'Scope 3',
            'category': 'business_travel',
            'description': 'Air travel',
            'amount': 15000 + 5000 * ((month + 1) % 4),
            'emission_factor': 0.15,
            'emissions': (15000 + 5000 * ((month + 1) % 4)) * 0.15,
            'date': date_str
        })
    
    # Set sample data
    total = sum(by_scope.values())
    st.session_state.processed_data = {
        'total': total,
        'by_scope': by_scope,
        'by_category': by_category,
        'line_items': pd.DataFrame(line_items_data)
    }

# Main dashboard function
def main():
    add_custom_css()
    init_session_state()
    
    # Display logo
    st.image("assets/logo.png", width=180)
    
    st.title("Emissions Dashboard")
    
    # Check if data is available
    if st.session_state.processed_data is None:
        st.warning("No emissions data available. Please import data first.")
        if st.button("Go to Data Import"):
            st.switch_page("pages/1_Data_Input.py")
        return
    
    # Get data from session state
    data = st.session_state.processed_data
    total_emissions = data['total']
    by_scope = data['by_scope']
    by_category = data['by_category']
    line_items = data['line_items'] if 'line_items' in data else pd.DataFrame()
    
    # Dashboard filters
    with st.expander("Dashboard Filters", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            # Date range filter (if dates are available in line items)
            if 'line_items' in data and 'date' in line_items.columns and not line_items['date'].isna().all():
                # Convert string dates to datetime if needed
                if line_items['date'].dtype == 'object':
                    line_items['date'] = pd.to_datetime(line_items['date'], errors='coerce')
                
                min_date = line_items['date'].min().date()
                max_date = line_items['date'].max().date()
                
                date_range = st.date_input(
                    "Filter by Date Range",
                    value=(min_date, max_date),
                    min_value=min_date,
                    max_value=max_date
                )
                
                if len(date_range) == 2:
                    start_date, end_date = date_range
                    line_items = line_items[(line_items['date'] >= pd.Timestamp(start_date)) & 
                                          (line_items['date'] <= pd.Timestamp(end_date))]
        
        with col2:
            # Scope filter
            available_scopes = list(by_scope.keys())
            selected_scopes = st.multiselect(
                "Filter by Scope",
                options=available_scopes,
                default=available_scopes
            )
            
            if selected_scopes and len(selected_scopes) < len(available_scopes):
                # Filter line items by selected scopes
                if not line_items.empty and 'scope' in line_items.columns:
                    line_items = line_items[line_items['scope'].isin(selected_scopes)]
                
                # Recalculate scope and category totals based on filtered line items
                filtered_by_scope = {scope: value for scope, value in by_scope.items() if scope in selected_scopes}
                by_scope = filtered_by_scope
    
    # Overview metrics row
    st.markdown("## Overview")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{format_number(total_emissions)}</div>
            <div class="metric-label">Total Emissions ({get_emission_units()})</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # Calculate intensity or per-employee average if available
        intensity_value = total_emissions / 100  # Placeholder calculation
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{format_number(intensity_value)}</div>
            <div class="metric-label">Emissions Intensity ({get_emission_units()} per unit)</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        # Get scope 3 percentage
        scope3_value = by_scope.get('Scope 3', 0)
        scope3_pct = (scope3_value / total_emissions * 100) if total_emissions > 0 else 0
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{format_number(scope3_pct)}%</div>
            <div class="metric-label">Scope 3 Percentage</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Scope breakdown and category breakdown
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="chart-card">
            <div class="chart-title">Emissions by Scope</div>
        """, unsafe_allow_html=True)
        
        # Create scope data
        scope_data = pd.DataFrame({
            'Scope': list(by_scope.keys()),
            'Emissions': list(by_scope.values())
        })
        
        # Create pie chart
        fig_scope = px.pie(
            scope_data,
            values='Emissions',
            names='Scope',
            color='Scope',
            color_discrete_map={
                'Scope 1': '#0f62fe',
                'Scope 2': '#6929c4',
                'Scope 3': '#1192e8'
            },
            hole=0.4
        )
        
        fig_scope.update_layout(
            margin=dict(t=0, b=0, l=0, r=0),
            legend=dict(orientation='h', yanchor='bottom', y=-0.2)
        )
        
        st.plotly_chart(fig_scope, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Scope breakdown details
        st.markdown("""
        <div class="chart-card">
            <div class="chart-title">Scope Details</div>
        """, unsafe_allow_html=True)
        
        for scope, value in by_scope.items():
            scope_class = scope.lower().replace(' ', '-')
            percentage = (value / total_emissions * 100) if total_emissions > 0 else 0
            st.markdown(f"""
            <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                <div class="{scope_class}">{scope}</div>
                <div>{format_number(value)} {get_emission_units()} ({format_number(percentage)}%)</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="chart-card">
            <div class="chart-title">Emissions by Category</div>
        """, unsafe_allow_html=True)
        
        # Create category data
        if by_category:
            category_data = pd.DataFrame({
                'Category': [cat.replace('_', ' ').title() for cat in by_category.keys()],
                'Emissions': list(by_category.values())
            })
            
            category_data = category_data.sort_values('Emissions', ascending=False)
            
            fig_category = px.bar(
                category_data,
                x='Category',
                y='Emissions',
                color='Emissions',
                color_continuous_scale='Blues'
            )
            
            fig_category.update_layout(
                margin=dict(t=0, b=0, l=0, r=0),
                xaxis_title="",
                yaxis_title=f"Emissions ({get_emission_units()})"
            )
            
            st.plotly_chart(fig_category, use_container_width=True)
        else:
            st.info("No category data available.")
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Emissions over time (if date data is available)
    if not line_items.empty and 'date' in line_items.columns and not line_items['date'].isna().all():
        st.markdown("""
        <div class="chart-card">
            <div class="chart-title">Emissions Over Time</div>
        """, unsafe_allow_html=True)
        
        # Group by date and scope
        if 'date' in line_items.columns and 'scope' in line_items.columns and 'emissions' in line_items.columns:
            # Make sure date is datetime type
            if line_items['date'].dtype == 'object':
                line_items['date'] = pd.to_datetime(line_items['date'])
            
            # Group by month and scope
            line_items['month'] = line_items['date'].dt.to_period('M').astype(str)
            timeline_data = line_items.groupby(['month', 'scope'])['emissions'].sum().reset_index()
            
            fig_timeline = px.line(
                timeline_data,
                x='month',
                y='emissions',
                color='scope',
                markers=True,
                color_discrete_map={
                    'Scope 1': '#0f62fe',
                    'Scope 2': '#6929c4',
                    'Scope 3': '#1192e8'
                }
            )
            
            fig_timeline.update_layout(
                margin=dict(t=0, b=0, l=0, r=0),
                xaxis_title="",
                yaxis_title=f"Emissions ({get_emission_units()})",
                legend_title="Scope"
            )
            
            st.plotly_chart(fig_timeline, use_container_width=True)
        else:
            st.info("Insufficient data for timeline chart.")
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Detailed line items table
    st.markdown("## Detailed Line Items")
    
    if not line_items.empty:
        # Format emissions values
        if 'emissions' in line_items.columns:
            line_items['emissions'] = line_items['emissions'].apply(lambda x: format_number(x))
        
        # Format date column if available
        if 'date' in line_items.columns:
            if line_items['date'].dtype != 'object':
                line_items['date'] = line_items['date'].dt.strftime('%Y-%m-%d')
        
        # Reorder columns for better display
        column_order = ['scope', 'category', 'description', 'amount', 'emission_factor', 'emissions', 'date']
        available_columns = [col for col in column_order if col in line_items.columns]
        
        # Add any remaining columns not in the ordered list
        for col in line_items.columns:
            if col not in available_columns:
                available_columns.append(col)
        
        st.dataframe(line_items[available_columns], use_container_width=True)
    else:
        st.info("No detailed line items available.")
    
    # Export options
    st.markdown("## Export Data")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Export to Excel"):
            # In a real implementation, this would generate the file
            st.success("Excel export functionality would be implemented here.")
    
    with col2:
        if st.button("Generate PDF Report"):
            # In a real implementation, this would generate the PDF
            st.success("PDF report functionality would be implemented here.")

if __name__ == "__main__":
    main()