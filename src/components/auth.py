"""
Role-Based Authentication Login Component
Handles user login with role-based access control
"""

import streamlit as st
from utils.rbac import authenticate_user, login_user, logout, is_logged_in, get_current_user, initialize_rbac
from services.db import get_session, User
from sqlmodel import select

def render_login_form():
    """Render the login form"""
    st.title("🔐 Login")
    st.markdown("Please enter your credentials to access the Student Report Management System.")
    
    with st.form("login_form"):
        st.subheader("User Login")
        username = st.text_input("Username", placeholder="Enter your username")
        password = st.text_input("Password", type="password", placeholder="Enter your password")
        login_button = st.form_submit_button("Login", type="primary", use_container_width=True)
        
        if login_button:
            if username and password:
                user_data = authenticate_user(username, password)
                if user_data:
                    login_user(user_data)
                    st.success(f"Welcome, {user_data['full_name']}!")
                    st.rerun()
                else:
                    st.error("Invalid username or password. Please try again.")
            else:
                st.error("Please enter both username and password.")
    
    # Show default credentials for first-time users
    st.markdown("---")
    st.info("""
    **Default Credentials:**
    - Username: `admin`
    - Password: `admin123`
    - Role: Administrator
    
    Please change these credentials after your first login.
    """)

def render_user_info():
    """Render current user information in the sidebar"""
    user = get_current_user()
    if user:
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 👤 User Information")
        st.sidebar.write(f"**Name:** {user['full_name']}")
        st.sidebar.write(f"**Role:** {user['role']}")
        st.sidebar.write(f"**Username:** {user['username']}")
        
        # Role-specific information
        role_info = {
            "Admin": "🔧 Full system access",
            "Head": "👨‍💼 Management access", 
            "Teacher": "👨‍🏫 Teaching access"
        }
        st.sidebar.write(f"**Access Level:** {role_info.get(user['role'], 'Standard')}")
        
        # Logout button
        if st.sidebar.button("🚪 Logout", type="secondary", use_container_width=True):
            logout()

def render_permission_denied():
    """Render permission denied message"""
    st.error("🚫 Access Denied")
    st.write("You don't have permission to access this feature.")
    
    user = get_current_user()
    if user:
        st.info(f"Your current role: **{user['role']}**")
        st.write("Please contact your administrator if you believe you should have access to this feature.")

def check_page_permission(permission: str) -> bool:
    """Check if current user has permission to view a page"""
    if not is_logged_in():
        return False
    
    user = get_current_user()
    return permission in user.get('permissions', [])

def render_unauthorized_page():
    """Render page for unauthorized access"""
    st.title("🔒 Authentication Required")
    st.write("Please log in to access the Student Report Management System.")
    
    if not is_logged_in():
        render_login_form()
    else:
        user = get_current_user()
        st.success(f"Welcome, {user['full_name']}!")

def initialize_auth_system():
    """Initialize the authentication system"""
    # Initialize RBAC system
    admin_created = initialize_rbac()
    
    if admin_created:
        st.success("Default administrator account created successfully!")
        st.info("Please use the default credentials to log in for the first time.")
    
    return True

def create_user_management_interface():
    """Create user management interface for admins"""
    user = get_current_user()
    if not user or user['role'] != 'Admin':
        render_permission_denied()
        return
    
    st.title("👥 User Management")
    st.markdown("Manage system users and their roles.")
    
    tab1, tab2 = st.tabs(["View Users", "Add User"])
    
    with tab1:
        render_users_list()
    
    with tab2:
        render_add_user_form()

def render_users_list():
    """Render list of all users"""
    st.subheader("System Users")
    
    with get_session() as session:
        users = session.exec(select(User).order_by(User.full_name)).all()
    
    if not users:
        st.info("No users found in the system.")
        return
    
    for user in users:
        with st.expander(f"👤 {user.full_name} ({user.role})", expanded=False):
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                st.write(f"**Username:** {user.username}")
                st.write(f"**Email:** {user.email}")
                st.write(f"**Role:** {user.role}")
                st.write(f"**Status:** {'Active' if user.is_active else 'Inactive'}")
                if user.last_login:
                    st.write(f"**Last Login:** {user.last_login.strftime('%Y-%m-%d %H:%M')}")
                else:
                    st.write("**Last Login:** Never")
            
            with col2:
                # Toggle active status
                new_status = not user.is_active
                status_text = "Activate" if new_status else "Deactivate"
                
                if st.button(f"{status_text}", key=f"toggle_{user.id}"):
                    toggle_user_status(user.id, new_status)
                    st.rerun()
            
            with col3:
                if st.button("Edit Role", key=f"edit_{user.id}"):
                    edit_user_role(user)

def render_add_user_form():
    """Render form to add new users"""
    st.subheader("Add New User")
    
    with st.form("add_user_form"):
        full_name = st.text_input("Full Name", placeholder="Enter full name")
        username = st.text_input("Username", placeholder="Enter username")
        email = st.text_input("Email", placeholder="Enter email address")
        password = st.text_input("Password", type="password", placeholder="Enter password")
        role = st.selectbox("Role", ["Teacher", "Head", "Admin"])
        
        submitted = st.form_submit_button("Create User", type="primary")
        
        if submitted:
            if full_name and username and email and password:
                create_new_user(full_name, username, email, password, role)
            else:
                st.error("Please fill in all fields.")

def create_new_user(full_name: str, username: str, email: str, password: str, role: str):
    """Create a new user in the system"""
    from utils.rbac import hash_password
    
    with get_session() as session:
        # Check if username or email already exists
        existing_user = session.exec(
            select(User).where(
                (User.username == username) | (User.email == email)
            )
        ).first()
        
        if existing_user:
            st.error("Username or email already exists. Please choose different values.")
            return
        
        # Create new user
        new_user = User(
            username=username,
            email=email,
            hashed_password=hash_password(password),
            full_name=full_name,
            role=role,
            is_active=True
        )
        
        session.add(new_user)
        session.commit()
        st.success(f"User '{full_name}' created successfully with role '{role}'!")
        st.rerun()

def toggle_user_status(user_id: int, new_status: bool):
    """Toggle user active/inactive status"""
    with get_session() as session:
        user = session.get(User, user_id)
        if user:
            user.is_active = new_status
            session.add(user)
            session.commit()
            status_text = "activated" if new_status else "deactivated"
            st.success(f"User {status_text} successfully!")

def edit_user_role(user: User):
    """Edit user role interface"""
    st.subheader(f"Edit Role for {user.full_name}")
    
    new_role = st.selectbox(
        "Select New Role",
        ["Teacher", "Head", "Admin"],
        index=["Teacher", "Head", "Admin"].index(user.role)
    )
    
    if st.button("Update Role"):
        update_user_role(user.id, new_role)
        st.success(f"Role updated to {new_role}!")
        st.rerun()

def update_user_role(user_id: int, new_role: str):
    """Update user role in database"""
    with get_session() as session:
        user = session.get(User, user_id)
        if user:
            user.role = new_role
            session.add(user)
            session.commit()