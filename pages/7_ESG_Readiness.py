import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.data_manager import init_session_state

# Initialize session state
init_session_state()

# Add Carbon Aegis branding
col1, col2 = st.columns([1, 5])
with col1:
    st.image("assets/logo.png", width=100)
with col2:
    st.title("Carbon Aegis - ESG Readiness Assessment")

st.markdown("""
This tool helps your organization assess its readiness for ESG reporting and sustainability initiatives 
through a targeted questionnaire covering key ESG dimensions.
""")

# Initialize assessment state variables
if 'esg_assessment_started' not in st.session_state:
    st.session_state.esg_assessment_started = False
if 'esg_assessment_completed' not in st.session_state:
    st.session_state.esg_assessment_completed = False
if 'esg_assessment_answers' not in st.session_state:
    st.session_state.esg_assessment_answers = {}
if 'esg_assessment_score' not in st.session_state:
    st.session_state.esg_assessment_score = {
        'Environmental': 0,
        'Social': 0,
        'Governance': 0,
        'Total': 0
    }

# Define assessment questions
assessment_questions = {
    'Environmental': [
        {
            'id': 'env_1',
            'question': 'Does your organization have a formal environmental policy?',
            'options': ['Yes, comprehensive and regularly reviewed', 'Yes, but limited in scope', 'In development', 'No'],
            'weights': [3, 2, 1, 0]
        },
        {
            'id': 'env_2',
            'question': 'Does your organization track its emissions (Scope 1, 2, and/or 3)?',
            'options': ['Yes, all scopes comprehensively', 'Yes, but only Scope 1 and 2', 'Only basic tracking', 'No tracking'],
            'weights': [3, 2, 1, 0]
        },
        {
            'id': 'env_3',
            'question': 'Has your organization set specific carbon reduction targets?',
            'options': ['Yes, science-based targets', 'Yes, non-science-based targets', 'Informal targets only', 'No targets'],
            'weights': [3, 2, 1, 0]
        },
        {
            'id': 'env_4',
            'question': 'Does your organization have waste management and recycling programs?',
            'options': ['Yes, comprehensive with metrics', 'Yes, basic program', 'Limited initiatives', 'No program'],
            'weights': [3, 2, 1, 0]
        }
    ],
    'Social': [
        {
            'id': 'soc_1',
            'question': 'Does your organization have diversity and inclusion policies?',
            'options': ['Yes, comprehensive with targets and metrics', 'Yes, written policies', 'Informal practices only', 'No policies'],
            'weights': [3, 2, 1, 0]
        },
        {
            'id': 'soc_2',
            'question': 'Does your organization regularly assess employee satisfaction?',
            'options': ['Yes, regular formal surveys with action plans', 'Yes, occasional surveys', 'Informal feedback only', 'No assessment'],
            'weights': [3, 2, 1, 0]
        },
        {
            'id': 'soc_3',
            'question': 'Does your organization have a supplier code of conduct that includes ESG criteria?',
            'options': ['Yes, comprehensive with verification', 'Yes, basic requirements', 'In development', 'No'],
            'weights': [3, 2, 1, 0]
        }
    ],
    'Governance': [
        {
            'id': 'gov_1',
            'question': 'Does your organization have board oversight of ESG issues?',
            'options': ['Yes, dedicated committee', 'Yes, part of existing committee', 'Ad-hoc oversight', 'No oversight'],
            'weights': [3, 2, 1, 0]
        },
        {
            'id': 'gov_2',
            'question': 'Does your organization have a formal ESG reporting process?',
            'options': ['Yes, following recognized standards', 'Yes, but not standardized', 'Ad-hoc reporting', 'No reporting'],
            'weights': [3, 2, 1, 0]
        },
        {
            'id': 'gov_3',
            'question': 'Does your organization have policies on business ethics and anti-corruption?',
            'options': ['Yes, comprehensive with training', 'Yes, documented policies', 'Basic policies only', 'No policies'],
            'weights': [3, 2, 1, 0]
        }
    ]
}

# Start assessment button
if not st.session_state.esg_assessment_started and not st.session_state.esg_assessment_completed:
    st.subheader("ESG Readiness Assessment")
    st.markdown("""
    This assessment consists of 10 questions across Environmental, Social, and Governance dimensions.
    Your answers will help identify your organization's ESG maturity level and provide targeted recommendations.
    """)
    
    # Add organization input fields
    if 'organization_name' not in st.session_state or not st.session_state.organization_name:
        org_name = st.text_input("Organization Name", placeholder="Enter your organization name")
        if org_name:
            st.session_state.organization_name = org_name
    
    if st.button("Start Assessment", use_container_width=True):
        st.session_state.esg_assessment_started = True
        st.rerun()

# Display assessment questions
elif st.session_state.esg_assessment_started and not st.session_state.esg_assessment_completed:
    st.subheader("ESG Readiness Assessment Questionnaire")
    
    # Create form for all questions
    with st.form("esg_assessment_form"):
        # Environmental questions
        st.markdown("### Environmental Factors")
        for q in assessment_questions['Environmental']:
            response = st.radio(
                q['question'],
                options=q['options'],
                key=q['id']
            )
            st.session_state.esg_assessment_answers[q['id']] = {
                'question': q['question'],
                'answer': response,
                'weight': q['weights'][q['options'].index(response)]
            }
        
        # Social questions
        st.markdown("### Social Factors")
        for q in assessment_questions['Social']:
            response = st.radio(
                q['question'],
                options=q['options'],
                key=q['id']
            )
            st.session_state.esg_assessment_answers[q['id']] = {
                'question': q['question'],
                'answer': response,
                'weight': q['weights'][q['options'].index(response)]
            }
        
        # Governance questions
        st.markdown("### Governance Factors")
        for q in assessment_questions['Governance']:
            response = st.radio(
                q['question'],
                options=q['options'],
                key=q['id']
            )
            st.session_state.esg_assessment_answers[q['id']] = {
                'question': q['question'],
                'answer': response,
                'weight': q['weights'][q['options'].index(response)]
            }
        
        # Submit button
        submit_button = st.form_submit_button("Complete Assessment", use_container_width=True)
        
        if submit_button:
            # Calculate scores
            env_score = sum(st.session_state.esg_assessment_answers[q['id']]['weight'] for q in assessment_questions['Environmental'])
            env_max = sum(q['weights'][0] for q in assessment_questions['Environmental'])
            
            soc_score = sum(st.session_state.esg_assessment_answers[q['id']]['weight'] for q in assessment_questions['Social'])
            soc_max = sum(q['weights'][0] for q in assessment_questions['Social'])
            
            gov_score = sum(st.session_state.esg_assessment_answers[q['id']]['weight'] for q in assessment_questions['Governance'])
            gov_max = sum(q['weights'][0] for q in assessment_questions['Governance'])
            
            # Normalize scores to percentage
            st.session_state.esg_assessment_score['Environmental'] = round((env_score / env_max) * 100)
            st.session_state.esg_assessment_score['Social'] = round((soc_score / soc_max) * 100)
            st.session_state.esg_assessment_score['Governance'] = round((gov_score / gov_max) * 100)
            
            # Calculate total score
            total_score = env_score + soc_score + gov_score
            total_max = env_max + soc_max + gov_max
            st.session_state.esg_assessment_score['Total'] = round((total_score / total_max) * 100)
            
            # Mark assessment as completed
            st.session_state.esg_assessment_completed = True
            st.rerun()

# Display assessment results
elif st.session_state.esg_assessment_completed:
    st.subheader("ESG Readiness Assessment Results")
    
    if st.session_state.organization_name:
        st.markdown(f"**Organization:** {st.session_state.organization_name}")
    
    # Display overall score
    total_score = st.session_state.esg_assessment_score['Total']
    
    # Create gauge chart for overall score
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=total_score,
        title={'text': "Overall ESG Readiness"},
        gauge={
            'axis': {'range': [0, 100]},
            'bar': {'color': "darkgreen"},
            'steps': [
                {'range': [0, 30], 'color': "red"},
                {'range': [30, 70], 'color': "yellow"},
                {'range': [70, 100], 'color': "green"},
            ],
            'threshold': {
                'line': {'color': "black", 'width': 4},
                'thickness': 0.75,
                'value': total_score
            }
        }
    ))
    
    fig.update_layout(
        height=300,
        margin=dict(l=30, r=30, t=50, b=30),
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Display maturity level
    maturity_level = "Beginning"
    if total_score >= 75:
        maturity_level = "Advanced"
    elif total_score >= 50:
        maturity_level = "Established"
    elif total_score >= 25:
        maturity_level = "Developing"
    
    st.markdown(f"### ESG Maturity Level: **{maturity_level}**")
    
    # Show breakdown by category
    st.markdown("### Readiness by ESG Category")
    
    category_scores = {
        'Category': ['Environmental', 'Social', 'Governance'],
        'Score': [
            st.session_state.esg_assessment_score['Environmental'],
            st.session_state.esg_assessment_score['Social'],
            st.session_state.esg_assessment_score['Governance']
        ]
    }
    
    df = pd.DataFrame(category_scores)
    
    # Create bar chart for category scores
    fig_bar = px.bar(
        df, 
        x='Category', 
        y='Score',
        color='Score',
        color_continuous_scale=['red', 'yellow', 'green'],
        range_color=[0, 100],
        text='Score',
        title="ESG Category Scores"
    )
    
    fig_bar.update_traces(texttemplate='%{text}%', textposition='outside')
    fig_bar.update_layout(
        uniformtext_minsize=8,
        uniformtext_mode='hide',
        yaxis_title="Score (%)",
        yaxis_range=[0, 100],
        height=400
    )
    
    st.plotly_chart(fig_bar, use_container_width=True)
    
    # Show detailed recommendations
    st.markdown("## Recommended Actions")
    
    # Environmental recommendations
    env_score = st.session_state.esg_assessment_score['Environmental']
    st.markdown("### Environmental")
    if env_score < 40:
        st.markdown("""
        * **Develop a formal environmental policy** to guide your sustainability efforts
        * **Implement basic emissions tracking** for Scope 1 and 2 emissions
        * **Establish waste management procedures** and track basic metrics
        """)
    elif env_score < 70:
        st.markdown("""
        * **Expand emissions tracking** to include Scope 3 emissions
        * **Set formal carbon reduction targets** with clear timelines
        * **Enhance waste management program** with comprehensive metrics
        * **Consider environmental certifications** such as ISO 14001
        """)
    else:
        st.markdown("""
        * **Implement science-based targets** for emissions reductions
        * **Pursue advanced environmental certifications**
        * **Develop a comprehensive climate risk assessment**
        * **Explore renewable energy investments** and carbon offsets
        """)
    
    # Social recommendations
    soc_score = st.session_state.esg_assessment_score['Social']
    st.markdown("### Social")
    if soc_score < 40:
        st.markdown("""
        * **Develop formal diversity and inclusion policies**
        * **Implement regular employee satisfaction surveys**
        * **Create a basic supplier code of conduct**
        """)
    elif soc_score < 70:
        st.markdown("""
        * **Set diversity targets** with measurable metrics
        * **Implement comprehensive employee feedback programs**
        * **Enhance supplier assessments** to include ESG criteria
        * **Develop community engagement initiatives**
        """)
    else:
        st.markdown("""
        * **Implement advanced diversity and inclusion programs**
        * **Develop comprehensive social impact measurements**
        * **Implement supplier ESG audits and verification**
        * **Create strategic community investment programs**
        """)
    
    # Governance recommendations
    gov_score = st.session_state.esg_assessment_score['Governance']
    st.markdown("### Governance")
    if gov_score < 40:
        st.markdown("""
        * **Establish board-level oversight** of ESG issues
        * **Develop a formal ESG reporting process**
        * **Create comprehensive ethics and anti-corruption policies**
        """)
    elif gov_score < 70:
        st.markdown("""
        * **Create a dedicated ESG committee** at the board level
        * **Implement standardized ESG reporting frameworks**
        * **Enhance ethics training programs** for all employees
        * **Develop a formal ESG risk assessment process**
        """)
    else:
        st.markdown("""
        * **Integrate ESG metrics into executive compensation**
        * **Implement advanced ESG risk management systems**
        * **Pursue external ESG rating assessments**
        * **Develop industry-leading transparency initiatives**
        """)
    
    # Next steps
    st.markdown("## Next Steps")
    st.markdown("""
    Based on your assessment results, we recommend focusing on the areas with the lowest scores first.
    Your Carbon Aegis dashboard provides tools to help address these recommendations:
    
    1. **Track and reduce emissions** with the emissions calculator
    2. **Find applicable reporting frameworks** with the Framework Finder
    3. **Generate comprehensive reports** with the Report Generator
    
    For assistance implementing these recommendations, use the Resources section below.
    """)
    
    # Reset button
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Retake Assessment", use_container_width=True):
            # Reset assessment
            st.session_state.esg_assessment_started = False
            st.session_state.esg_assessment_completed = False
            st.session_state.esg_assessment_answers = {}
            st.session_state.esg_assessment_score = {
                'Environmental': 0,
                'Social': 0,
                'Governance': 0,
                'Total': 0
            }
            st.rerun()
    
    with col2:
        if st.button("Return to Dashboard", use_container_width=True):
            st.switch_page("pages/6_ESG_Dashboard.py")
    
    # Resources
    st.markdown("## Resources")
    with st.expander("ESG Reporting Standards and Frameworks"):
        st.markdown("""
        * [Global Reporting Initiative (GRI)](https://www.globalreporting.org/)
        * [Sustainability Accounting Standards Board (SASB)](https://www.sasb.org/)
        * [Task Force on Climate-related Financial Disclosures (TCFD)](https://www.fsb-tcfd.org/)
        * [CDP (formerly Carbon Disclosure Project)](https://www.cdp.net/)
        * [Corporate Sustainability Reporting Directive (CSRD)](https://finance.ec.europa.eu/capital-markets-union-and-financial-markets/company-reporting-and-auditing/company-reporting/corporate-sustainability-reporting_en)
        """)

# Add navigation after all content
st.markdown("---")
col1, col2, col3 = st.columns([1, 1, 1])
with col1:
    if st.button("📊 ESG Dashboard", use_container_width=True):
        st.switch_page("pages/6_ESG_Dashboard.py")
with col2:
    if st.button("📏 Framework Finder", use_container_width=True):
        st.switch_page("pages/5_Framework_Finder.py")
with col3:
    if st.button("🏠 Home", use_container_width=True):
        st.switch_page("app.py")