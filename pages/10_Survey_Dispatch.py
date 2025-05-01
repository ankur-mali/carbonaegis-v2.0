import streamlit as st
import pandas as pd
import json
import uuid
from datetime import datetime
from utils.data_manager import init_session_state

# Initialize session state
init_session_state()

# Add Carbon Aegis branding
col1, col2 = st.columns([1, 5])
with col1:
    st.image("assets/logo.png", width=100)
with col2:
    st.title("Carbon Aegis - Survey Dispatch")

st.markdown("""
Create and distribute targeted ESG surveys to collect data from across your organization.
This tool helps you gather input from employees, suppliers, and stakeholders to improve your
ESG reporting and sustainability initiatives.
""")

# Initialize survey state variables
if 'surveys' not in st.session_state:
    st.session_state.surveys = []
if 'survey_responses' not in st.session_state:
    st.session_state.survey_responses = {}
if 'active_survey_id' not in st.session_state:
    st.session_state.active_survey_id = None
if 'view_mode' not in st.session_state:
    st.session_state.view_mode = "list"  # list, create, view, results

# Predefined survey templates
survey_templates = {
    "Employee Commuting": {
        "title": "Employee Commuting Survey",
        "description": "This survey collects data on employee commuting patterns to calculate Scope 3 emissions.",
        "target_audience": "All employees",
        "questions": [
            {
                "id": "ec_1",
                "type": "select",
                "question": "What is your primary mode of transportation to work?",
                "options": ["Car (solo driver)", "Carpool", "Public transportation", "Bicycle", "Walking", "Work from home"],
                "required": True
            },
            {
                "id": "ec_2",
                "type": "number",
                "question": "What is your one-way commute distance in kilometers?",
                "required": True
            },
            {
                "id": "ec_3",
                "type": "select",
                "question": "How many days per week do you typically commute to the office?",
                "options": ["1", "2", "3", "4", "5", "More than 5"],
                "required": True
            },
            {
                "id": "ec_4",
                "type": "select",
                "question": "If you drive, what type of vehicle do you use?",
                "options": ["Gasoline car", "Diesel car", "Hybrid", "Electric vehicle", "Motorcycle/Scooter", "I don't drive"],
                "required": False
            },
            {
                "id": "ec_5",
                "type": "multiselect",
                "question": "What would encourage you to use more sustainable transportation?",
                "options": ["Public transit subsidies", "Bicycle facilities", "EV charging stations", "Carpool incentives", "Flexible work options"],
                "required": False
            }
        ]
    },
    "Supplier Assessment": {
        "title": "Supplier Sustainability Assessment",
        "description": "This survey evaluates the sustainability practices of your suppliers for Scope 3 emissions reporting.",
        "target_audience": "Suppliers and vendors",
        "questions": [
            {
                "id": "sa_1",
                "type": "select",
                "question": "Does your company have a formal environmental or sustainability policy?",
                "options": ["Yes, comprehensive", "Yes, basic", "In development", "No"],
                "required": True
            },
            {
                "id": "sa_2",
                "type": "select",
                "question": "Do you measure your greenhouse gas emissions?",
                "options": ["Yes, all scopes", "Yes, scope 1 and 2 only", "Partially", "No"],
                "required": True
            },
            {
                "id": "sa_3",
                "type": "select",
                "question": "Do you have emission reduction targets?",
                "options": ["Yes, science-based targets", "Yes, but not science-based", "In development", "No"],
                "required": True
            },
            {
                "id": "sa_4",
                "type": "multiselect",
                "question": "Which of the following practices do you implement?",
                "options": ["Energy efficiency measures", "Renewable energy use", "Waste reduction programs", "Water conservation", "Sustainable packaging"],
                "required": True
            },
            {
                "id": "sa_5",
                "type": "text",
                "question": "What is your primary environmental challenge in your operations?",
                "required": False
            }
        ]
    },
    "Waste Audit": {
        "title": "Workplace Waste Audit",
        "description": "This survey assesses waste generation and recycling practices to improve resource efficiency.",
        "target_audience": "Facility managers and operations staff",
        "questions": [
            {
                "id": "wa_1",
                "type": "number",
                "question": "Approximately how much general waste is produced monthly at your location (in kg)?",
                "required": True
            },
            {
                "id": "wa_2",
                "type": "number",
                "question": "Approximately how much recycled material is collected monthly (in kg)?",
                "required": True
            },
            {
                "id": "wa_3",
                "type": "multiselect",
                "question": "Which materials do you currently recycle?",
                "options": ["Paper", "Cardboard", "Plastic", "Glass", "Metal", "E-waste", "Organic waste"],
                "required": True
            },
            {
                "id": "wa_4",
                "type": "select",
                "question": "How would you rate your current waste management practices?",
                "options": ["Excellent", "Good", "Adequate", "Needs improvement", "Poor"],
                "required": True
            },
            {
                "id": "wa_5",
                "type": "text",
                "question": "What are the main barriers to reducing waste at your location?",
                "required": False
            }
        ]
    },
    "Energy Consumption": {
        "title": "Energy Consumption Survey",
        "description": "This survey collects data on energy usage to calculate Scope 1 and 2 emissions.",
        "target_audience": "Facility managers and operations staff",
        "questions": [
            {
                "id": "en_1",
                "type": "number",
                "question": "What is your monthly electricity consumption (in kWh)?",
                "required": True
            },
            {
                "id": "en_2",
                "type": "number",
                "question": "What is your monthly natural gas consumption (in m³), if applicable?",
                "required": False
            },
            {
                "id": "en_3",
                "type": "select",
                "question": "Do you purchase renewable energy?",
                "options": ["Yes, 100%", "Yes, partially", "No, but interested", "No"],
                "required": True
            },
            {
                "id": "en_4",
                "type": "multiselect",
                "question": "Which energy efficiency measures have you implemented?",
                "options": ["LED lighting", "Smart controls/sensors", "HVAC optimization", "Building insulation", "Energy-efficient equipment", "None"],
                "required": True
            },
            {
                "id": "en_5",
                "type": "text",
                "question": "What are your biggest challenges in reducing energy consumption?",
                "required": False
            }
        ]
    },
    "Custom Survey": {
        "title": "Custom Sustainability Survey",
        "description": "Build your own custom sustainability survey.",
        "target_audience": "Custom audience",
        "questions": [
            {
                "id": "custom_1",
                "type": "text",
                "question": "Your first question here",
                "required": True
            }
        ]
    }
}

# Main navigation for survey management
if st.session_state.view_mode == "list":
    # Survey list view
    st.subheader("Survey Management")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.write("Create and manage your sustainability data collection surveys")
    with col2:
        if st.button("+ Create New Survey", use_container_width=True):
            st.session_state.view_mode = "create"
            st.rerun()
    
    # Display existing surveys
    if not st.session_state.surveys:
        st.info("No surveys created yet. Click 'Create New Survey' to get started.")
    else:
        for i, survey in enumerate(st.session_state.surveys):
            with st.container(border=True):
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    st.markdown(f"**{survey['title']}**")
                    st.markdown(f"*{survey['description']}*")
                    st.markdown(f"Target audience: {survey['target_audience']}")
                    st.markdown(f"Created: {survey['created_at']} | Status: {survey['status']}")
                
                with col2:
                    if st.button("View Details", key=f"view_{i}", use_container_width=True):
                        st.session_state.active_survey_id = survey['id']
                        st.session_state.view_mode = "view"
                        st.rerun()
                
                with col3:
                    if survey['status'] == "Active":
                        if st.button("View Results", key=f"results_{i}", use_container_width=True):
                            st.session_state.active_survey_id = survey['id']
                            st.session_state.view_mode = "results"
                            st.rerun()

elif st.session_state.view_mode == "create":
    # Survey creation view
    st.subheader("Create New Survey")
    
    # Template selection
    template_name = st.selectbox(
        "Choose a survey template or create a custom survey:",
        options=list(survey_templates.keys()),
        index=0
    )
    
    template = survey_templates[template_name].copy()
    
    # Survey details form
    with st.form("create_survey_form"):
        # Basic info
        title = st.text_input("Survey Title", value=template["title"])
        description = st.text_area("Description", value=template["description"])
        target_audience = st.text_input("Target Audience", value=template["target_audience"])
        
        # Allow customizing questions if using a template
        st.subheader("Survey Questions")
        
        # Clone template questions to avoid modifying the original
        questions = []
        for q in template["questions"]:
            questions.append(q.copy())
        
        # Display and allow editing of questions
        for i, question in enumerate(questions):
            with st.expander(f"Question {i+1}: {question['question']}", expanded=i==0):
                question_text = st.text_input("Question", value=question["question"], key=f"q_text_{i}")
                question["question"] = question_text
                
                question_type = st.selectbox(
                    "Question Type", 
                    options=["text", "number", "select", "multiselect"], 
                    index=["text", "number", "select", "multiselect"].index(question["type"]),
                    key=f"q_type_{i}"
                )
                question["type"] = question_type
                
                if question_type in ["select", "multiselect"]:
                    if "options" in question:
                        options_str = st.text_area(
                            "Options (one per line)", 
                            value="\n".join(question["options"]),
                            key=f"q_options_{i}"
                        )
                    else:
                        options_str = st.text_area(
                            "Options (one per line)", 
                            value="Option 1\nOption 2\nOption 3",
                            key=f"q_options_{i}"
                        )
                    
                    question["options"] = [opt.strip() for opt in options_str.split("\n") if opt.strip()]
                
                question["required"] = st.checkbox("Required", value=question.get("required", False), key=f"q_req_{i}")
        
        # Option to add a new question
        if st.checkbox("Add Another Question"):
            new_q = {
                "id": f"q_{len(questions)+1}",
                "type": "text",
                "question": "New question",
                "required": False
            }
            questions.append(new_q)
        
        # Submit button
        create_survey = st.form_submit_button("Create Survey", use_container_width=True)
        
        if create_survey:
            if not title:
                st.error("Survey title is required.")
            else:
                # Create new survey object
                new_survey = {
                    "id": str(uuid.uuid4()),
                    "title": title,
                    "description": description,
                    "target_audience": target_audience,
                    "questions": questions,
                    "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "status": "Active",
                    "responses": 0
                }
                
                # Add to session state
                st.session_state.surveys.append(new_survey)
                st.session_state.view_mode = "view"
                st.session_state.active_survey_id = new_survey["id"]
                st.success("Survey created successfully!")
                st.rerun()
    
    # Cancel button
    if st.button("Cancel", use_container_width=True):
        st.session_state.view_mode = "list"
        st.rerun()

elif st.session_state.view_mode == "view":
    # View survey details and sharing options
    active_survey = next((s for s in st.session_state.surveys if s["id"] == st.session_state.active_survey_id), None)
    
    if not active_survey:
        st.error("Survey not found.")
        st.session_state.view_mode = "list"
        st.rerun()
    
    st.subheader(active_survey["title"])
    st.markdown(active_survey["description"])
    
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown(f"**Target audience:** {active_survey['target_audience']}")
        st.markdown(f"**Created:** {active_survey['created_at']}")
        st.markdown(f"**Status:** {active_survey['status']}")
        st.markdown(f"**Responses:** {active_survey.get('responses', 0)}")
    
    with col2:
        # Survey actions
        if active_survey["status"] == "Active":
            if st.button("View Results", use_container_width=True):
                st.session_state.view_mode = "results"
                st.rerun()
            
            if st.button("Deactivate Survey", use_container_width=True):
                for survey in st.session_state.surveys:
                    if survey["id"] == active_survey["id"]:
                        survey["status"] = "Inactive"
                st.success("Survey deactivated.")
                st.rerun()
        else:
            if st.button("Reactivate Survey", use_container_width=True):
                for survey in st.session_state.surveys:
                    if survey["id"] == active_survey["id"]:
                        survey["status"] = "Active"
                st.success("Survey reactivated.")
                st.rerun()
    
    # Distribution section
    st.subheader("Survey Distribution")
    st.markdown("""
    Use one of the following methods to distribute your survey:
    
    1. **Share link** - Send the unique survey link to your target audience
    2. **Email invitation** - Send email invitations to respondents (feature coming soon)
    3. **Export as PDF** - Download a printable version of the survey (feature coming soon)
    """)
    
    survey_link = f"https://your-carbon-aegis-domain.com/survey/{active_survey['id']}"
    st.code(survey_link, language=None)
    
    st.markdown("For demonstration purposes, you can preview the survey interface here:")
    
    if st.button("Preview Survey", use_container_width=True):
        st.session_state.preview_survey = True
        st.rerun()
    
    # Survey preview
    if st.session_state.get('preview_survey', False):
        st.subheader("Survey Preview")
        with st.form("survey_preview_form"):
            st.write(active_survey["title"])
            st.write(active_survey["description"])
            
            for q in active_survey["questions"]:
                if q["type"] == "text":
                    st.text_input(f"{q['question']}{' *' if q['required'] else ''}", key=f"preview_{q['id']}")
                elif q["type"] == "number":
                    st.number_input(f"{q['question']}{' *' if q['required'] else ''}", min_value=0, key=f"preview_{q['id']}")
                elif q["type"] == "select":
                    st.selectbox(f"{q['question']}{' *' if q['required'] else ''}", options=q["options"], key=f"preview_{q['id']}")
                elif q["type"] == "multiselect":
                    st.multiselect(f"{q['question']}{' *' if q['required'] else ''}", options=q["options"], key=f"preview_{q['id']}")
            
            st.form_submit_button("Submit (Preview Only)")
        
        st.info("This is a preview only. Responses in preview mode are not recorded.")
        
        if st.button("Close Preview", use_container_width=True):
            st.session_state.preview_survey = False
            st.rerun()
    
    # Show survey questions
    st.subheader("Survey Questions")
    for i, q in enumerate(active_survey["questions"]):
        with st.expander(f"Question {i+1}: {q['question']}"):
            st.write(f"**Type:** {q['type']}")
            st.write(f"**Required:** {'Yes' if q['required'] else 'No'}")
            
            if q["type"] in ["select", "multiselect"]:
                st.write("**Options:**")
                for opt in q["options"]:
                    st.write(f"- {opt}")
    
    # Back button
    if st.button("Back to Survey List", use_container_width=True):
        st.session_state.view_mode = "list"
        st.session_state.preview_survey = False
        st.rerun()

elif st.session_state.view_mode == "results":
    # View survey results
    active_survey = next((s for s in st.session_state.surveys if s["id"] == st.session_state.active_survey_id), None)
    
    if not active_survey:
        st.error("Survey not found.")
        st.session_state.view_mode = "list"
        st.rerun()
    
    st.subheader(f"Results: {active_survey['title']}")
    
    # For demo purposes, generate some sample responses
    if active_survey["id"] not in st.session_state.survey_responses:
        # Create sample responses
        num_responses = 8
        sample_responses = []
        
        for i in range(num_responses):
            response = {
                "response_id": f"resp_{i+1}",
                "timestamp": (datetime.now()).strftime("%Y-%m-%d %H:%M"),
                "respondent": f"respondent_{i+1}@example.com",
                "answers": {}
            }
            
            for q in active_survey["questions"]:
                if q["type"] == "text":
                    response["answers"][q["id"]] = f"Sample text response {i+1}"
                elif q["type"] == "number":
                    response["answers"][q["id"]] = i * 10 + 5
                elif q["type"] == "select":
                    response["answers"][q["id"]] = q["options"][i % len(q["options"])]
                elif q["type"] == "multiselect":
                    response["answers"][q["id"]] = [q["options"][j] for j in range(len(q["options"])) if j % (i+2) == 0]
            
            sample_responses.append(response)
        
        st.session_state.survey_responses[active_survey["id"]] = sample_responses
        
        # Update the response count
        for survey in st.session_state.surveys:
            if survey["id"] == active_survey["id"]:
                survey["responses"] = len(sample_responses)
    
    # Display response summary
    responses = st.session_state.survey_responses.get(active_survey["id"], [])
    
    st.markdown(f"**Total Responses:** {len(responses)}")
    st.markdown(f"**Response Rate:** {'N/A - Demo Data'}")
    
    # Results analysis
    if responses:
        st.subheader("Response Summary")
        
        # Process results for visualization
        for i, q in enumerate(active_survey["questions"]):
            with st.expander(f"Question {i+1}: {q['question']}", expanded=i==0):
                if q["type"] == "text":
                    # For text questions, show a list of responses
                    st.markdown("**Text Responses:**")
                    for r in responses:
                        if q["id"] in r["answers"]:
                            st.markdown(f"- {r['answers'][q['id']]}")
                
                elif q["type"] == "number":
                    # For numeric questions, show statistics and a histogram
                    values = [r["answers"].get(q["id"], 0) for r in responses if q["id"] in r["answers"]]
                    
                    if values:
                        avg = sum(values) / len(values)
                        minimum = min(values)
                        maximum = max(values)
                        
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Average", f"{avg:.2f}")
                        with col2:
                            st.metric("Minimum", f"{minimum}")
                        with col3:
                            st.metric("Maximum", f"{maximum}")
                        
                        # Create histogram
                        df = pd.DataFrame({q["question"]: values})
                        st.bar_chart(df)
                    else:
                        st.info("No numeric responses for this question.")
                
                elif q["type"] in ["select", "multiselect"]:
                    # For select/multiselect, count occurrences of each option
                    option_counts = {option: 0 for option in q["options"]}
                    
                    for r in responses:
                        if q["id"] in r["answers"]:
                            if q["type"] == "select":
                                answer = r["answers"][q["id"]]
                                if answer in option_counts:
                                    option_counts[answer] += 1
                            else:  # multiselect
                                for selected in r["answers"][q["id"]]:
                                    if selected in option_counts:
                                        option_counts[selected] += 1
                    
                    # Create chart
                    chart_data = pd.DataFrame({
                        "Option": list(option_counts.keys()),
                        "Count": list(option_counts.values())
                    })
                    
                    st.bar_chart(chart_data, x="Option", y="Count")
        
        # Export options
        st.subheader("Export Results")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Export to CSV (Coming Soon)", use_container_width=True, disabled=True):
                pass
        with col2:
            if st.button("Generate Report (Coming Soon)", use_container_width=True, disabled=True):
                pass
    else:
        st.info("No responses received yet.")
    
    # Emissions estimation (for relevant surveys)
    if active_survey["title"] == "Employee Commuting Survey":
        st.subheader("Emissions Estimation")
        st.info("Based on the survey responses, we can estimate the following emissions:")
        
        # Simulate emissions calculation
        total_commute_km = sum([r["answers"].get("ec_2", 0) * 2 * int(r["answers"].get("ec_3", "3").split()[0]) * 4 for r in responses])
        avg_emission_factor = 0.17  # kg CO2e per km (average)
        estimated_emissions = total_commute_km * avg_emission_factor / 1000  # tonnes
        
        st.metric("Estimated Annual Commuting Emissions", f"{estimated_emissions:.2f} tCO₂e")
        
        st.markdown("""
        **Methodology:**
        - Total distance calculated from all respondents' commuting patterns
        - Applied average emission factors based on transportation modes
        - Extrapolated to annual emissions (48 working weeks)
        
        **Next Steps:**
        - Update your Scope 3 emissions in the Carbon Aegis emissions calculator
        - Consider implementing sustainable commuting incentives based on survey feedback
        """)
    
    # Back buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Back to Survey Details", use_container_width=True):
            st.session_state.view_mode = "view"
            st.rerun()
    with col2:
        if st.button("Back to Survey List", use_container_width=True):
            st.session_state.view_mode = "list"
            st.rerun()

# Add navigation
st.markdown("---")
col1, col2, col3 = st.columns([1, 1, 1])
with col1:
    if st.button("📊 ESG Dashboard", use_container_width=True):
        st.switch_page("pages/6_ESG_Dashboard.py")
with col2:
    if st.button("👥 Team Workspace", use_container_width=True):
        st.switch_page("pages/8_Team_Workspace.py")
with col3:
    if st.button("🏠 Home", use_container_width=True):
        st.switch_page("app.py")