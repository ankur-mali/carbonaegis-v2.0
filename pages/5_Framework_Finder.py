import streamlit as st
import pandas as pd
from utils.data_manager import init_session_state

# Initialize session state
init_session_state()

# Add Carbon Aegis branding
col1, col2 = st.columns([1, 5])
with col1:
    st.image("assets/logo.png", width=100)
with col2:
    st.title("Carbon Aegis - Framework Finder")

st.markdown("""
This tool helps you identify the most appropriate sustainability reporting framework(s) 
for your organization based on European sustainability regulations and standards.
""")

# Framework detection helper function
def detect_frameworks(size, listed, turnover, employees, sector, country):
    """
    Determines the appropriate frameworks based on user inputs
    
    Parameters:
    -----------
    size : str
        Organization size category
    listed : bool
        Whether the organization is listed on a stock exchange
    turnover : float
        Annual turnover in euros
    employees : int
        Number of employees
    sector : str
        Industry sector
    country : str
        Country of operation
        
    Returns:
    --------
    dict
        Dictionary with recommended frameworks and explanations
    """
    frameworks = {
        'primary': [],
        'secondary': [],
        'explanations': {}
    }
    
    # CSRD check (Corporate Sustainability Reporting Directive)
    csrd_required = (
        listed or  # All listed companies (with some exceptions for micro-enterprises)
        (employees >= 250 and turnover >= 40000000) or  # Large companies meeting both criteria
        size == "Large"  # Self-identified large companies
    )
    
    # Make an exception for listed micro-enterprises (< 10 employees)
    if listed and employees < 10 and turnover < 2000000 and size == "Micro":
        csrd_required = False
    
    if csrd_required:
        frameworks['primary'].append('CSRD')
        frameworks['primary'].append('ESRS')
        frameworks['explanations']['CSRD'] = "Required for large companies with 250+ employees, €40M+ annual turnover, or listed companies"
        frameworks['explanations']['ESRS'] = "Required alongside CSRD as the reporting standards"
    
    # VSME check (Voluntary SME Standard)
    vsme_applicable = (
        employees < 250 and
        not listed and
        turnover < 40000000 and
        size in ["Micro", "Small", "Medium"]
    )
    
    if vsme_applicable:
        frameworks['primary'].append('VSME')
        frameworks['explanations']['VSME'] = "Voluntary standard specifically designed for SMEs not obligated under CSRD"
    
    # Always offer GRI as a secondary option
    frameworks['secondary'].append('GRI')
    frameworks['explanations']['GRI'] = "Voluntary global standard widely adopted by organizations of all sizes"
    
    # TCFD recommendation for climate-focused sectors
    climate_sensitive_sectors = [
        "Energy", 
        "Manufacturing", 
        "Transportation & Storage", 
        "Agriculture, Forestry & Fishing", 
        "Financial Services",
        "Mining & Extraction",
        "Water & Waste Management"
    ]
    if sector in climate_sensitive_sectors:
        frameworks['secondary'].append('TCFD')
        frameworks['explanations']['TCFD'] = "Recommended for organizations in climate-sensitive sectors"
    
    # SFDR for financial institutions
    if sector == "Financial Services":
        if not 'SFDR' in frameworks['primary'] and not 'SFDR' in frameworks['secondary']:
            frameworks['secondary'].append('SFDR')
            frameworks['explanations']['SFDR'] = "Applicable to financial market participants and financial advisers"
    
    return frameworks

# Create wizard-like interface with multi-step form
st.markdown("### Framework Detection Wizard")

# Side progress information
current_step = st.session_state.get('framework_finder_step', 1)
total_steps = 7  # Updated to include the results page (step 7)

# Progress bar (ensure we don't exceed total steps)
progress_value = min(current_step / total_steps, 1.0)
st.progress(progress_value)

# Create container for wizard
with st.container():
    if current_step == 1:
        st.subheader("Step 1: Organization Size")
        size = st.radio(
            "What is the size of your organization?",
            options=["Micro", "Small", "Medium", "Large"],
            index=0,
            help="Micro: <10 employees, Small: <50 employees, Medium: <250 employees, Large: 250+ employees"
        )
        st.session_state.framework_size = size
        
        col1, col2 = st.columns([1, 5])
        with col1:
            if st.button("Next", use_container_width=True, key="size_next"):
                st.session_state.framework_finder_step = 2
                st.rerun()
    
    elif current_step == 2:
        st.subheader("Step 2: Stock Exchange Listing")
        listed = st.radio(
            "Is your organization listed on a stock exchange?",
            options=["Yes", "No"],
            index=1,
            help="Select 'Yes' if your company's shares are traded on any stock exchange"
        )
        st.session_state.framework_listed = (listed == "Yes")
        
        col1, col2, col3 = st.columns([1, 1, 5])
        with col1:
            if st.button("Previous", use_container_width=True, key="listed_prev"):
                st.session_state.framework_finder_step = 1
                st.rerun()
        with col2:
            if st.button("Next", use_container_width=True, key="listed_next"):
                st.session_state.framework_finder_step = 3
                st.rerun()
    
    elif current_step == 3:
        st.subheader("Step 3: Annual Turnover")
        turnover = st.number_input(
            "What is your organization's annual turnover (in €)?",
            min_value=0,
            value=1000000,
            step=100000,
            format="%d",
            help="Enter your organization's annual revenue in euros"
        )
        st.session_state.framework_turnover = turnover
        
        col1, col2, col3 = st.columns([1, 1, 5])
        with col1:
            if st.button("Previous", use_container_width=True, key="turnover_prev"):
                st.session_state.framework_finder_step = 2
                st.rerun()
        with col2:
            if st.button("Next", use_container_width=True, key="turnover_next"):
                st.session_state.framework_finder_step = 4
                st.rerun()
    
    elif current_step == 4:
        st.subheader("Step 4: Employee Count")
        employees = st.number_input(
            "How many employees does your organization have?",
            min_value=1,
            value=50,
            step=10,
            format="%d",
            help="Enter the total number of full-time equivalent employees"
        )
        st.session_state.framework_employees = employees
        
        col1, col2, col3 = st.columns([1, 1, 5])
        with col1:
            if st.button("Previous", use_container_width=True, key="employees_prev"):
                st.session_state.framework_finder_step = 3
                st.rerun()
        with col2:
            if st.button("Next", use_container_width=True, key="employees_next"):
                st.session_state.framework_finder_step = 5
                st.rerun()
    
    elif current_step == 5:
        st.subheader("Step 5: Industry Sector")
        sector = st.selectbox(
            "What is your organization's primary sector?",
            options=[
                "Agriculture, Forestry & Fishing",
                "Mining & Extraction",
                "Manufacturing",
                "Energy",
                "Water & Waste Management",
                "Construction",
                "Wholesale & Retail",
                "Transportation & Storage",
                "Accommodation & Food Service",
                "Information & Communication",
                "Financial Services",
                "Real Estate",
                "Professional Services",
                "Administrative Services",
                "Public Administration",
                "Education",
                "Healthcare & Social Work",
                "Arts & Entertainment",
                "Other Service Activities"
            ],
            index=0,
            help="Select the industry that best describes your organization's activities"
        )
        st.session_state.framework_sector = sector
        
        col1, col2, col3 = st.columns([1, 1, 5])
        with col1:
            if st.button("Previous", use_container_width=True, key="sector_prev"):
                st.session_state.framework_finder_step = 4
                st.rerun()
        with col2:
            if st.button("Next", use_container_width=True, key="sector_next"):
                st.session_state.framework_finder_step = 6
                st.rerun()
    
    elif current_step == 6:
        st.subheader("Step 6: Country of Operation")
        country = st.selectbox(
            "In which European country is your organization primarily operating?",
            options=[
                "Austria", "Belgium", "Bulgaria", "Croatia", "Cyprus", "Czech Republic",
                "Denmark", "Estonia", "Finland", "France", "Germany", "Greece", "Hungary",
                "Ireland", "Italy", "Latvia", "Lithuania", "Luxembourg", "Malta", "Netherlands",
                "Poland", "Portugal", "Romania", "Slovakia", "Slovenia", "Spain", "Sweden",
                "United Kingdom", "Other (Non-EU)"
            ],
            index=0,
            help="Select your organization's primary country of operation for localized guidance"
        )
        st.session_state.framework_country = country
        
        col1, col2, col3 = st.columns([1, 1, 5])
        with col1:
            if st.button("Previous", use_container_width=True, key="country_prev"):
                st.session_state.framework_finder_step = 5
                st.rerun()
        with col2:
            if st.button("Get Results", use_container_width=True, key="get_results"):
                st.session_state.framework_finder_step = 7
                st.rerun()

# Display results
if current_step == 7:
    st.markdown("### Recommended Frameworks")
    
    # Retrieve all the saved data
    size = st.session_state.framework_size
    listed = st.session_state.framework_listed
    turnover = st.session_state.framework_turnover
    employees = st.session_state.framework_employees
    sector = st.session_state.framework_sector
    country = st.session_state.framework_country
    
    # Get framework recommendations
    frameworks = detect_frameworks(size, listed, turnover, employees, sector, country)
    
    # Display organization info summary
    st.markdown("#### Organization Profile Summary")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**Size:** {size}")
        st.markdown(f"**Listed on Stock Exchange:** {'Yes' if listed else 'No'}")
        st.markdown(f"**Annual Turnover:** €{turnover:,}")
    with col2:
        st.markdown(f"**Employee Count:** {employees}")
        st.markdown(f"**Sector:** {sector}")
        st.markdown(f"**Country:** {country}")
    
    # Primary frameworks
    st.markdown("#### Primary Recommended Framework(s)")
    if frameworks['primary']:
        for framework in frameworks['primary']:
            st.markdown(f"**{framework}**")
            st.markdown(f"- {frameworks['explanations'][framework]}")
    else:
        st.info("No primary frameworks are mandatory for your organization.")
    
    # Secondary frameworks
    st.markdown("#### Additional Recommended Framework(s)")
    if frameworks['secondary']:
        for framework in frameworks['secondary']:
            st.markdown(f"**{framework}**")
            st.markdown(f"- {frameworks['explanations'][framework]}")
    
    # Framework descriptions
    st.markdown("### Framework Descriptions")
    
    framework_info = {
        'CSRD': {
            'full_name': 'Corporate Sustainability Reporting Directive',
            'description': 'An EU directive that requires large companies to disclose information on the way they operate and manage social and environmental challenges.',
            'link': 'https://finance.ec.europa.eu/capital-markets-union-and-financial-markets/company-reporting-and-auditing/company-reporting/corporate-sustainability-reporting_en'
        },
        'ESRS': {
            'full_name': 'European Sustainability Reporting Standards',
            'description': 'Detailed standards for sustainability reporting under the CSRD, covering environmental, social, and governance aspects.',
            'link': 'https://www.efrag.org/Activities/2105191406363055/Sustainability-reporting-standards-interim-draft'
        },
        'VSME': {
            'full_name': 'Voluntary SME Standards',
            'description': 'Simplified standards for Small and Medium-sized Enterprises to voluntarily report on sustainability matters.',
            'link': 'https://www.efrag.org/Assets/Download?assetUrl=%2Fsites%2Fwebpublishing%2FSiteAssets%2FED_ESRS_SMEs.pdf'
        },
        'GRI': {
            'full_name': 'Global Reporting Initiative',
            'description': 'A widely used international framework for sustainability reporting applicable to organizations of all sizes.',
            'link': 'https://www.globalreporting.org/standards/'
        },
        'TCFD': {
            'full_name': 'Task Force on Climate-related Financial Disclosures',
            'description': 'Framework for climate-related financial risk disclosures, focusing on governance, strategy, risk management, and metrics & targets.',
            'link': 'https://www.fsb-tcfd.org/'
        },
        'SFDR': {
            'full_name': 'Sustainable Finance Disclosure Regulation',
            'description': 'EU regulation requiring financial market participants to disclose how they integrate ESG factors into their investment decisions.',
            'link': 'https://finance.ec.europa.eu/sustainable-finance/disclosures_en'
        }
    }
    
    # Show info for all frameworks that are either primary or secondary
    all_frameworks = set(frameworks['primary'] + frameworks['secondary'])
    
    for framework in all_frameworks:
        if framework in framework_info:
            info = framework_info[framework]
            with st.expander(f"{framework} - {info['full_name']}"):
                st.markdown(f"**Description:** {info['description']}")
                st.markdown(f"**Official Resources:** [Learn more]({info['link']})")
    
    # Reset button
    if st.button("Start Over", key="reset_finder"):
        st.session_state.framework_finder_step = 1
        st.rerun()

    # Add this info to session state for report generation
    st.session_state.framework_recommendations = frameworks
    
    # Navigation buttons
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        if st.button("📊 Input Data", use_container_width=True):
            st.switch_page("pages/1_Data_Input.py")
    with col2:
        if st.button("📈 View Dashboard", use_container_width=True):
            st.switch_page("pages/2_Dashboard.py")
    with col3:
        if st.button("📝 Generate Report", use_container_width=True):
            st.switch_page("pages/3_Report.py")

# Help section with improved styling
st.markdown("### ❓ Help & Resources")
with st.container():
    st.markdown("")
    
    with st.expander("About Sustainability Reporting Frameworks"):
        st.markdown("""
        **What are sustainability reporting frameworks?**
        
        Sustainability reporting frameworks provide guidelines and standards for organizations to disclose their environmental, social, and governance (ESG) impacts and performance.
        
        **Why are they important?**
        
        * **Compliance**: Many organizations are legally required to report on sustainability matters
        * **Transparency**: They help stakeholders understand an organization's sustainability performance
        * **Comparability**: They enable comparison of sustainability performance across organizations
        * **Improvement**: They help organizations identify areas for improvement
        
        **How to use this tool**
        
        This tool provides guidance on which frameworks may be most relevant to your organization based on European regulations. The actual requirements may vary based on specific circumstances, so always consult with sustainability reporting experts for definitive advice.
        """)