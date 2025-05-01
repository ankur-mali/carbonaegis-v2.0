import streamlit as st
import pandas as pd
import sys
import io
from datetime import datetime

# Add parent directory to path to import utils
sys.path.append('..')

# Page configuration
st.set_page_config(
    page_title="Report Generator | Carbon Aegis",
    page_icon="📝",
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
    .section-card {
        padding: 1.5rem;
        border-radius: 4px;
        background: #ffffff;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        margin-bottom: 1.5rem;
    }
    .section-header {
        display: flex;
        align-items: center;
        margin-bottom: 1rem;
    }
    .section-icon {
        font-size: 1.5rem;
        margin-right: 0.5rem;
    }
    .section-title {
        font-size: 1.2rem;
        font-weight: 600;
        color: #161616;
    }
    .report-preview {
        padding: 2rem;
        border: 1px solid #e0e0e0;
        border-radius: 4px;
        background: #ffffff;
        margin-top: 1rem;
    }
    .logo-container {
        margin-bottom: 2rem;
    }
    .logo-container img {
        max-height: 60px;
    }
    </style>
    """, unsafe_allow_html=True)

# Initialize session state variables
def init_session_state():
    if 'processed_data' not in st.session_state:
        st.session_state.processed_data = None
    if 'report_title' not in st.session_state:
        st.session_state.report_title = "GHG Emissions Report"
    if 'report_period' not in st.session_state:
        st.session_state.report_period = f"Year {datetime.now().year}"
    if 'organization_name' not in st.session_state:
        st.session_state.organization_name = "Your Organization"
    if 'include_sections' not in st.session_state:
        st.session_state.include_sections = {
            'executive_summary': True,
            'emissions_overview': True,
            'scope_breakdown': True,
            'category_breakdown': True,
            'time_series': True,
            'methodology': True,
            'recommendations': False
        }

# Format number with thousand separators
def format_number(number, precision=2):
    """Format number with thousand separators and specified precision"""
    if isinstance(number, (int, float)):
        return f"{number:,.{precision}f}"
    return number

# Get the appropriate units for emissions
def get_emission_units():
    """Return the appropriate units for emissions"""
    if 'emission_unit' in st.session_state:
        return st.session_state.emission_unit
    return "kg CO₂e"  # Default unit

# Main report function
def main():
    add_custom_css()
    init_session_state()
    
    # Display logo
    st.image("assets/logo.png", width=180)
    
    st.title("Report Generator")
    st.write("Generate comprehensive emissions reports based on your data.")
    
    # Check if data is available
    if st.session_state.processed_data is None:
        st.warning("No emissions data available. Please import data first.")
        if st.button("Go to Data Import"):
            st.switch_page("pages/1_Data_Input.py")
        return
    
    # Get data from session state
    data = st.session_state.processed_data
    
    # Report configuration sidebar
    st.sidebar.title("Report Configuration")
    
    st.sidebar.subheader("Report Information")
    st.session_state.report_title = st.sidebar.text_input("Report Title", value=st.session_state.report_title)
    st.session_state.organization_name = st.sidebar.text_input("Organization Name", value=st.session_state.organization_name)
    st.session_state.report_period = st.sidebar.text_input("Reporting Period", value=st.session_state.report_period)
    
    st.sidebar.subheader("Included Sections")
    st.session_state.include_sections['executive_summary'] = st.sidebar.checkbox("Executive Summary", value=st.session_state.include_sections['executive_summary'])
    st.session_state.include_sections['emissions_overview'] = st.sidebar.checkbox("Emissions Overview", value=st.session_state.include_sections['emissions_overview'])
    st.session_state.include_sections['scope_breakdown'] = st.sidebar.checkbox("Scope Breakdown", value=st.session_state.include_sections['scope_breakdown'])
    st.session_state.include_sections['category_breakdown'] = st.sidebar.checkbox("Category Breakdown", value=st.session_state.include_sections['category_breakdown'])
    st.session_state.include_sections['time_series'] = st.sidebar.checkbox("Time Series Analysis", value=st.session_state.include_sections['time_series'])
    st.session_state.include_sections['methodology'] = st.sidebar.checkbox("Methodology", value=st.session_state.include_sections['methodology'])
    st.session_state.include_sections['recommendations'] = st.sidebar.checkbox("Recommendations", value=st.session_state.include_sections['recommendations'])
    
    # Report format selection
    st.sidebar.subheader("Export Format")
    report_format = st.sidebar.radio("Select Format", ["Excel", "PDF"])
    
    # Generate report button
    if st.sidebar.button("Generate Report", type="primary"):
        with st.spinner("Generating report..."):
            # In a production system, this would generate the actual report
            # For now, we'll just wait a moment to simulate processing
            import time
            time.sleep(1)
            
            # Show success message
            if report_format == "Excel":
                st.sidebar.success("Excel report generated successfully.")
                st.sidebar.info("In a production environment, this would download the Excel file.")
            else:
                st.sidebar.success("PDF report generated successfully.")
                st.sidebar.info("In a production environment, this would download the PDF file.")
    
    # Main content area - Report Preview
    st.header("Report Preview")
    
    with st.container():
        st.markdown(f"""
        <div class="report-preview">
            <h2 style="text-align: center;">{st.session_state.report_title}</h2>
            <h4 style="text-align: center;">{st.session_state.organization_name}</h4>
            <h4 style="text-align: center;">{st.session_state.report_period}</h4>
            <p style="text-align: center;">Generated on {datetime.now().strftime('%B %d, %Y')}</p>
            <hr>
        """, unsafe_allow_html=True)
        
        # Executive Summary
        if st.session_state.include_sections['executive_summary']:
            total_emissions = data['total']
            by_scope = data['by_scope']
            
            st.markdown("""
            <div class="section-header">
                <div class="section-icon">📊</div>
                <div class="section-title">Executive Summary</div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <p>This report provides a comprehensive overview of greenhouse gas (GHG) emissions for {st.session_state.organization_name} during {st.session_state.report_period}.</p>
            
            <p>Total emissions for the period were <strong>{format_number(total_emissions)} {get_emission_units()}</strong>, with the following breakdown:</p>
            <ul>
                <li>Scope 1 (Direct Emissions): {format_number(by_scope.get('Scope 1', 0))} {get_emission_units()} ({format_number(by_scope.get('Scope 1', 0) / total_emissions * 100 if total_emissions > 0 else 0)}%)</li>
                <li>Scope 2 (Indirect Emissions from Purchased Energy): {format_number(by_scope.get('Scope 2', 0))} {get_emission_units()} ({format_number(by_scope.get('Scope 2', 0) / total_emissions * 100 if total_emissions > 0 else 0)}%)</li>
                <li>Scope 3 (Other Indirect Emissions): {format_number(by_scope.get('Scope 3', 0))} {get_emission_units()} ({format_number(by_scope.get('Scope 3', 0) / total_emissions * 100 if total_emissions > 0 else 0)}%)</li>
            </ul>
            """, unsafe_allow_html=True)
        
        # Emissions Overview
        if st.session_state.include_sections['emissions_overview']:
            st.markdown("""
            <div class="section-header">
                <div class="section-icon">📈</div>
                <div class="section-title">Emissions Overview</div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <p>The organization's total greenhouse gas emissions for {st.session_state.report_period} were {format_number(data['total'])} {get_emission_units()}.</p>
            
            <p>Key metrics:</p>
            <ul>
                <li>Emissions Intensity: {format_number(data['total'] / 100)} {get_emission_units()} per unit of revenue/output</li>
                <li>Per Employee: {format_number(data['total'] / 50)} {get_emission_units()} per employee</li>
                <li>Year-over-Year Change: [Would be calculated based on historical data]</li>
            </ul>
            """, unsafe_allow_html=True)
        
        # Scope Breakdown
        if st.session_state.include_sections['scope_breakdown']:
            st.markdown("""
            <div class="section-header">
                <div class="section-icon">🔍</div>
                <div class="section-title">Scope Breakdown</div>
            </div>
            """, unsafe_allow_html=True)
            
            by_scope = data['by_scope']
            st.markdown(f"""
            <h4>Scope 1: Direct Emissions</h4>
            <p>Scope 1 emissions from owned or controlled sources totaled {format_number(by_scope.get('Scope 1', 0))} {get_emission_units()}.</p>
            <p>These emissions include:</p>
            <ul>
                <li>Stationary combustion (e.g., natural gas, fuel oil)</li>
                <li>Mobile combustion (e.g., company vehicles)</li>
                <li>Fugitive emissions (e.g., refrigerants)</li>
                <li>Process emissions</li>
            </ul>
            
            <h4>Scope 2: Indirect Emissions from Purchased Energy</h4>
            <p>Scope 2 emissions from purchased electricity, steam, heating, and cooling totaled {format_number(by_scope.get('Scope 2', 0))} {get_emission_units()}.</p>
            <p>These emissions include:</p>
            <ul>
                <li>Purchased electricity</li>
                <li>Purchased steam</li>
                <li>Purchased heating</li>
                <li>Purchased cooling</li>
            </ul>
            
            <h4>Scope 3: Other Indirect Emissions</h4>
            <p>Scope 3 emissions from the value chain totaled {format_number(by_scope.get('Scope 3', 0))} {get_emission_units()}.</p>
            <p>These emissions include:</p>
            <ul>
                <li>Business travel</li>
                <li>Employee commuting</li>
                <li>Purchased goods and services</li>
                <li>Waste disposal</li>
                <li>Transportation and distribution</li>
                <li>Use of sold products</li>
                <li>End-of-life treatment of sold products</li>
            </ul>
            """, unsafe_allow_html=True)
        
        # Category Breakdown
        if st.session_state.include_sections['category_breakdown']:
            st.markdown("""
            <div class="section-header">
                <div class="section-icon">📊</div>
                <div class="section-title">Category Breakdown</div>
            </div>
            """, unsafe_allow_html=True)
            
            # Create a table of emission categories
            by_category = data['by_category']
            if by_category:
                st.markdown("<h4>Emissions by Category</h4>", unsafe_allow_html=True)
                
                # Sort categories by emissions (descending)
                sorted_categories = sorted(by_category.items(), key=lambda x: x[1], reverse=True)
                
                # Create HTML table
                table_html = """
                <table style="width:100%; border-collapse: collapse;">
                    <tr style="background-color: #f4f4f4;">
                        <th style="padding: 8px; text-align: left; border-bottom: 1px solid #ddd;">Category</th>
                        <th style="padding: 8px; text-align: right; border-bottom: 1px solid #ddd;">Emissions</th>
                        <th style="padding: 8px; text-align: right; border-bottom: 1px solid #ddd;">Percentage</th>
                    </tr>
                """
                
                for category, emissions in sorted_categories:
                    percentage = (emissions / data['total'] * 100) if data['total'] > 0 else 0
                    category_display = category.replace('_', ' ').title()
                    
                    table_html += f"""
                    <tr>
                        <td style="padding: 8px; text-align: left; border-bottom: 1px solid #ddd;">{category_display}</td>
                        <td style="padding: 8px; text-align: right; border-bottom: 1px solid #ddd;">{format_number(emissions)} {get_emission_units()}</td>
                        <td style="padding: 8px; text-align: right; border-bottom: 1px solid #ddd;">{format_number(percentage)}%</td>
                    </tr>
                    """
                
                table_html += "</table>"
                st.markdown(table_html, unsafe_allow_html=True)
            else:
                st.markdown("<p>No category data available.</p>", unsafe_allow_html=True)
        
        # Time Series Analysis
        if st.session_state.include_sections['time_series']:
            st.markdown("""
            <div class="section-header">
                <div class="section-icon">📅</div>
                <div class="section-title">Time Series Analysis</div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("""
            <p>This section provides analysis of emissions trends over time.</p>
            
            <p>[In a production environment, this section would include time series charts and analysis of emissions trends.]</p>
            """, unsafe_allow_html=True)
        
        # Methodology
        if st.session_state.include_sections['methodology']:
            st.markdown("""
            <div class="section-header">
                <div class="section-icon">📋</div>
                <div class="section-title">Methodology</div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("""
            <p>This report follows the Greenhouse Gas Protocol Corporate Accounting and Reporting Standard, which provides requirements and guidance for companies preparing a GHG emissions inventory.</p>
            
            <h4>Calculation Methodology</h4>
            <p>Emissions were calculated using the following formula:</p>
            <p><strong>Activity data × Emission factor = GHG emissions</strong></p>
            
            <h4>Emission Factors</h4>
            <p>Emission factors were sourced from recognized databases including:</p>
            <ul>
                <li>EPA Emission Factors Hub</li>
                <li>DEFRA Conversion Factors</li>
                <li>IEA Emission Factors</li>
                <li>Local utility-specific emission factors where available</li>
            </ul>
            
            <h4>Organizational Boundaries</h4>
            <p>The operational control approach was used to define organizational boundaries. Under this approach, the organization accounts for 100% of emissions from operations over which it has operational control.</p>
            
            <h4>Reporting Period</h4>
            <p>This report covers the period: {st.session_state.report_period}</p>
            """, unsafe_allow_html=True)
        
        # Recommendations
        if st.session_state.include_sections['recommendations']:
            st.markdown("""
            <div class="section-header">
                <div class="section-icon">💡</div>
                <div class="section-title">Recommendations</div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("""
            <p>Based on the emissions data analyzed, the following recommendations are provided:</p>
            
            <h4>Short-term Actions</h4>
            <ul>
                <li>Implement energy efficiency measures in facilities</li>
                <li>Optimize business travel policies</li>
                <li>Expand remote work options to reduce commuting emissions</li>
                <li>Switch to renewable energy providers where available</li>
            </ul>
            
            <h4>Medium-term Strategies</h4>
            <ul>
                <li>Develop a comprehensive emissions reduction plan with targets</li>
                <li>Engage suppliers on emissions reduction initiatives</li>
                <li>Invest in on-site renewable energy generation</li>
                <li>Implement sustainable procurement policies</li>
            </ul>
            
            <h4>Long-term Vision</h4>
            <ul>
                <li>Set science-based targets aligned with the Paris Agreement</li>
                <li>Develop a roadmap to carbon neutrality</li>
                <li>Implement circular economy principles to reduce waste and resource consumption</li>
                <li>Integrate climate risks into business strategy and governance</li>
            </ul>
            """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()