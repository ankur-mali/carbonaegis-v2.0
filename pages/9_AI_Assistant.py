import streamlit as st
import os
import sys

# Add parent directory to path to import utils
sys.path.append('..')
from utils.ai_assistant import generate_ai_response

# Page configuration
st.set_page_config(
    page_title="AI Assistant | Carbon Aegis",
    page_icon="🤖",
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
    .chat-message {
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        display: flex;
        flex-direction: column;
    }
    .chat-message.user {
        background-color: #f4f4f4;
        border-left: 5px solid #0f62fe;
    }
    .chat-message.assistant {
        background-color: #edf5ff;
        border-left: 5px solid #33b1ff;
    }
    .avatar {
        width: 2.5rem;
        height: 2.5rem;
        border-radius: 50%;
        object-fit: cover;
        margin-right: 1rem;
    }
    .chat-header {
        display: flex;
        align-items: center;
        margin-bottom: 0.5rem;
        font-weight: bold;
    }
    .logo-container {
        margin-bottom: 2rem;
    }
    .logo-container img {
        max-height: 60px;
    }
    </style>
    """, unsafe_allow_html=True)

# Initialize session state for chat history
def init_session_state():
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'organization_context' not in st.session_state:
        st.session_state.organization_context = {
            "industry": None,
            "size": None,
            "region": None,
            "current_emissions": None
        }

# Generate a fallback response when API is unavailable
def generate_fallback_response(query, context):
    """
    Generate a fallback response based on predefined templates when the AI API is unavailable.
    """
    # Check for common question types
    query_lower = query.lower()
    
    if "calculate" in query_lower and "emissions" in query_lower:
        return """
        To calculate emissions correctly:
        
        1. Identify your emission sources (electricity, fuel, business travel, etc.)
        2. Collect activity data (kWh, liters, km traveled)
        3. Apply appropriate emission factors from recognized sources like EPA, DEFRA, or IEA
        4. Calculate using the formula: Activity data × Emission factor = Emissions (CO2e)
        5. Separate your calculations by scope (1, 2, and 3)
        
        The Carbon Aegis platform automates much of this process when you upload your data.
        """
    
    elif "reduce" in query_lower and ("emissions" in query_lower or "carbon" in query_lower):
        return """
        Effective emission reduction strategies include:
        
        1. Energy efficiency improvements in facilities and operations
        2. Renewable energy adoption through on-site generation or purchasing
        3. Fleet electrification and sustainable transportation policies
        4. Supply chain engagement to address Scope 3 emissions
        5. Process optimization to reduce waste and resource consumption
        
        Start with a baseline assessment to identify your largest emission sources, then prioritize actions that target these areas.
        """
    
    elif "framework" in query_lower or "reporting" in query_lower:
        return """
        Key ESG reporting frameworks include:
        
        1. GHG Protocol - The foundation for emissions accounting
        2. TCFD - For climate-related financial disclosures
        3. CDP - Global disclosure system for environmental impacts
        4. GRI - Comprehensive sustainability reporting standards
        5. SASB - Industry-specific sustainability standards
        
        The most appropriate framework depends on your industry, stakeholders, and regulatory requirements. Many organizations use multiple frameworks in combination.
        """
    
    elif "net zero" in query_lower or "carbon neutral" in query_lower:
        return """
        Achieving net zero emissions requires:
        
        1. Measuring your complete carbon footprint across all scopes
        2. Setting science-based reduction targets aligned with 1.5°C pathways
        3. Implementing deep decarbonization across operations and value chain
        4. Using high-quality carbon removals only for residual emissions
        5. Regularly reporting progress and updating strategies
        
        Unlike carbon neutrality, net zero requires actual emission reductions rather than primarily relying on offsets.
        """
    
    else:
        return """
        I understand you're asking about sustainability and emissions management. While I don't have specific information on your query, here are some general recommendations:

        1. Follow GHG Protocol standards for emissions accounting
        2. Focus on material issues for your industry sector
        3. Set science-based targets for emissions reduction
        4. Implement robust data collection processes
        5. Engage stakeholders in your sustainability journey

        For more specific guidance, try asking about emissions calculation, reduction strategies, reporting frameworks, or regulatory compliance.
        """

# Main function
def main():
    add_custom_css()
    init_session_state()
    
    # Display logo
    st.image("assets/logo.png", width=180)
    
    st.title("Terra ESG AI Assistant")
    st.write("Ask questions about sustainability, ESG reporting, emissions calculations, and more.")
    
    # Organization context form (collapsible)
    with st.expander("Provide Organization Context (Optional)"):
        st.write("Help the AI provide more relevant responses by sharing details about your organization.")
        
        col1, col2 = st.columns(2)
        with col1:
            industry = st.selectbox(
                "Industry Sector",
                options=[None, "Manufacturing", "Technology", "Finance", "Energy", "Retail", 
                        "Healthcare", "Transportation", "Food & Beverage", "Construction", "Other"],
                index=0
            )
            
            size = st.selectbox(
                "Organization Size",
                options=[None, "Small (<50 employees)", "Medium (50-250 employees)", "Large (>250 employees)"],
                index=0
            )
        
        with col2:
            region = st.selectbox(
                "Primary Region of Operation",
                options=[None, "North America", "Europe", "Asia-Pacific", "Latin America", 
                        "Middle East & Africa", "Global"],
                index=0
            )
            
            current_emissions = st.selectbox(
                "Current Emissions Tracking",
                options=[None, "Not tracking yet", "Scope 1 only", "Scope 1 & 2", "Scope 1, 2 & 3 (partial)", 
                        "Comprehensive Scope 1, 2 & 3"],
                index=0
            )
        
        if st.button("Update Context"):
            st.session_state.organization_context = {
                "industry": industry,
                "size": size,
                "region": region,
                "current_emissions": current_emissions
            }
            st.success("Context updated successfully!")
    
    # Chat interface
    st.markdown("---")
    
    # Display chat history
    for message in st.session_state.chat_history:
        role = message["role"]
        content = message["content"]
        
        if role == "user":
            st.markdown(f"""
            <div class="chat-message user">
                <div class="chat-header">
                    <span>You</span>
                </div>
                <div class="message-content">
                    {content}
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="chat-message assistant">
                <div class="chat-header">
                    <span>Terra ESG Assistant</span>
                </div>
                <div class="message-content">
                    {content}
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    # Input for new message
    with st.form("chat_input_form", clear_on_submit=True):
        user_input = st.text_area("Your question:", height=100)
        submitted = st.form_submit_button("Ask Terra ESG")
        
        if submitted and user_input:
            # Add user message to chat history
            st.session_state.chat_history.append({
                "role": "user",
                "content": user_input
            })
            
            # Check for OpenAI API key
            api_key = os.environ.get("OPENAI_API_KEY")
            
            # Generate response
            if api_key:
                with st.spinner("Generating response..."):
                    response = generate_ai_response(user_input, st.session_state.organization_context)
            else:
                response = generate_fallback_response(user_input, st.session_state.organization_context)
                st.warning("Using built-in responses. For more accurate and customized AI responses, please add your OpenAI API key.")
            
            # Add assistant response to chat history
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": response
            })
            
            # Refresh the page to show new messages
            st.rerun()
    
    # Clear chat button
    if st.session_state.chat_history:
        if st.button("Clear Chat History"):
            st.session_state.chat_history = []
            st.rerun()

if __name__ == "__main__":
    main()