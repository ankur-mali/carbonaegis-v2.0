import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.data_manager import init_session_state

# Define formatting functions here to avoid import errors
def format_number(number, precision=2):
    """Format number with thousand separators and specified precision"""
    if isinstance(number, (int, float)):
        return f"{number:,.{precision}f}"
    return str(number)

def get_emission_units():
    """Return the appropriate units for emissions"""
    return "tCO₂e"

# Initialize session state
init_session_state()

# Add Carbon Aegis branding
col1, col2 = st.columns([1, 5])
with col1:
    st.image("assets/logo.png", width=100)
with col2:
    st.title("Carbon Aegis - ESG Overview Dashboard")

st.markdown("""
This dashboard provides a comprehensive overview of your organization's ESG performance, 
with a focus on greenhouse gas emissions and sustainability metrics.
""")

# Check if there's emission data to display
if not st.session_state.get('has_data', False):
    st.warning("No emissions data available. Please enter your activity data in the Data Input page.")
    st.markdown("""
    To view this dashboard with your organization's data:
    1. Go to the Data Input page
    2. Enter your activity data
    3. Return to this dashboard
    """)
    
    if st.button("Go to Data Input", use_container_width=True):
        st.switch_page("pages/1_Data_Input.py")
else:
    # --- DASHBOARD LAYOUT --- #
    # Get emission data from session state
    scope1_total = st.session_state.get('scope1_total', 0.0)
    scope2_total = st.session_state.get('scope2_total', 0.0)
    scope3_total = st.session_state.get('scope3_total', 0.0)
    total_emissions = st.session_state.get('total_emissions', 0.0)
    
    # Get organization info if available
    org_name = st.session_state.get('organization_name', 'Your Organization')
    reporting_year = st.session_state.get('report_year', 2025)
    
    # Calculate emission intensity if revenue is available
    annual_revenue = st.session_state.get('annual_revenue', 0) 
    
    # Allow user to enter revenue if not already set
    if annual_revenue == 0:
        st.markdown("### Organization Revenue")
        st.markdown("Enter your organization's annual revenue to calculate emission intensity metrics.")
        col1, col2 = st.columns(2)
        with col1:
            currency = st.selectbox("Currency", ["EUR (€)", "USD ($)", "GBP (£)"], index=0)
        with col2:
            annual_revenue = st.number_input(
                "Annual Revenue (in millions)",
                min_value=0.0,
                value=10.0,
                step=1.0
            ) * 1000000  # Convert to full value
            st.session_state.annual_revenue = annual_revenue
            st.session_state.currency = currency
    
    # Get currency symbol
    currency_symbol = "€"
    if hasattr(st.session_state, 'currency'):
        if "USD" in st.session_state.currency:
            currency_symbol = "$"
        elif "GBP" in st.session_state.currency:
            currency_symbol = "£"
    
    # --- SECTION 1: EMISSION SUMMARY METRICS --- #
    st.markdown("## Emissions Overview")
    
    # Top-level metrics in cards
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(
            "Total Emissions",
            f"{format_number(total_emissions)} tCO₂e",
            delta=None
        )
    with col2:
        st.metric(
            "Scope 1 (Direct)",
            f"{format_number(scope1_total)} tCO₂e",
            delta=f"{format_number(scope1_total/total_emissions*100 if total_emissions else 0)}%"
        )
    with col3:
        st.metric(
            "Scope 2 (Indirect)",
            f"{format_number(scope2_total)} tCO₂e",
            delta=f"{format_number(scope2_total/total_emissions*100 if total_emissions else 0)}%"
        )
    with col4:
        st.metric(
            "Scope 3 (Value Chain)",
            f"{format_number(scope3_total)} tCO₂e", 
            delta=f"{format_number(scope3_total/total_emissions*100 if total_emissions else 0)}%"
        )
    
    # --- SECTION 2: EMISSION INTENSITY METRICS --- #
    st.markdown("## Emission Intensity")
    
    # Calculate emission intensity metrics
    if annual_revenue > 0:
        emission_intensity = (total_emissions * 1000) / annual_revenue  # kg CO2e per currency unit
        emission_intensity_revenue = emission_intensity * 1000000  # kg CO2e per million currency
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric(
                f"Emission Intensity (per {currency_symbol}1M revenue)",
                f"{format_number(emission_intensity_revenue)} kg CO₂e",
                delta=None
            )
        with col2:
            st.metric(
                f"Emission Intensity (per {currency_symbol} revenue)",
                f"{format_number(emission_intensity)} kg CO₂e",
                delta=None
            )
    else:
        st.info("Enter your organization's annual revenue to view emission intensity metrics.")
    
    # --- SECTION 3: EMISSIONS BREAKDOWN VISUALIZATIONS --- #
    st.markdown("## Emissions Breakdown")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Scope Distribution Pie Chart
        scope_data = {'Scope': ['Scope 1', 'Scope 2', 'Scope 3'], 
                     'Emissions': [scope1_total, scope2_total, scope3_total]}
        scope_df = pd.DataFrame(scope_data)
        
        fig_pie = px.pie(
            scope_df, 
            values='Emissions', 
            names='Scope',
            title='Emissions by Scope',
            color_discrete_sequence=px.colors.sequential.Viridis,
            hole=0.4
        )
        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
        fig_pie.update_layout(
            legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5),
            margin=dict(t=60, b=100, l=40, r=40),
            height=400
        )
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        # Category Breakdown
        if 'emissions_data' in st.session_state and st.session_state.emissions_data:
            # Extract category data from emissions_data
            categories = []
            emissions = []
            
            # Scope 1 categories
            if 'scope1' in st.session_state.emissions_data:
                for category, value in st.session_state.emissions_data['scope1'].items():
                    categories.append(category.replace('_', ' ').title())
                    emissions.append(value)
            
            # Scope 2 categories
            if 'scope2' in st.session_state.emissions_data:
                for category, value in st.session_state.emissions_data['scope2'].items():
                    categories.append(category.replace('_', ' ').title())
                    emissions.append(value)
            
            # Scope 3 categories (top 5 only to avoid overcrowding)
            if 'scope3' in st.session_state.emissions_data:
                scope3_categories = []
                scope3_emissions = []
                for category, value in st.session_state.emissions_data['scope3'].items():
                    scope3_categories.append(category.replace('_', ' ').title())
                    scope3_emissions.append(value)
                
                # Sort and take top 5
                if scope3_categories:
                    scope3_df = pd.DataFrame({'category': scope3_categories, 'emissions': scope3_emissions})
                    scope3_df = scope3_df.sort_values('emissions', ascending=False).head(5)
                    
                    for _, row in scope3_df.iterrows():
                        categories.append(row['category'])
                        emissions.append(row['emissions'])
            
            # Create horizontal bar chart
            if categories and emissions:
                df = pd.DataFrame({'Category': categories, 'Emissions': emissions})
                df = df.sort_values('Emissions', ascending=True)
                
                fig_bar = px.bar(
                    df,
                    x='Emissions',
                    y='Category',
                    orientation='h',
                    title='Top Emission Sources',
                    color='Emissions',
                    color_continuous_scale=px.colors.sequential.Viridis
                )
                fig_bar.update_layout(
                    xaxis_title="Emissions (tCO₂e)",
                    yaxis_title="",
                    height=400,
                    margin=dict(t=60, b=40, l=120, r=40)
                )
                st.plotly_chart(fig_bar, use_container_width=True)
            else:
                st.info("No detailed emissions data available to display category breakdown.")
        else:
            st.info("No detailed emissions data available to display category breakdown.")
    
    # --- SECTION 4: EMISSION REDUCTION TARGETS --- #
    st.markdown("## Emission Reduction Targets")
    
    # Allow setting reduction targets
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Set Reduction Targets")
        target_year = st.number_input("Target Year", min_value=2025, max_value=2050, value=2030)
        reduction_target = st.slider("Reduction Target (%)", min_value=0, max_value=100, value=30)
        
        # Calculate target emissions
        target_emissions = total_emissions * (1 - reduction_target/100)
        annual_reduction_needed = (total_emissions - target_emissions) / (target_year - reporting_year)
        annual_reduction_percent = (annual_reduction_needed / total_emissions) * 100
    
    with col2:
        st.subheader("Target Metrics")
        st.metric(
            f"Current Emissions ({reporting_year})",
            f"{format_number(total_emissions)} tCO₂e",
            delta=None
        )
        st.metric(
            f"Target Emissions ({target_year})",
            f"{format_number(target_emissions)} tCO₂e",
            delta=f"-{reduction_target}%"
        )
        st.metric(
            "Required Annual Reduction",
            f"{format_number(annual_reduction_needed)} tCO₂e/year",
            delta=f"-{format_number(annual_reduction_percent)}%/year"
        )
    
    # --- SECTION 5: FRAMEWORK COMPLIANCE --- #
    st.markdown("## ESG Framework Compliance")
    
    # Check if we have framework recommendations
    if 'framework_recommendations' in st.session_state and st.session_state.framework_recommendations:
        frameworks = st.session_state.framework_recommendations
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Recommended Frameworks")
            if frameworks.get('primary'):
                st.markdown("**Primary Frameworks:**")
                for framework in frameworks.get('primary', []):
                    st.markdown(f"- {framework}")
            
            if frameworks.get('secondary'):
                st.markdown("**Secondary Frameworks:**")
                for framework in frameworks.get('secondary', []):
                    st.markdown(f"- {framework}")
        
        with col2:
            st.subheader("Framework Assessment")
            st.markdown("Use the Framework Finder for detailed guidance on applicable frameworks based on your organization's profile.")
            if st.button("Go to Framework Finder", use_container_width=True):
                st.switch_page("pages/5_Framework_Finder.py")
    else:
        st.info("Complete the Framework Finder assessment to receive recommendations on applicable ESG reporting frameworks.")
        if st.button("Go to Framework Finder", use_container_width=True):
            st.switch_page("pages/5_Framework_Finder.py")
    
    # --- SECTION 6: NAVIGATION --- #
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        if st.button("📊 Input Data", use_container_width=True):
            st.switch_page("pages/1_Data_Input.py")
    with col2:
        if st.button("📈 View Detailed Dashboard", use_container_width=True):
            st.switch_page("pages/2_Dashboard.py")
    with col3:
        if st.button("📝 Generate Report", use_container_width=True):
            st.switch_page("pages/3_Report.py")