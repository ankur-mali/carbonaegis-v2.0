import streamlit as st

def render_sidebar():
    """
    Renders a consistent, modern sidebar across all pages
    """
    with st.sidebar:
        # Logo at the top
        st.image("assets/logo.png", width=100)
        
        # App name under logo
        st.markdown("### Carbon Aegis")
        
        # Add some space
        st.markdown("---")
        
        # Show user info if onboarded
        if st.session_state.get('onboarding_complete', False) and st.session_state.get('user_role'):
            role_display = "Consultant" if st.session_state.user_role == "consultant" else "Organization"
            user_name = st.session_state.onboarding_data.get('name', '') if hasattr(st.session_state, 'onboarding_data') else ''
            org_name = st.session_state.onboarding_data.get('organization', '') if hasattr(st.session_state, 'onboarding_data') else ''
            
            st.markdown(f"**User:** {user_name}")
            st.markdown(f"**Role:** {role_display}")
            st.markdown(f"**Organization:** {org_name}")
            st.markdown("---")
        
        # Navigation Sections
        st.markdown("### Navigation")
        
        # Home
        if st.sidebar.button("🏠 Home", use_container_width=True):
            st.switch_page("app.py")
        
        # Core Features Section
        st.markdown("#### Core Features")
        
        # Data Input
        if st.sidebar.button("📊 Data Input", use_container_width=True):
            st.switch_page("pages/1_Data_Input.py")
        
        # Dashboard
        if st.sidebar.button("📈 Dashboard", use_container_width=True):
            st.switch_page("pages/2_Dashboard.py")
        
        # Reports
        if st.sidebar.button("📝 Report Generator", use_container_width=True):
            st.switch_page("pages/3_Report.py")
        
        # Saved Reports
        if st.sidebar.button("📁 Saved Reports", use_container_width=True):
            st.switch_page("pages/4_Saved_Reports.py")
        
        # ESG Tools Section
        st.markdown("#### ESG Tools")
        
        # Framework Finder
        if st.sidebar.button("📏 Framework Finder", use_container_width=True):
            st.switch_page("pages/5_Framework_Finder.py")
        
        # ESG Dashboard
        if st.sidebar.button("🎯 ESG Dashboard", use_container_width=True):
            st.switch_page("pages/6_ESG_Dashboard.py")
        
        # ESG Readiness
        if st.sidebar.button("📊 ESG Readiness", use_container_width=True):
            st.switch_page("pages/7_ESG_Readiness.py")
        
        # Team Workspace
        if st.sidebar.button("👥 Team Workspace", use_container_width=True):
            st.switch_page("pages/8_Team_Workspace.py")
        
        # Advanced Features Section
        st.markdown("#### Advanced Features")
        
        # AI Assistant
        if st.sidebar.button("🤖 AI Assistant", use_container_width=True):
            st.switch_page("pages/9_AI_Assistant.py")
        
        # Survey Dispatch
        if st.sidebar.button("📋 Survey Dispatch", use_container_width=True):
            st.switch_page("pages/10_Survey_Dispatch.py")
        
        # IoT Integration
        if st.sidebar.button("📡 IoT Integration", use_container_width=True):
            st.switch_page("pages/11_IoT_Integration.py")
        
        # Footer
        st.markdown("---")
        st.markdown("<div style='text-align: center; color: #888; font-size: 0.8rem;'>Carbon Aegis v1.0.0</div>", unsafe_allow_html=True)
        
        # If not onboarded yet, add a button to start
        if not st.session_state.get('onboarding_complete', False):
            st.sidebar.markdown("---")
            if st.sidebar.button("✨ Complete Onboarding", use_container_width=True):
                st.switch_page("pages/0_Onboarding.py")


def render_page_header(title, subtitle=None, show_logo=True):
    """
    Renders a consistent page header across all pages
    
    Parameters:
    -----------
    title : str
        The main page title
    subtitle : str, optional
        An optional subtitle for the page
    show_logo : bool, default=True
        Whether to show the logo in the header
    """
    if show_logo:
        col1, col2 = st.columns([1, 5])
        with col1:
            st.image("assets/logo.png", width=80)
        with col2:
            st.markdown(f"<h1 style='margin-bottom: 0;'>{title}</h1>", unsafe_allow_html=True)
            if subtitle:
                st.markdown(f"<p style='color: #666; margin-top: 0;'>{subtitle}</p>", unsafe_allow_html=True)
    else:
        st.markdown(f"<h1 style='margin-bottom: 0;'>{title}</h1>", unsafe_allow_html=True)
        if subtitle:
            st.markdown(f"<p style='color: #666; margin-top: 0;'>{subtitle}</p>", unsafe_allow_html=True)
    
    # Add a subtle divider
    st.markdown("<hr style='margin: 1rem 0; opacity: 0.3;'>", unsafe_allow_html=True)


def create_feature_card(icon, title, description, button_text, page_link, key_prefix):
    """
    Creates a feature card with consistent styling
    
    Parameters:
    -----------
    icon : str
        Emoji or icon to display
    title : str
        Card title
    description : str
        Card description
    button_text : str
        Text to display on the button
    page_link : str
        Page to navigate to when button is clicked
    key_prefix : str
        Prefix for the button key
    """
    st.markdown(f"""
    <div style="background-color: white; border-radius: 10px; padding: 20px; height: 100%; box-shadow: 0 4px 6px rgba(0,0,0,0.05);">
        <div style="font-size: 2.5rem; color: #2E8B57; margin-bottom: 10px;">{icon}</div>
        <div style="font-weight: 600; font-size: 1.2rem; margin-bottom: 0.5rem; color: #333;">{title}</div>
        <div style="color: #666; font-size: 0.9rem; margin-bottom: 1rem;">{description}</div>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button(button_text, key=f"{key_prefix}_{title.lower().replace(' ', '_')}", use_container_width=True):
        st.switch_page(page_link)