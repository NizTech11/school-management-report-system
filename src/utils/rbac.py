"""
Role-Based Access Control (RBAC) System
Handles user roles, permissions, and access control
"""

import streamlit as st
import bcrypt
import json
from datetime import datetime
from typing import Dict, List, Optional, Set, Tuple
from services.db import get_session, User, Role, Teacher, TeacherClass, Class
from sqlmodel import select

# Define permissions for different system features
PERMISSIONS = {
    # Student Management
    "students.view": "View students",
    "students.create": "Add new students", 
    "students.edit": "Edit student information",
    "students.delete": "Delete students",
    
    # Teacher Management
    "teachers.view": "View teachers",
    "teachers.create": "Add new teachers",
    "teachers.edit": "Edit teacher information", 
    "teachers.delete": "Delete teachers",
    
    # Class Management
    "classes.view": "View classes",
    "classes.create": "Add new classes",
    "classes.edit": "Edit class information",
    "classes.delete": "Delete classes",
    
    # Subject Management
    "subjects.view": "View subjects",
    "subjects.create": "Add new subjects",
    "subjects.edit": "Edit subjects",
    "subjects.delete": "Delete subjects",
    
    # Marks Management
    "marks.view": "View marks",
    "marks.create": "Enter new marks",
    "marks.edit": "Edit existing marks", 
    "marks.delete": "Delete marks",
    "marks.delete_all": "Delete all marks from all students",
    
    # Reports and Analytics
    "reports.view": "View reports",
    "reports.generate": "Generate reports",
    "reports.export": "Export reports",
    "analytics.view": "View analytics dashboard",
    "analytics.advanced": "Access advanced analytics",
    
    # Calendar and Scheduling
    "calendar.view": "View academic calendar",
    "calendar.create": "Create calendar events",
    "calendar.edit": "Edit calendar events",
    "calendar.delete": "Delete calendar events",
    
    # System Administration
    "system.settings": "Modify system settings",
    "system.backup": "Perform system backups",
    "system.logs": "View system logs",
    "system.users": "Manage user accounts",
    "system.roles": "Manage user roles",
    
    # Curriculum and Assessment
    "curriculum.view": "View curriculum",
    "curriculum.create": "Create curriculum content",
    "curriculum.edit": "Edit curriculum",
    "curriculum.manage": "Full curriculum management",
    "assignments.view": "View assignments",
    "assignments.create": "Create assignments",
    "assignments.grade": "Grade assignments",
    "rubrics.view": "View grading rubrics",
    "rubrics.create": "Create grading rubrics",
    "assessment.continuous": "Record continuous assessments",
    
    # Advanced Reporting System
    "reports.templates.view": "View report templates",
    "reports.templates.create": "Create report templates",
    "reports.templates.edit": "Edit report templates",
    "reports.templates.delete": "Delete report templates",
    "reports.custom.create": "Create custom reports",
    "reports.custom.execute": "Execute and generate reports",
    "reports.custom.schedule": "Schedule automated reports",
    "reports.custom.share": "Share reports with others",
    "reports.builder.access": "Access report builder interface",
    "reports.analytics.advanced": "Access advanced report analytics",
}

# Define role permissions
ROLE_PERMISSIONS = {
    "Teacher": [
        "students.view", # Teachers can view students in their assigned classes only
        "students.create", # Teachers can add students to their assigned classes
        "students.edit", # Teachers can edit students in their assigned classes
        "students.delete", # Teachers can delete students from their assigned classes
        "classes.view",  # Teachers can view class information but not create/edit
        "subjects.view",
        "marks.view", "marks.create", "marks.edit", # Teachers can manage marks for their students
        "reports.view", "reports.generate",
        "analytics.view",
        "calendar.view",
        "curriculum.view", "assignments.view", "assignments.create", "assignments.grade",
        "rubrics.view", "assessment.continuous",
        # Basic reporting permissions for teachers
        "reports.templates.view", "reports.custom.create", "reports.custom.execute",
        "reports.builder.access"
    ],
    "Head": [
        # All Teacher permissions plus:
        "students.view", "students.create", "students.edit", "students.delete",
        "teachers.view", "teachers.create", "teachers.edit",
        "classes.view", "classes.create", "classes.edit", "classes.delete",
        "subjects.view", "subjects.create", "subjects.edit", "subjects.delete",
        "marks.view", "marks.create", "marks.edit", "marks.delete", "marks.delete_all",
        "reports.view", "reports.generate", "reports.export",
        "analytics.view", "analytics.advanced",
        "calendar.view", "calendar.create", "calendar.edit", "calendar.delete",
        "curriculum.view", "curriculum.create", "curriculum.edit", "curriculum.manage",
        "assignments.view", "assignments.create", "assignments.grade",
        "rubrics.view", "rubrics.create", "assessment.continuous",
        # Advanced reporting permissions for heads
        "reports.templates.view", "reports.templates.create", "reports.templates.edit",
        "reports.custom.create", "reports.custom.execute", "reports.custom.schedule",
        "reports.custom.share", "reports.builder.access", "reports.analytics.advanced"
    ],
    "Admin": [
        # All permissions
        *PERMISSIONS.keys()
    ]
}

def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    """Verify a password against its hash"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def create_default_roles():
    """Create default roles if they don't exist"""
    with get_session() as session:
        for role_name, permissions in ROLE_PERMISSIONS.items():
            existing_role = session.exec(select(Role).where(Role.name == role_name)).first()
            if not existing_role:
                role = Role(
                    name=role_name,
                    description=f"Default {role_name} role",
                    permissions=json.dumps(permissions)
                )
                session.add(role)
        session.commit()

def create_default_admin():
    """Create default admin user if no users exist"""
    with get_session() as session:
        users_count = len(session.exec(select(User)).all())
        if users_count == 0:
            admin_user = User(
                username="admin",
                email="admin@school.com",
                hashed_password=hash_password("admin123"),
                full_name="System Administrator",
                role="Admin",
                is_active=True
            )
            session.add(admin_user)
            session.commit()
            return True
    return False

def authenticate_user(username: str, password: str) -> Optional[Dict]:
    """Authenticate a user with username and password"""
    with get_session() as session:
        user = session.exec(
            select(User).where(
                User.username == username,
                User.is_active == True
            )
        ).first()
        
        if user and verify_password(password, user.hashed_password):
            # Update last login
            user.last_login = datetime.utcnow()
            session.add(user)
            session.commit()
            
            # Return user data as dict to avoid DetachedInstanceError
            return {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'full_name': user.full_name,
                'role': user.role,
                'is_active': user.is_active,
                'last_login': user.last_login
            }
    return None

def get_user_permissions(role: str) -> Set[str]:
    """Get all permissions for a given role"""
    return set(ROLE_PERMISSIONS.get(role, []))

def has_permission(user_role: str, permission: str) -> bool:
    """Check if a user role has a specific permission"""
    user_permissions = get_user_permissions(user_role)
    return permission in user_permissions

def require_permission(permission: str):
    """Decorator to require a specific permission for a function"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            if 'user' not in st.session_state:
                st.error("Please login to access this feature")
                st.stop()
            
            user_role = st.session_state.user.get('role', 'Teacher')
            if not has_permission(user_role, permission):
                st.error("You don't have permission to access this feature")
                st.stop()
            
            return func(*args, **kwargs)
        return wrapper
    return decorator

def get_current_user() -> Optional[Dict]:
    """Get the current logged-in user from session state"""
    return st.session_state.get('user')

def is_logged_in() -> bool:
    """Check if a user is currently logged in"""
    return 'user' in st.session_state and st.session_state.user is not None

def logout():
    """Log out the current user"""
    if 'user' in st.session_state:
        del st.session_state.user
    st.rerun()

def login_user(user_data: Dict):
    """Log in a user and store in session state"""
    st.session_state.user = {
        'id': user_data['id'],
        'username': user_data['username'],
        'email': user_data['email'],
        'full_name': user_data['full_name'],
        'role': user_data['role'],
        'permissions': list(get_user_permissions(user_data['role']))
    }

def get_permission_description(permission: str) -> str:
    """Get human-readable description of a permission"""
    return PERMISSIONS.get(permission, permission)

def get_role_permissions_display(role: str) -> List[str]:
    """Get formatted list of permissions for display"""
    permissions = ROLE_PERMISSIONS.get(role, [])
    return [f"• {get_permission_description(p)}" for p in permissions]

# Initialize roles and default admin on import
def initialize_rbac():
    """Initialize RBAC system with default roles and admin user"""
    try:
        create_default_roles()
        admin_created = create_default_admin()
        return admin_created
    except Exception as e:
        st.error(f"Error initializing RBAC system: {e}")
        return False

def create_teacher_user(teacher_data: dict, class_ids: Optional[List[int]] = None) -> Tuple[bool, str]:
    """Create a new teacher user account and link to Teacher record"""
    with get_session() as session:
        # Check if username or email already exists
        existing_user = session.exec(
            select(User).where(
                (User.username == teacher_data['username']) | 
                (User.email == teacher_data['email'])
            )
        ).first()
        
        if existing_user:
            return False, f"User with username '{teacher_data['username']}' or email '{teacher_data['email']}' already exists"
        
        try:
            # Create Teacher record first
            teacher = Teacher(
                first_name=teacher_data['first_name'],
                last_name=teacher_data['last_name'],
                email=teacher_data['email'],
                phone=teacher_data.get('phone'),
                subject_specialization=teacher_data.get('subject_specialization')
            )
            session.add(teacher)
            session.commit()
            session.refresh(teacher)
            
            # Create User record linked to Teacher
            user = User(
                username=teacher_data['username'],
                email=teacher_data['email'],
                hashed_password=hash_password(teacher_data['password']),
                full_name=f"{teacher_data['first_name']} {teacher_data['last_name']}",
                role=teacher_data.get('role', 'Teacher'),
                teacher_id=teacher.id,
                is_active=True
            )
            session.add(user)
            session.commit()
            session.refresh(user)
            
            # Assign to classes if provided
            if class_ids and user.id is not None:
                for class_id in class_ids:
                    teacher_class = TeacherClass(
                        user_id=user.id,
                        class_id=class_id,
                        is_active=True
                    )
                    session.add(teacher_class)
                session.commit()
            
            return True, f"Teacher user {teacher_data['username']} created successfully"
            
        except Exception as e:
            session.rollback()
            return False, f"Error creating teacher user: {str(e)}"

def get_teacher_classes(user_id: int) -> List[int]:
    """Get all class IDs assigned to a teacher user"""
    with get_session() as session:
        teacher_classes = session.exec(
            select(TeacherClass.class_id).where(
                TeacherClass.user_id == user_id,
                TeacherClass.is_active == True
            )
        ).all()
        return list(teacher_classes)

def assign_teacher_to_classes(user_id: int, class_ids: List[int]) -> bool:
    """Assign a teacher to multiple classes"""
    with get_session() as session:
        try:
            # Remove existing assignments
            existing_assignments = session.exec(
                select(TeacherClass).where(TeacherClass.user_id == user_id)
            ).all()
            
            for assignment in existing_assignments:
                session.delete(assignment)
            
            # Add new assignments
            for class_id in class_ids:
                teacher_class = TeacherClass(
                    user_id=user_id,
                    class_id=class_id,
                    is_active=True
                )
                session.add(teacher_class)
            
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            return False

def is_teacher_assigned_to_class(user_id: int, class_id: int) -> bool:
    """Check if a teacher is assigned to a specific class"""
    with get_session() as session:
        assignment = session.exec(
            select(TeacherClass).where(
                TeacherClass.user_id == user_id,
                TeacherClass.class_id == class_id,
                TeacherClass.is_active == True
            )
        ).first()
        return assignment is not None

def get_user_accessible_students(user_id: int, role: str) -> List[int]:
    """Get list of student IDs accessible to a user based on their role and class assignments
    Returns:
    - [] (empty list): Admin/Head - access to all students
    - [-1]: Teacher with no class assignments - no access
    - [-2]: Teacher with class assignments but no students in those classes
    - [student_ids]: Teacher with specific students they can access
    """
    if role in {'Admin', 'Head'}:
        # Admin and Head can access all students
        return []  # Empty list means access to all
    
    with get_session() as session:
        # Get classes assigned to this teacher
        teacher_classes = session.exec(
            select(TeacherClass.class_id).where(
                TeacherClass.user_id == user_id,
                TeacherClass.is_active == True
            )
        ).all()
        
        if not teacher_classes:
            return [-1]  # No access to any students - not assigned to classes
        
        # Get students in assigned classes
        from services.db import Student
        students = session.exec(
            select(Student.id).where(Student.class_id.in_(teacher_classes))
        ).all()
        
        # Filter out None values and convert to list
        student_ids = [s for s in students if s is not None]
        
        # If teacher has class assignments but no students in those classes
        if not student_ids:
            return [-2]  # Teacher has classes but no students in assigned classes
        
        return student_ids

def reset_user_password(username: str, new_password: str) -> Tuple[bool, str]:
    """Reset a user's password"""
    with get_session() as session:
        try:
            # Find user by username
            user = session.exec(select(User).where(User.username == username)).first()
            if not user:
                return False, "User not found"
            
            # Update password
            user.hashed_password = hash_password(new_password)
            session.add(user)
            session.commit()
            
            return True, f"Password reset successfully for user {username}"
            
        except Exception as e:
            session.rollback()
            return False, f"Error resetting password: {str(e)}"

def find_user_by_email(email: str) -> Optional[Dict]:
    """Find a user by their email address"""
    with get_session() as session:
        user = session.exec(select(User).where(User.email == email)).first()
        if user:
            return {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'full_name': user.full_name,
                'role': user.role
            }
        return None

def deactivate_user(user_id: int) -> Tuple[bool, str]:
    """Deactivate a user account"""
    with get_session() as session:
        try:
            user = session.get(User, user_id)
            if not user:
                return False, "User not found"
            
            user.is_active = False
            session.add(user)
            session.commit()
            
            return True, f"User {user.username} deactivated successfully"
            
        except Exception as e:
            session.rollback()
            return False, f"Error deactivating user: {str(e)}"

def reactivate_user(user_id: int) -> Tuple[bool, str]:
    """Reactivate a user account"""
    with get_session() as session:
        try:
            user = session.get(User, user_id)
            if not user:
                return False, "User not found"
            
            user.is_active = True
            session.add(user)
            session.commit()
            
            return True, f"User {user.username} reactivated successfully"
            
        except Exception as e:
            session.rollback()
            return False, f"Error reactivating user: {str(e)}"