import streamlit as st
import pandas as pd
from datetime import datetime
from utils.data_manager import init_session_state

# Page configuration
st.set_page_config(
    page_title="Carbon Aegis - Onboarding",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initialize session state
init_session_state()

# Initialize onboarding session state variables
if 'onboarding_step' not in st.session_state:
    st.session_state.onboarding_step = 1
if 'user_role' not in st.session_state:
    st.session_state.user_role = None
if 'onboarding_complete' not in st.session_state:
    st.session_state.onboarding_complete = False
if 'onboarding_data' not in st.session_state:
    st.session_state.onboarding_data = {}

# Custom CSS for modern styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #2E8B57;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        font-weight: 500;
        color: #444;
        margin-bottom: 2rem;
    }
    .info-text {
        font-size: 1.1rem;
        color: #666;
        margin-bottom: 1.5rem;
    }
    .card-container {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 20px;
        border-left: 5px solid #2E8B57;
    }
    .centered {
        display: flex;
        justify-content: center;
        align-items: center;
    }
    .role-card {
        background-color: white;
        border-radius: 10px;
        padding: 30px;
        text-align: center;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        cursor: pointer;
        height: 100%;
    }
    .role-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 16px rgba(0,0,0,0.1);
    }
    .role-card h3 {
        color: #2E8B57;
        margin-bottom: 15px;
    }
    .progress-container {
        margin: 2rem 0;
    }
    .progress-step {
        background-color: #e9ecef;
        color: #666;
        border-radius: 50%;
        width: 30px;
        height: 30px;
        line-height: 30px;
        text-align: center;
        display: inline-block;
        margin: 0 5px;
    }
    .progress-step.active {
        background-color: #2E8B57;
        color: white;
    }
    .progress-line {
        display: inline-block;
        width: 50px;
        height: 3px;
        background-color: #e9ecef;
        margin: 0 -5px;
        vertical-align: middle;
    }
    .progress-line.active {
        background-color: #2E8B57;
    }
    .btn-primary {
        background-color: #2E8B57;
        color: white;
        padding: 12px 24px;
        border-radius: 5px;
        border: none;
        cursor: pointer;
        font-size: 16px;
        font-weight: 500;
        display: inline-block;
        text-align: center;
        margin: 10px 0;
    }
    .btn-primary:hover {
        background-color: #3aa76d;
    }
    .btn-secondary {
        background-color: #6c757d;
        color: white;
        padding: 12px 24px;
        border-radius: 5px;
        border: none;
        cursor: pointer;
        font-size: 16px;
        font-weight: 500;
        display: inline-block;
        text-align: center;
        margin: 10px 0;
    }
    .btn-secondary:hover {
        background-color: #5a6268;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="main-header">Welcome to Carbon Aegis</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Let\'s personalize your experience</div>', unsafe_allow_html=True)

# Progress indicator
def render_progress_bar(current_step, total_steps=3):
    html = '<div class="progress-container">'
    for i in range(1, total_steps + 1):
        step_class = "active" if i <= current_step else ""
        html += f'<div class="progress-step {step_class}">{i}</div>'
        if i < total_steps:
            line_class = "active" if i < current_step else ""
            html += f'<div class="progress-line {line_class}"></div>'
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)

render_progress_bar(st.session_state.onboarding_step)

# Step 1: Role Selection
if st.session_state.onboarding_step == 1:
    st.markdown('<div class="info-text">Please select your role to help us personalize your Carbon Aegis experience.</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        consultant_card = st.container(border=False)
        with consultant_card:
            st.markdown("""
            <div class="role-card" id="consultant-card">
                <img src="https://img.icons8.com/fluency/96/000000/conference-call.png" alt="Consultant Icon" width="60">
                <h3>ESG Consultant</h3>
                <p>I help organizations improve their sustainability practices and ESG reporting.</p>
                <p><strong>Features:</strong> Multi-client management, Framework mapping, Client surveys</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Select Consultant", key="consultant_btn", use_container_width=True):
                st.session_state.user_role = "consultant"
                st.session_state.onboarding_step = 2
                st.rerun()
    
    with col2:
        organization_card = st.container(border=False)
        with organization_card:
            st.markdown("""
            <div class="role-card" id="organization-card">
                <img src="https://img.icons8.com/fluency/96/000000/organization.png" alt="Organization Icon" width="60">
                <h3>Organization</h3>
                <p>I want to track, report, and improve my organization's sustainability performance.</p>
                <p><strong>Features:</strong> Emissions tracking, ESG reporting, Improvement recommendations</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Select Organization", key="organization_btn", use_container_width=True):
                st.session_state.user_role = "organization"
                st.session_state.onboarding_step = 2
                st.rerun()

# Step 2: Profile Questionnaire
elif st.session_state.onboarding_step == 2:
    st.markdown(f'<div class="info-text">Tell us more about you as an {st.session_state.user_role.capitalize()}</div>', unsafe_allow_html=True)
    
    with st.form("onboarding_form"):
        st.markdown('<div class="card-container">', unsafe_allow_html=True)
        
        # Common fields
        name = st.text_input("Your Name", key="user_name")
        email = st.text_input("Email Address", key="user_email")
        
        # Role-specific fields
        if st.session_state.user_role == "consultant":
            organization = st.text_input("Consulting Firm Name", key="consulting_firm")
            focus_areas = st.multiselect(
                "Areas of Focus",
                options=["Carbon Accounting", "ESG Reporting", "Sustainability Strategy", "Climate Risk Assessment", 
                         "Net Zero Planning", "Regulatory Compliance", "Sustainable Finance"],
                default=["Carbon Accounting", "ESG Reporting"]
            )
            num_clients = st.select_slider(
                "Number of Clients",
                options=["1-5", "6-20", "21-49", "50+"],
                value="6-20"
            )
            experience = st.select_slider(
                "Years of Experience",
                options=["<1 year", "1-3 years", "3-5 years", "5-10 years", "10+ years"],
                value="3-5 years"
            )
            frameworks = st.multiselect(
                "Frameworks You Work With",
                options=["GHG Protocol", "TCFD", "CSRD", "ESRS", "GRI", "SASB", "CDP", "SFDR"],
                default=["GHG Protocol", "TCFD"]
            )
            
        else:  # organization
            organization = st.text_input("Organization Name", key="organization_name")
            industry = st.selectbox(
                "Industry Sector",
                options=["Manufacturing", "Financial Services", "Technology", "Energy", "Healthcare", "Retail", 
                         "Transportation", "Construction", "Agriculture", "Other"],
            )
            size = st.select_slider(
                "Organization Size",
                options=["Small (<50 employees)", "Medium (50-250 employees)", "Large (250-1000 employees)", "Enterprise (1000+ employees)"],
                value="Medium (50-250 employees)"
            )
            reporting_status = st.radio(
                "Current ESG Reporting Status",
                options=["Not reporting yet", "Basic reporting", "Comprehensive reporting", "Advanced reporting with targets"],
                index=1
            )
            goals = st.multiselect(
                "Sustainability Goals",
                options=["Regulatory compliance", "Emissions reduction", "Net zero commitment", "Supply chain sustainability",
                         "ESG investor reporting", "Stakeholder transparency", "Product sustainability"],
                default=["Regulatory compliance", "Emissions reduction"]
            )
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Submit button
        submitted = st.form_submit_button("Continue", use_container_width=True)
        
        if submitted:
            # Save form data
            onboarding_data = {
                "name": name,
                "email": email,
                "organization": organization,
                "role": st.session_state.user_role,
            }
            
            if st.session_state.user_role == "consultant":
                onboarding_data.update({
                    "focus_areas": focus_areas,
                    "num_clients": num_clients,
                    "experience": experience,
                    "frameworks": frameworks
                })
            else:
                onboarding_data.update({
                    "industry": industry,
                    "size": size,
                    "reporting_status": reporting_status,
                    "goals": goals
                })
            
            st.session_state.onboarding_data = onboarding_data
            st.session_state.onboarding_step = 3
            st.rerun()

# Step 3: Confirmation and Personalization
elif st.session_state.onboarding_step == 3:
    data = st.session_state.onboarding_data
    
    st.markdown('<div class="card-container">', unsafe_allow_html=True)
    st.subheader("Perfect! Your Carbon Aegis platform is ready.")
    
    if st.session_state.user_role == "consultant":
        st.markdown(f"""
        ### Welcome, {data.get('name', 'Consultant')}!
        
        Your personalized ESG consulting platform has been configured with:
        
        * **Focus Areas**: {', '.join(data.get('focus_areas', []))}
        * **Framework Expertise**: {', '.join(data.get('frameworks', []))}
        * **Client Capacity**: {data.get('num_clients', '')}
        
        Your consultant dashboard will help you manage multiple clients, 
        streamline ESG reporting, and provide strategic sustainability guidance.
        """)
    else:
        st.markdown(f"""
        ### Welcome, {data.get('name', 'User')} from {data.get('organization', 'Your Organization')}!
        
        Your personalized sustainability platform has been configured with:
        
        * **Industry**: {data.get('industry', '')}
        * **Size**: {data.get('size', '')}
        * **Primary Goals**: {', '.join(data.get('goals', []))}
        
        Your dashboard will help you track emissions, meet reporting requirements,
        and identify opportunities to improve your sustainability performance.
        """)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Next steps and recommendations
    st.subheader("Recommended Next Steps")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        #### Start with Data Input
        Begin by entering your emissions data to establish a baseline
        """)
        if st.button("Go to Data Input", key="data_input_btn", use_container_width=True):
            st.session_state.onboarding_complete = True
            st.switch_page("pages/1_Data_Input.py")
    
    with col2:
        st.markdown("""
        #### Explore Reporting Frameworks
        Identify which frameworks apply to your organization
        """)
        if st.button("Framework Finder", key="framework_btn", use_container_width=True):
            st.session_state.onboarding_complete = True
            st.switch_page("pages/5_Framework_Finder.py")
    
    # Complete button
    if st.button("Go to Home Dashboard", key="complete_btn", use_container_width=True):
        st.session_state.onboarding_complete = True
        st.switch_page("home.py")

# Handle "back" navigation
if st.session_state.onboarding_step > 1:
    if st.button("← Back", key="back_btn"):
        st.session_state.onboarding_step -= 1
        st.rerun()