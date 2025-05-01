import streamlit as st
import pandas as pd
from datetime import datetime
from utils.data_manager import init_session_state

# Initialize session state
init_session_state()

# Add Carbon Aegis branding
col1, col2 = st.columns([1, 5])
with col1:
    st.image("assets/logo.png", width=100)
with col2:
    st.title("Carbon Aegis - Team Collaboration Workspace")

st.markdown("""
This workspace allows your team to collaborate on sustainability initiatives, 
track tasks, and manage your ESG reporting process efficiently.
""")

# Initialize team collaboration variables
if 'team_members' not in st.session_state:
    st.session_state.team_members = []
if 'tasks' not in st.session_state:
    st.session_state.tasks = []
if 'active_tab' not in st.session_state:
    st.session_state.active_tab = "Tasks"

# Tab navigation
tab1, tab2, tab3 = st.tabs(["Tasks", "Team Members", "Activity Log"])

# Tasks Management Tab
with tab1:
    st.subheader("Task Management")
    
    # Create task form
    with st.expander("Create New Task", expanded=len(st.session_state.tasks) == 0):
        with st.form("new_task_form"):
            task_title = st.text_input("Task Title", placeholder="Enter task title...")
            task_description = st.text_area("Description", placeholder="Describe the task...")
            
            col1, col2 = st.columns(2)
            with col1:
                task_type = st.selectbox(
                    "Task Type",
                    options=["General", "Emissions", "Framework", "Compliance"]
                )
            with col2:
                task_status = st.selectbox(
                    "Status",
                    options=["To Do", "In Progress", "Done"],
                    index=0
                )
            
            col1, col2 = st.columns(2)
            with col1:
                task_due_date = st.date_input("Due Date")
            with col2:
                task_priority = st.select_slider(
                    "Priority",
                    options=["Low", "Medium", "High"],
                    value="Medium"
                )
            
            # Get assignee from team members
            if st.session_state.team_members:
                assignee = st.selectbox(
                    "Assign To",
                    options=["Unassigned"] + [member['name'] for member in st.session_state.team_members],
                    index=0
                )
            else:
                assignee = "Unassigned"
                st.info("No team members available. Add team members in the Team Members tab.")
            
            submit_task = st.form_submit_button("Create Task")
            
            if submit_task and task_title:
                # Create a new task
                new_task = {
                    'id': len(st.session_state.tasks) + 1,
                    'title': task_title,
                    'description': task_description,
                    'type': task_type,
                    'status': task_status,
                    'priority': task_priority,
                    'due_date': task_due_date.strftime("%Y-%m-%d"),
                    'assignee': assignee,
                    'created_at': datetime.now().strftime("%Y-%m-%d %H:%M"),
                    'updated_at': datetime.now().strftime("%Y-%m-%d %H:%M")
                }
                
                st.session_state.tasks.append(new_task)
                st.success(f"Task '{task_title}' created successfully!")
                st.rerun()
    
    # Display tasks as kanban board
    if not st.session_state.tasks:
        st.info("No tasks have been created yet. Use the form above to create your first task.")
    else:
        st.subheader("Task Board")
        
        # Allow filtering tasks
        col1, col2, col3 = st.columns(3)
        with col1:
            filter_type = st.multiselect(
                "Filter by Type",
                options=["General", "Emissions", "Framework", "Compliance"],
                default=[]
            )
        with col2:
            filter_priority = st.multiselect(
                "Filter by Priority",
                options=["Low", "Medium", "High"],
                default=[]
            )
        with col3:
            if st.session_state.team_members:
                filter_assignee = st.multiselect(
                    "Filter by Assignee",
                    options=["Unassigned"] + [member['name'] for member in st.session_state.team_members],
                    default=[]
                )
            else:
                filter_assignee = []
        
        # Apply filters
        filtered_tasks = st.session_state.tasks
        if filter_type:
            filtered_tasks = [task for task in filtered_tasks if task['type'] in filter_type]
        if filter_priority:
            filtered_tasks = [task for task in filtered_tasks if task['priority'] in filter_priority]
        if filter_assignee:
            filtered_tasks = [task for task in filtered_tasks if task['assignee'] in filter_assignee]
        
        # Organize tasks by status
        todo_tasks = [task for task in filtered_tasks if task['status'] == "To Do"]
        in_progress_tasks = [task for task in filtered_tasks if task['status'] == "In Progress"]
        done_tasks = [task for task in filtered_tasks if task['status'] == "Done"]
        
        # Display Kanban board
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("### To Do")
            for task in todo_tasks:
                with st.container(border=True):
                    st.markdown(f"**{task['title']}**")
                    st.markdown(f"**Type:** {task['type']} | **Priority:** {task['priority']}")
                    st.markdown(f"**Due:** {task['due_date']}")
                    
                    if task['assignee'] != "Unassigned":
                        st.markdown(f"**Assigned to:** {task['assignee']}")
                    else:
                        st.markdown("**Assigned to:** Unassigned")
                    
                    if task['description']:
                        with st.expander("Description"):
                            st.write(task['description'])
                    
                    # Action buttons
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("Start", key=f"start_{task['id']}"):
                            for t in st.session_state.tasks:
                                if t['id'] == task['id']:
                                    t['status'] = "In Progress"
                                    t['updated_at'] = datetime.now().strftime("%Y-%m-%d %H:%M")
                            st.rerun()
                    with col2:
                        if st.button("Edit", key=f"edit_{task['id']}"):
                            st.session_state.active_task = task
                            st.session_state.edit_task = True
                            st.rerun()
        
        with col2:
            st.markdown("### In Progress")
            for task in in_progress_tasks:
                with st.container(border=True):
                    st.markdown(f"**{task['title']}**")
                    st.markdown(f"**Type:** {task['type']} | **Priority:** {task['priority']}")
                    st.markdown(f"**Due:** {task['due_date']}")
                    
                    if task['assignee'] != "Unassigned":
                        st.markdown(f"**Assigned to:** {task['assignee']}")
                    else:
                        st.markdown("**Assigned to:** Unassigned")
                    
                    if task['description']:
                        with st.expander("Description"):
                            st.write(task['description'])
                    
                    # Action buttons
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("Complete", key=f"complete_{task['id']}"):
                            for t in st.session_state.tasks:
                                if t['id'] == task['id']:
                                    t['status'] = "Done"
                                    t['updated_at'] = datetime.now().strftime("%Y-%m-%d %H:%M")
                            st.rerun()
                    with col2:
                        if st.button("Return", key=f"return_{task['id']}"):
                            for t in st.session_state.tasks:
                                if t['id'] == task['id']:
                                    t['status'] = "To Do"
                                    t['updated_at'] = datetime.now().strftime("%Y-%m-%d %H:%M")
                            st.rerun()
        
        with col3:
            st.markdown("### Done")
            for task in done_tasks:
                with st.container(border=True):
                    st.markdown(f"**{task['title']}**")
                    st.markdown(f"**Type:** {task['type']} | **Priority:** {task['priority']}")
                    st.markdown(f"**Completed:** {task['updated_at']}")
                    
                    if task['assignee'] != "Unassigned":
                        st.markdown(f"**Completed by:** {task['assignee']}")
                    
                    if task['description']:
                        with st.expander("Description"):
                            st.write(task['description'])
                    
                    # Action button
                    if st.button("Reopen", key=f"reopen_{task['id']}"):
                        for t in st.session_state.tasks:
                            if t['id'] == task['id']:
                                t['status'] = "To Do"
                                t['updated_at'] = datetime.now().strftime("%Y-%m-%d %H:%M")
                        st.rerun()

# Team Members Tab
with tab2:
    st.subheader("Team Members")
    
    # Add team member form
    with st.expander("Add Team Member", expanded=len(st.session_state.team_members) == 0):
        with st.form("add_team_member_form"):
            member_name = st.text_input("Name", placeholder="Enter team member name...")
            member_email = st.text_input("Email", placeholder="Enter email address...")
            member_role = st.selectbox(
                "Role",
                options=["Admin", "Manager", "Contributor", "Viewer"]
            )
            
            add_member = st.form_submit_button("Add Team Member")
            
            if add_member and member_name and member_email:
                # Check if email already exists
                if any(member['email'] == member_email for member in st.session_state.team_members):
                    st.error("A team member with this email already exists.")
                else:
                    # Add new team member
                    new_member = {
                        'id': len(st.session_state.team_members) + 1,
                        'name': member_name,
                        'email': member_email,
                        'role': member_role,
                        'joined_at': datetime.now().strftime("%Y-%m-%d %H:%M")
                    }
                    
                    st.session_state.team_members.append(new_member)
                    st.success(f"Team member '{member_name}' added successfully!")
                    st.rerun()
    
    # Display team members
    if not st.session_state.team_members:
        st.info("No team members have been added yet. Use the form above to add your first team member.")
    else:
        # Convert to DataFrame for display
        members_data = {
            'Name': [],
            'Email': [],
            'Role': [],
            'Joined': [],
            'Actions': []
        }
        
        for member in st.session_state.team_members:
            members_data['Name'].append(member['name'])
            members_data['Email'].append(member['email'])
            members_data['Role'].append(member['role'])
            members_data['Joined'].append(member['joined_at'])
            members_data['Actions'].append("...")
        
        df = pd.DataFrame(members_data)
        st.dataframe(df, hide_index=True, use_container_width=True)
        
        # Email invitation section
        st.subheader("Invite Team Members")
        st.markdown("""
        To invite new team members to collaborate on your ESG initiatives:
        
        1. Add them using the form above
        2. Share your organization's Carbon Aegis access details
        3. Assign them specific tasks from the Tasks tab
        """)
        
        # Future feature placeholder
        st.info("Email invitations will be available in a future update.")

# Activity Log Tab
with tab3:
    st.subheader("Activity Log")
    
    # Generate activity log from tasks and team members
    activities = []
    
    # Add task activities
    for task in st.session_state.tasks:
        activities.append({
            'date': task['created_at'],
            'type': 'Task Created',
            'description': f"Task '{task['title']}' was created",
            'user': 'System'
        })
        
        if task['updated_at'] != task['created_at']:
            activities.append({
                'date': task['updated_at'],
                'type': 'Task Updated',
                'description': f"Task '{task['title']}' status changed to {task['status']}",
                'user': task['assignee'] if task['assignee'] != "Unassigned" else 'System'
            })
    
    # Add team member activities
    for member in st.session_state.team_members:
        activities.append({
            'date': member['joined_at'],
            'type': 'Member Added',
            'description': f"{member['name']} ({member['role']}) joined the team",
            'user': 'System'
        })
    
    # Sort activities by date (newest first)
    activities.sort(key=lambda x: datetime.strptime(x['date'], "%Y-%m-%d %H:%M"), reverse=True)
    
    if not activities:
        st.info("No activities recorded yet. Create tasks or add team members to see activity here.")
    else:
        for activity in activities:
            with st.container(border=True):
                col1, col2 = st.columns([1, 4])
                with col1:
                    st.markdown(f"**{activity['date']}**")
                    st.markdown(f"*{activity['type']}*")
                with col2:
                    st.markdown(activity['description'])
                    st.markdown(f"By: {activity['user']}")

# Add navigation
st.markdown("---")
col1, col2, col3 = st.columns([1, 1, 1])
with col1:
    if st.button("📊 ESG Dashboard", use_container_width=True):
        st.switch_page("pages/6_ESG_Dashboard.py")
with col2:
    if st.button("📝 ESG Assessment", use_container_width=True):
        st.switch_page("pages/7_ESG_Readiness.py")
with col3:
    if st.button("🏠 Home", use_container_width=True):
        st.switch_page("app.py")