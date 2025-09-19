import streamlit as st
from services.db import get_session, Teacher, Class, User, TeacherClass
from utils.rbac import create_teacher_user, get_teacher_classes, has_permission, require_permission, assign_teacher_to_classes, reset_user_password, deactivate_user, reactivate_user
from sqlmodel import select


@require_permission("teachers.create")
def teacher_form():
    st.header("Add New Teacher with User Account")
    
    # Get available classes for assignment
    with get_session() as session:
        classes = session.exec(select(Class).order_by(Class.category, Class.name)).all()
    
    with st.form("teacher_form"):
        # Teacher Information
        st.subheader("👤 Teacher Information")
        col1, col2 = st.columns(2)
        
        with col1:
            first_name = st.text_input("First Name*", key="teacher_first_name")
            email = st.text_input("Email*", key="teacher_email")
            phone = st.text_input("Phone Number", key="teacher_phone")
        
        with col2:
            last_name = st.text_input("Last Name*", key="teacher_last_name")
            specialization = st.text_input("Subject Specialization", 
                                         placeholder="e.g., Mathematics, English, Science",
                                         key="teacher_specialization")
        
        # User Account Information
        st.subheader("🔐 User Account")
        col3, col4 = st.columns(2)
        
        with col3:
            username = st.text_input("Username*", key="teacher_username",
                                   help="Username for login (must be unique)")
            password = st.text_input("Password*", type="password", key="teacher_password",
                                   help="Minimum 6 characters")
        
        with col4:
            role = st.selectbox("Role", ["Teacher", "Head"], key="teacher_role",
                              help="Teacher: Basic access, Head: Advanced access")
            confirm_password = st.text_input("Confirm Password*", type="password", 
                                           key="teacher_confirm_password")
        
        # Class Assignment Section
        st.subheader("🏫 Class Assignment")
        
        if not classes:
            st.info("No classes available. Please create classes first before assigning teachers.")
            selected_classes = []
        else:
            class_options = [f"{cls.name} ({cls.category})" for cls in classes]
            selected_class_names = st.multiselect(
                "Assign to Classes",
                options=class_options,
                help="Select one or more classes to assign this teacher to. Teachers can only see students from their assigned classes."
            )
            
            # Convert selected names back to class IDs
            selected_classes = []
            for selected_name in selected_class_names:
                if selected_name:
                    class_name = selected_name.split(" (")[0]
                    selected_class = next((cls for cls in classes if cls.name == class_name), None)
                    if selected_class and selected_class.id is not None:
                        selected_classes.append(selected_class.id)
        
        submitted = st.form_submit_button("Create Teacher Account", type="primary")
    
    if submitted:
        # Validation
        if not all([first_name, last_name, email, username, password]):
            st.error("Please fill in all required fields (marked with *)")
            return
        
        if len(password) < 6:
            st.error("Password must be at least 6 characters long")
            return
            
        if password != confirm_password:
            st.error("Passwords do not match")
            return
        
        if not selected_classes:
            st.warning("⚠️ No classes assigned. Teacher will have limited access until classes are assigned.")
        
        # Create teacher data
        teacher_data = {
            'first_name': first_name,
            'last_name': last_name,
            'email': email,
            'phone': phone or None,
            'subject_specialization': specialization or None,
            'username': username,
            'password': password,
            'role': role
        }
        
        # Create teacher user account
        success, message = create_teacher_user(teacher_data, selected_classes)
        
        if success:
            st.success(f"✅ {message}")
            if selected_classes:
                class_names = [cls.name for cls in classes if cls.id in selected_classes]
                st.info(f"📚 Assigned to classes: {', '.join(class_names)}")
            st.rerun()
        else:
            st.error(f"❌ {message}")


@require_permission("teachers.view")
def display_teachers():
    """Enhanced teacher display with user accounts and class assignments"""
    st.header("All Teachers")
    
    with get_session() as session:
        # Get all teachers with their user accounts
        teachers = session.exec(select(Teacher).order_by(Teacher.last_name, Teacher.first_name)).all()
        
        if not teachers:
            st.info("No teachers found. Add teachers using the form above.")
            return
        
        # Display each teacher
        for teacher in teachers:
            if teacher.id is None:
                continue
                
            with st.expander(f"👨‍🏫 {teacher.first_name} {teacher.last_name}"):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.write(f"**Email:** {teacher.email}")
                    if teacher.phone:
                        st.write(f"**Phone:** {teacher.phone}")
                    if teacher.subject_specialization:
                        st.write(f"**Specialization:** {teacher.subject_specialization}")
                    
                    # Find associated user account
                    user = session.exec(select(User).where(User.teacher_id == teacher.id)).first()
                    if user:
                        st.write(f"**Username:** {user.username}")
                        st.write(f"**Role:** {user.role}")
                        status = "🟢 Active" if user.is_active else "🔴 Inactive"
                        st.write(f"**Status:** {status}")
                        if user.last_login:
                            st.write(f"**Last Login:** {user.last_login.strftime('%Y-%m-%d %H:%M')}")
                        
                        # Show assigned classes
                        if user.id is not None:
                            class_assignments = get_teacher_classes(user.id)
                            if class_assignments:
                                assigned_classes = session.exec(
                                    select(Class).where(Class.id.in_(class_assignments))
                                ).all()
                                class_names = [f"{cls.name} ({cls.category})" for cls in assigned_classes]
                                st.write(f"**Assigned Classes:** {', '.join(class_names)}")
                            else:
                                st.write("**Assigned Classes:** None")
                    else:
                        st.warning("⚠️ No user account found - create account to enable login")
                
                with col2:
                    # Password reset section
                    if user and user.id is not None:
                        password_reset_section(user.id, user.username, teacher.first_name)
                    
                    # Account management
                    if user and user.id is not None:
                        account_management_section(user.id, user.username, user.is_active)
                    
                    # Class assignment management
                    if user and user.id is not None:
                        manage_class_assignments(user.id, teacher.first_name)
                    
                    # Delete button
                    if st.button(f"🗑️ Delete Teacher", key=f"delete_teacher_{teacher.id}"):
                        delete_teacher_with_confirmation(teacher.id, f"{teacher.first_name} {teacher.last_name}")


def password_reset_section(user_id: int, username: str, teacher_name: str):
    """Password reset section for a teacher"""
    st.write("**🔐 Password Reset:**")
    
    with st.form(key=f"password_reset_{user_id}"):
        new_password = st.text_input(
            f"New Password for {teacher_name}",
            type="password",
            help="Minimum 6 characters",
            key=f"new_pass_{user_id}"
        )
        confirm_password = st.text_input(
            "Confirm New Password",
            type="password",
            key=f"confirm_pass_{user_id}"
        )
        
        if st.form_submit_button("Reset Password"):
            if not new_password or len(new_password) < 6:
                st.error("Password must be at least 6 characters long")
            elif new_password != confirm_password:
                st.error("Passwords do not match")
            else:
                success, message = reset_user_password(username, new_password)
                if success:
                    st.success(f"✅ {message}")
                else:
                    st.error(f"❌ {message}")


def account_management_section(user_id: int, username: str, is_active: bool):
    """Account activation/deactivation section"""
    st.write("**👤 Account Management:**")
    
    if is_active:
        st.write("🟢 Account Status: Active")
        if st.button("🔴 Deactivate Account", key=f"deactivate_{user_id}"):
            success, message = deactivate_user(user_id)
            if success:
                st.success(f"✅ {message}")
                st.rerun()
            else:
                st.error(f"❌ {message}")
    else:
        st.write("🔴 Account Status: Inactive")
        if st.button("🟢 Reactivate Account", key=f"reactivate_{user_id}"):
            success, message = reactivate_user(user_id)
            if success:
                st.success(f"✅ {message}")
                st.rerun()
            else:
                st.error(f"❌ {message}")


def manage_class_assignments(user_id: int, teacher_name: str):
    """Allow managing class assignments for a teacher"""
    st.write("**📚 Manage Classes:**")
    
    with get_session() as session:
        # Get all classes
        all_classes = session.exec(select(Class).order_by(Class.category, Class.name)).all()
        
        if not all_classes:
            st.info("No classes available")
            return
        
        # Get currently assigned classes
        current_assignments = get_teacher_classes(user_id)
        
        # Create multiselect with current assignments pre-selected
        class_options = [f"{cls.name} ({cls.category})" for cls in all_classes if cls.id is not None]
        current_class_names = []
        for cls in all_classes:
            if cls.id in current_assignments:
                current_class_names.append(f"{cls.name} ({cls.category})")
        
        selected_class_names = st.multiselect(
            f"Assign {teacher_name} to classes:",
            options=class_options,
            default=current_class_names,
            key=f"class_assign_{user_id}"
        )
        
        if st.button("Update Assignments", key=f"update_{user_id}"):
            # Convert selected names back to class IDs
            selected_class_ids = []
            for selected_name in selected_class_names:
                class_name = selected_name.split(" (")[0]
                selected_class = next((cls for cls in all_classes if cls.name == class_name), None)
                if selected_class and selected_class.id is not None:
                    selected_class_ids.append(selected_class.id)
            
            # Update assignments
            if assign_teacher_to_classes(user_id, selected_class_ids):
                st.success(f"✅ Updated class assignments for {teacher_name}")
                st.rerun()
            else:
                st.error("❌ Failed to update class assignments")


def delete_teacher_with_confirmation(teacher_id: int, teacher_name: str):
    """Delete teacher with confirmation"""
    if f"confirm_delete_{teacher_id}" not in st.session_state:
        st.session_state[f"confirm_delete_{teacher_id}"] = False
    
    if not st.session_state[f"confirm_delete_{teacher_id}"]:
        if st.button(f"⚠️ Confirm Delete {teacher_name}", key=f"confirm_btn_{teacher_id}"):
            st.session_state[f"confirm_delete_{teacher_id}"] = True
            st.rerun()
    else:
        st.warning(f"Are you sure you want to delete {teacher_name}? This will also delete their user account.")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Yes, Delete", key=f"final_delete_{teacher_id}"):
                success = delete_teacher_and_user(teacher_id)
                if success:
                    del st.session_state[f"confirm_delete_{teacher_id}"]
                    st.rerun()
        
        with col2:
            if st.button("❌ Cancel", key=f"cancel_delete_{teacher_id}"):
                del st.session_state[f"confirm_delete_{teacher_id}"]
                st.rerun()


def delete_teacher_and_user(teacher_id: int) -> bool:
    """Delete teacher and associated user account"""
    with get_session() as session:
        try:
            # Get teacher
            teacher = session.get(Teacher, teacher_id)
            if not teacher:
                st.error("Teacher not found")
                return False
            
            teacher_name = f"{teacher.first_name} {teacher.last_name}"
            
            # Find and delete associated user account
            user = session.exec(select(User).where(User.teacher_id == teacher_id)).first()
            if user and user.id is not None:
                # Delete class assignments first
                assignments = session.exec(select(TeacherClass).where(TeacherClass.user_id == user.id)).all()
                for assignment in assignments:
                    session.delete(assignment)
                
                # Delete user
                session.delete(user)
            
            # Delete teacher
            session.delete(teacher)
            session.commit()
            
            st.success(f"✅ Successfully deleted teacher {teacher_name} and associated user account")
            return True
            
        except Exception as e:
            session.rollback()
            st.error(f"❌ Error deleting teacher: {str(e)}")
            return False


@require_permission("teachers.view")
def teacher_statistics():
    """Display teacher statistics"""
    st.header("Teacher Statistics")
    
    with get_session() as session:
        # Basic counts - use Python filtering instead of SQLModel for problematic queries
        all_teachers = session.exec(select(Teacher)).all()
        total_teachers = len(all_teachers)
        
        all_users = session.exec(select(User)).all()
        teacher_users = [u for u in all_users if u.teacher_id is not None]
        total_users = len(teacher_users)
        
        # Class assignment stats
        all_teacher_classes = session.exec(select(TeacherClass).where(TeacherClass.is_active == True)).all()
        unique_user_ids = set(tc.user_id for tc in all_teacher_classes)
        teachers_with_classes = len(unique_user_ids)
        
        # Display metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Teachers", total_teachers)
        
        with col2:
            st.metric("With User Accounts", total_users)
        
        with col3:
            st.metric("With Class Assignments", teachers_with_classes)
        
        # Specialization breakdown
        if total_teachers > 0:
            spec_counts = {}
            for teacher in all_teachers:
                spec = teacher.subject_specialization
                if spec and spec.strip():
                    spec_counts[spec] = spec_counts.get(spec, 0) + 1
                else:
                    spec_counts['Not Specified'] = spec_counts.get('Not Specified', 0) + 1
            
            st.subheader("Teachers by Specialization")
            if spec_counts:
                st.bar_chart(spec_counts)
        
        # Active vs Inactive users
        if total_users > 0:
            active_users = len([u for u in teacher_users if u.is_active])
            inactive_users = total_users - active_users
            
            st.subheader("User Account Status")
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Active Accounts", active_users)
            with col2:
                st.metric("Inactive Accounts", inactive_users)


def password_reset_form():
    """Standalone password reset form"""
    st.header("🔐 Password Reset")
    st.write("Reset password for any teacher account")
    
    with get_session() as session:
        # Get all users with teacher accounts
        teacher_users = session.exec(
            select(User, Teacher).join(Teacher, User.teacher_id == Teacher.id)
        ).all()
        
        if not teacher_users:
            st.info("No teacher accounts found")
            return
        
        # Create options for selection
        user_options = {}
        for user, teacher in teacher_users:
            display_name = f"{teacher.first_name} {teacher.last_name} (@{user.username})"
            user_options[display_name] = user.username
        
        with st.form("password_reset_form"):
            selected_display = st.selectbox(
                "Select Teacher Account",
                options=list(user_options.keys()),
                help="Choose the teacher whose password you want to reset"
            )
            
            new_password = st.text_input(
                "New Password",
                type="password",
                help="Minimum 6 characters"
            )
            
            confirm_password = st.text_input(
                "Confirm New Password",
                type="password"
            )
            
            submitted = st.form_submit_button("Reset Password", type="primary")
            
            if submitted and selected_display:
                username = user_options[selected_display]
                
                # Validation
                if not new_password or len(new_password) < 6:
                    st.error("Password must be at least 6 characters long")
                elif new_password != confirm_password:
                    st.error("Passwords do not match")
                else:
                    success, message = reset_user_password(username, new_password)
                    if success:
                        st.success(f"✅ {message}")
                    else:
                        st.error(f"❌ {message}")