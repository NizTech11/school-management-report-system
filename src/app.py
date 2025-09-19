import os
import sys
import streamlit as st

# Ensure relative imports from src/ work when launched by Streamlit
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

st.set_page_config(
    page_title="Student Report Management System",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Import role-based authentication system
try:
    from components.auth import (
        render_login_form, 
        render_user_info, 
        initialize_auth_system
    )
    from utils.rbac import (
        has_permission, 
        is_logged_in, 
        get_current_user,
        initialize_rbac
    )
    auth_ok = True
except Exception as e:
    auth_ok = False
    st.error(f"Authentication system failed to load: {e}")

# Initialize the authentication system
if auth_ok:
    initialize_rbac()

def render_sidebar():
    """Render sidebar with role-based navigation"""
    st.sidebar.title("📚 Student Report System")
    
    if is_logged_in():
        user = get_current_user()
        if user:  # Add null check
            st.sidebar.success(f"Welcome, {user['full_name']}!")
            st.sidebar.write(f"**Role:** {user['role']}")
            
            # Role-based navigation
            st.sidebar.markdown("---")
            st.sidebar.markdown("### 📋 Navigation")
            
            # Students - Available to all roles
            if has_permission(user['role'], 'students.view'):
                st.sidebar.page_link("pages/1_Students.py", label="🎓 Students")
            
            # Classes - Available to Head and Admin
            if has_permission(user['role'], 'classes.view'):
                st.sidebar.page_link("pages/2_Classes.py", label="🏫 Classes")
            
            # Subjects - Available to all roles
            if has_permission(user['role'], 'subjects.view'):
                st.sidebar.page_link("pages/3_Subjects.py", label="📚 Subjects")
            
            # Marks - Available to all roles
            if has_permission(user['role'], 'marks.view'):
                st.sidebar.page_link("pages/4_Marks.py", label="📝 Marks")
            
            # Dashboard - Available to all roles
            if has_permission(user['role'], 'analytics.view'):
                st.sidebar.page_link("pages/5_Dashboard.py", label="📊 Dashboard")
            
            # Enhanced Analytics - Available to Head and Admin
            if has_permission(user['role'], 'analytics.advanced'):
                st.sidebar.page_link("pages/10_Enhanced_Analytics.py", label="🔬 Enhanced Analytics")
            
            # Reports - Available to all roles
            if has_permission(user['role'], 'reports.view'):
                st.sidebar.page_link("pages/6_Reports.py", label="📋 Reports")
            
            # Template Editor - Available to Head and Admin
            if has_permission(user['role'], 'reports.templates.edit'):
                st.sidebar.page_link("pages/10_Clean_Template_Editor.py", label="📝 Report Template Editor")
            
            # Advanced Reports - Available to users with advanced reporting permissions
            if has_permission(user['role'], 'reports.templates.view'):
                st.sidebar.page_link("pages/12_Advanced_Reports.py", label="📊 Advanced Reports")
            
            # Teachers - Available to Head and Admin
            if has_permission(user['role'], 'teachers.view'):
                st.sidebar.page_link("pages/7_Teachers.py", label="👨‍🏫 Teachers")
            
            # Calendar - Available to all roles
            if has_permission(user['role'], 'calendar.view'):
                st.sidebar.page_link("pages/9_Calendar.py", label="📅 Calendar")
            
            # Curriculum & Assessment - Available to Head and Admin (and Teachers with view permissions)
            if has_permission(user['role'], 'curriculum.manage'):
                st.sidebar.page_link("pages/11_Curriculum_Assessment.py", label="📚 Curriculum & Assessment")
            
            # Admin features
            if user['role'] == 'Admin':
                st.sidebar.markdown("---")
                st.sidebar.markdown("### ⚙️ Administration")
                if st.sidebar.button("👥 User Management"):
                    st.switch_page("pages/8_UserManagement.py")
            
            # User info and logout
            render_user_info()
    else:
        st.sidebar.write("Please log in to access the system.")

def render_home():
    """Render home page with role-based content"""
    if not is_logged_in():
        st.title("🔐 Student Report Management System")
        st.write("Please log in to access the system.")
        render_login_form()
        return
    
    user = get_current_user()
    if not user:  # Add null check
        st.error("Error loading user data. Please log in again.")
        return
        
    st.title(f"🎓 Welcome, {user['full_name']}!")
    
    # Role-specific welcome message
    role_messages = {
        "Teacher": "Access your classes, enter marks, and generate reports for your students.",
        "Head": "Manage school operations, oversee teachers, and access comprehensive analytics.",
        "Admin": "Full system administration including user management and system settings."
    }
    
    st.success(role_messages.get(user['role'], "Welcome to the Student Report Management System!"))

    # Role-based quick actions
    st.markdown("### 🚀 Quick Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if has_permission(user['role'], 'analytics.view'):
            if st.button("📊 Dashboard", use_container_width=True, type="primary"):
                st.switch_page("pages/5_Dashboard.py")
    
    with col2:
        if has_permission(user['role'], 'students.view'):
            if st.button("🎓 Students", use_container_width=True):
                st.switch_page("pages/1_Students.py")
    
    with col3:
        if has_permission(user['role'], 'marks.create'):
            if st.button("📝 Enter Marks", use_container_width=True):
                st.switch_page("pages/4_Marks.py")
    
    # Second row for additional actions based on role
    if user['role'] in ['Head', 'Admin']:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if has_permission(user['role'], 'teachers.view'):
                if st.button("�‍🏫 Teachers", use_container_width=True):
                    st.switch_page("pages/7_Teachers.py")
        
        with col2:
            if has_permission(user['role'], 'classes.view'):
                if st.button("🏫 Classes", use_container_width=True):
                    st.switch_page("pages/2_Classes.py")
        
        with col3:
            if user['role'] == 'Admin':
                if st.button("👥 User Management", use_container_width=True):
                    st.switch_page("pages/8_UserManagement.py")

    st.markdown("---")
    st.markdown("### 📋 Getting Started")
    
    # Role-specific instructions
    if user['role'] == 'Teacher':
        st.markdown("""
        **As a Teacher, you can:**
        1. View your assigned students and classes
        2. Enter and edit marks for your subjects
        3. Generate student reports
        4. View basic analytics for your classes
        """)
    elif user['role'] == 'Head':
        st.markdown("""
        **As a Head Teacher, you can:**
        1. Manage all students, classes, and subjects
        2. Oversee teacher assignments and performance
        3. Access comprehensive analytics and reports
        4. Manage the academic calendar and schedules
        """)
    elif user['role'] == 'Admin':
        st.markdown("""
        **As an Administrator, you can:**
        1. Full system access including user management
        2. System settings and configuration
        3. Data backup and recovery operations
        4. Advanced analytics and reporting features
        """)

# Render sidebar
render_sidebar()

# Main content
if not auth_ok:
    st.error("Authentication system not available.")
    st.info("Please ensure all required files are present and dependencies are installed.")
    st.stop()

# Check if user is logged in and render appropriate content
if is_logged_in():
    render_home()
else:
    st.title("🔐 Login Required")
    render_login_form()
