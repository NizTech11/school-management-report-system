import streamlit as st
from services.db import get_session, Teacher, Class, User, TeacherClass
from utils.rbac import create_teacher_user, get_teacher_classes, has_permission, require_permission
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
                    if selected_class:
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


def teacher_registration_form():
    """Standalone teacher registration form for new teacher accounts"""
    st.header("Add / Edit Teacher")
    
    # Get available classes for assignment
    with get_session() as session:
        classes = session.exec(select(Class).order_by(Class.category, Class.name)).all()
    
    with st.form("teacher_form"):
        first_name = st.text_input("First Name")
        last_name = st.text_input("Last Name")
        email = st.text_input("Email")
        phone = st.text_input("Phone Number (Optional)")
        specialization = st.text_input("Subject Specialization (Optional)", 
                                     placeholder="e.g., Mathematics, English, Science")
        
        # Class assignment section
        st.subheader("Class Assignment")
        
        if not classes:
            st.info("No classes available. Please create classes first before assigning teachers.")
            assign_class = None
        else:
            assign_class_option = st.selectbox(
                "Assign to Class (Optional)",
                options=["None"] + [f"{cls.name} ({cls.category})" for cls in classes],
                help="Select a class to assign this teacher to, or leave as 'None' to assign later"
            )
            
            if assign_class_option == "None":
                assign_class = None
            else:
                # Find the selected class
                class_name = assign_class_option.split(" (")[0]
                assign_class = next((cls for cls in classes if cls.name == class_name), None)
        
        submitted = st.form_submit_button("Save Teacher")
    
    if submitted and first_name and last_name and email:
        with get_session() as session:
            # Check if teacher with same email already exists
            existing = session.exec(
                select(Teacher).where(Teacher.email == email)
            ).first()
            
            if existing:
                st.error(f"Teacher with email '{email}' already exists")
            else:
                # Check if selected class already has a teacher
                if assign_class:
                    current_teacher = session.exec(
                        select(Class).where(Class.id == assign_class.id)
                    ).first()
                    
                    if current_teacher and current_teacher.teacher_id:
                        existing_teacher = session.get(Teacher, current_teacher.teacher_id)
                        if existing_teacher:
                            st.warning(f"Class '{assign_class.name}' is already assigned to {existing_teacher.first_name} {existing_teacher.last_name}. The new teacher will replace the current assignment.")
                
                # Create new teacher
                new_teacher = Teacher(
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                    phone=phone or None,
                    subject_specialization=specialization or None
                )
                session.add(new_teacher)
                session.commit()
                session.refresh(new_teacher)  # Get the ID of the newly created teacher
                
                # Assign to class if selected
                if assign_class:
                    class_to_update = session.get(Class, assign_class.id)
                    if class_to_update:
                        class_to_update.teacher_id = new_teacher.id
                        session.commit()
                        st.success(f"Teacher {first_name} {last_name} added successfully and assigned to class '{assign_class.name}'")
                    else:
                        st.error("Error assigning teacher to class")
                else:
                    st.success(f"Teacher {first_name} {last_name} added successfully")
                
                # Rerun to refresh the form
                st.rerun()
                
    elif submitted:
        st.error("Please fill in all required fields (First Name, Last Name, Email)")


def display_teachers():
    st.header("Existing Teachers")
    
    with get_session() as session:
        teachers = session.exec(select(Teacher).order_by(Teacher.last_name, Teacher.first_name)).all()
    
    if not teachers:
        st.info("No teachers have been added yet.")
        return
    
    # Display teachers in a table-like format
    for teacher in teachers:
        with st.expander(f"👨‍🏫 {teacher.first_name} {teacher.last_name}", expanded=False):
            col1, col2, col3 = st.columns([2, 2, 1])
            
            with col1:
                st.write(f"**Email:** {teacher.email}")
                if teacher.phone:
                    st.write(f"**Phone:** {teacher.phone}")
            
            with col2:
                if teacher.subject_specialization:
                    st.write(f"**Specialization:** {teacher.subject_specialization}")
                else:
                    st.write("**Specialization:** Not specified")
                
                # Show assigned classes
                display_teacher_classes(teacher.id)
            
            with col3:
                if st.button(f"Delete", key=f"delete_teacher_{teacher.id}", type="secondary"):
                    delete_teacher(teacher.id, f"{teacher.first_name} {teacher.last_name}")


def display_teacher_classes(teacher_id: int):
    """Show classes assigned to a teacher and allow reassignment"""
    with get_session() as session:
        assigned_classes = session.exec(select(Class).where(Class.teacher_id == teacher_id)).all()
        
        if assigned_classes:
            st.write("**Assigned Classes:**")
            for cls in assigned_classes:
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"• {cls.name} ({cls.category})")
                with col2:
                    if st.button("Unassign", key=f"unassign_{teacher_id}_{cls.id}", type="secondary"):
                        cls.teacher_id = None
                        session.commit()
                        st.rerun()
        else:
            st.write("**Assigned Classes:** None")
        
        # Quick assign section
        unassigned_classes = session.exec(
            select(Class).where(Class.teacher_id.is_(None)).order_by(Class.category, Class.name)
        ).all()
        
        if unassigned_classes:
            st.write("**Quick Assign to Available Class:**")
            class_options = [f"{cls.name} ({cls.category})" for cls in unassigned_classes]
            selected_class = st.selectbox(
                "Select class to assign",
                options=class_options,
                key=f"quick_assign_{teacher_id}",
                label_visibility="collapsed"
            )
            
            if st.button("Assign", key=f"assign_btn_{teacher_id}", type="primary"):
                class_name = selected_class.split(" (")[0]
                class_to_assign = next((cls for cls in unassigned_classes if cls.name == class_name), None)
                if class_to_assign:
                    class_to_assign.teacher_id = teacher_id
                    session.commit()
                    st.rerun()


def delete_teacher(teacher_id: int, teacher_name: str):
    """Delete a teacher after confirmation"""
    with get_session() as session:
        # Check if teacher is assigned to any classes
        assigned_classes = session.exec(select(Class).where(Class.teacher_id == teacher_id)).all()
        
        if assigned_classes:
            st.error(f"Cannot delete '{teacher_name}' - teacher is assigned to {len(assigned_classes)} class(es). Please reassign classes first.")
        else:
            teacher_to_delete = session.get(Teacher, teacher_id)
            if teacher_to_delete:
                session.delete(teacher_to_delete)
                session.commit()
                st.success(f"Teacher '{teacher_name}' deleted successfully")
                st.rerun()


def teacher_statistics():
    """Display teacher statistics"""
    st.header("Teacher Statistics")
    
    with get_session() as session:
        teachers = session.exec(select(Teacher)).all()
        
        if not teachers:
            st.info("No teachers to display statistics for.")
            return
        
        from services.db import Class
        classes = session.exec(select(Class)).all()
        
        # Count teachers with and without classes
        teachers_with_classes = len([t for t in teachers if any(c.teacher_id == t.id for c in classes)])
        teachers_without_classes = len(teachers) - teachers_with_classes
        
        # Count by specialization
        specializations = {}
        for teacher in teachers:
            spec = teacher.subject_specialization or "Not Specified"
            specializations[spec] = specializations.get(spec, 0) + 1
        
        # Display statistics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Teachers", len(teachers))
        
        with col2:
            st.metric("Teachers with Classes", teachers_with_classes)
        
        with col3:
            st.metric("Available Teachers", teachers_without_classes)
        
        with col4:
            st.metric("Specializations", len(specializations))
        
        # Show specialization breakdown
        if specializations:
            st.subheader("Teachers by Specialization")
            for spec, count in sorted(specializations.items()):
                st.write(f"• **{spec}**: {count} teacher(s)")
        
        # Show unassigned teachers
        unassigned_teachers = [t for t in teachers if not any(c.teacher_id == t.id for c in classes)]
        if unassigned_teachers:
            st.subheader("Unassigned Teachers")
            for teacher in unassigned_teachers:
                st.write(f"• {teacher.first_name} {teacher.last_name} ({teacher.subject_specialization or 'No specialization'})")
