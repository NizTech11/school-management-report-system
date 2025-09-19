import streamlit as st
from services.db import get_session, Class, Teacher
from sqlmodel import select
from utils.rbac import require_permission


@require_permission("classes.create")
def class_form():
    st.header("Add / Edit Class")
    
    # Get available teachers
    with get_session() as session:
        teachers = session.exec(select(Teacher).order_by(Teacher.last_name, Teacher.first_name)).all()
    
    # Category selection
    category = st.selectbox(
        "School Category",
        ["Lower Primary", "Upper Primary", "JHS"],
        help="Select the educational level category"
    )
    
    with st.form("class_form"):
        class_name = st.text_input("Class Name", placeholder="e.g., Class 1A, Form 2B")
        description = st.text_area("Description (Optional)", placeholder="Additional details about this class")
        
        # Teacher assignment
        if teachers:
            teacher_options = ["No Teacher Assigned"] + [f"{t.first_name} {t.last_name} ({t.subject_specialization or 'No specialization'})" for t in teachers]
            selected_teacher_display = st.selectbox("Assign Teacher", teacher_options)
            
            if selected_teacher_display == "No Teacher Assigned":
                selected_teacher = None
            else:
                # Find the teacher by name
                teacher_name = selected_teacher_display.split(" (")[0]
                first_name, last_name = teacher_name.split(" ", 1)
                selected_teacher = next((t for t in teachers if t.first_name == first_name and t.last_name == last_name), None)
        else:
            st.info("No teachers available. Add teachers first to assign them to classes.")
            selected_teacher = None
        
        submitted = st.form_submit_button("Save Class")
    
    if submitted and class_name:
        with get_session() as session:
            # Check if class already exists
            existing = session.exec(
                select(Class).where(Class.name == class_name, Class.category == category)
            ).first()
            
            if existing:
                st.error(f"Class '{class_name}' already exists in {category}")
            else:
                new_class = Class(
                    name=class_name,
                    category=category,
                    description=description or None,
                    teacher_id=selected_teacher.id if selected_teacher else None
                )
                session.add(new_class)
                session.commit()
                teacher_info = f" (Teacher: {selected_teacher.first_name} {selected_teacher.last_name})" if selected_teacher else ""
                st.success(f"Class '{class_name}' added to {category}{teacher_info}")
    elif submitted:
        st.error("Please enter a class name")


def display_classes():
    st.header("Existing Classes")
    
    with get_session() as session:
        classes = session.exec(select(Class).order_by(Class.category, Class.name)).all()
        teachers = session.exec(select(Teacher)).all()
        teacher_map = {t.id: t for t in teachers}
    
    if not classes:
        st.info("No classes have been added yet.")
        return
    
    # Group classes by category
    categories = {}
    for cls in classes:
        if cls.category not in categories:
            categories[cls.category] = []
        categories[cls.category].append(cls)
    
    # Display classes by category
    for category, class_list in categories.items():
        with st.expander(f"📚 {category} ({len(class_list)} classes)", expanded=True):
            for cls in class_list:
                col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
                
                with col1:
                    st.write(f"**{cls.name}**")
                
                with col2:
                    if cls.description:
                        st.write(cls.description)
                    else:
                        st.write("*No description*")
                
                with col3:
                    if cls.teacher_id and cls.teacher_id in teacher_map:
                        teacher = teacher_map[cls.teacher_id]
                        st.write(f"**Teacher:** {teacher.first_name} {teacher.last_name}")
                        if teacher.subject_specialization:
                            st.write(f"*{teacher.subject_specialization}*")
                    else:
                        st.write("**Teacher:** Not assigned")
                
                with col4:
                    # Edit/Reassign teacher button
                    if st.button(f"Edit", key=f"edit_{cls.id}", type="secondary"):
                        edit_class_teacher(cls, teacher_map)
                    
                    if st.button(f"Delete", key=f"delete_{cls.id}", type="secondary"):
                        delete_class(cls.id, cls.name)


@require_permission("classes.edit")
def edit_class_teacher(cls, teacher_map):
    """Edit class teacher assignment"""
    st.subheader(f"Edit Class: {cls.name}")
    
    with get_session() as session:
        teachers = session.exec(select(Teacher).order_by(Teacher.last_name, Teacher.first_name)).all()
        
        if not teachers:
            st.warning("No teachers available to assign.")
            return
        
        # Current teacher info
        current_teacher = teacher_map.get(cls.teacher_id)
        if current_teacher:
            st.write(f"**Current Teacher:** {current_teacher.first_name} {current_teacher.last_name}")
        else:
            st.write("**Current Teacher:** Not assigned")
        
        # Teacher selection
        teacher_options = ["No Teacher Assigned"] + [f"{t.first_name} {t.last_name} ({t.subject_specialization or 'No specialization'})" for t in teachers]
        
        # Set default selection
        if current_teacher:
            default_index = next((i+1 for i, t in enumerate(teachers) if t.id == current_teacher.id), 0)
        else:
            default_index = 0
        
        selected_teacher_display = st.selectbox(
            "Select New Teacher", 
            teacher_options,
            index=default_index,
            key=f"teacher_select_{cls.id}"
        )
        
        if st.button("Update Teacher Assignment", key=f"update_{cls.id}"):
            if selected_teacher_display == "No Teacher Assigned":
                new_teacher_id = None
                teacher_name = "No teacher"
            else:
                teacher_name = selected_teacher_display.split(" (")[0]
                first_name, last_name = teacher_name.split(" ", 1)
                selected_teacher = next((t for t in teachers if t.first_name == first_name and t.last_name == last_name), None)
                new_teacher_id = selected_teacher.id if selected_teacher else None
                teacher_name = f"{selected_teacher.first_name} {selected_teacher.last_name}" if selected_teacher else "No teacher"
            
            # Update the class
            cls.teacher_id = new_teacher_id
            session.add(cls)
            session.commit()
            st.success(f"Class '{cls.name}' updated. Teacher: {teacher_name}")
            st.rerun()


@require_permission("classes.delete")
def delete_class(class_id: int, class_name: str):
    """Delete a class after confirmation"""
    with get_session() as session:
        # Check if any students are assigned to this class
        from services.db import Student
        students_in_class = session.exec(select(Student).where(Student.class_id == class_id)).all()
        
        if students_in_class:
            st.error(f"Cannot delete '{class_name}' - {len(students_in_class)} student(s) are assigned to this class.")
        else:
            class_to_delete = session.get(Class, class_id)
            if class_to_delete:
                session.delete(class_to_delete)
                session.commit()
                st.success(f"Class '{class_name}' deleted successfully")
                st.rerun()


def class_statistics():
    """Display class statistics"""
    st.header("Class Statistics")
    
    with get_session() as session:
        classes = session.exec(select(Class)).all()
        teachers = session.exec(select(Teacher)).all()
        teacher_map = {t.id: t for t in teachers}
        
        if not classes:
            st.info("No classes to display statistics for.")
            return
        
        # Count by category
        category_counts = {}
        classes_with_teachers = 0
        for cls in classes:
            if cls.category not in category_counts:
                category_counts[cls.category] = 0
            category_counts[cls.category] += 1
            
            if cls.teacher_id:
                classes_with_teachers += 1
        
        # Display statistics
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric("Total Classes", len(classes))
        
        with col2:
            st.metric("Lower Primary", category_counts.get("Lower Primary", 0))
        
        with col3:
            st.metric("Upper Primary", category_counts.get("Upper Primary", 0))
        
        with col4:
            st.metric("JHS", category_counts.get("JHS", 0))
        
        with col5:
            st.metric("Classes with Teachers", classes_with_teachers)
        
        # Teacher assignment overview
        st.subheader("Teacher Assignments")
        
        classes_with_teachers_list = []
        classes_without_teachers_list = []
        
        for cls in classes:
            if cls.teacher_id and cls.teacher_id in teacher_map:
                teacher = teacher_map[cls.teacher_id]
                classes_with_teachers_list.append({
                    "class": cls,
                    "teacher": teacher
                })
            else:
                classes_without_teachers_list.append(cls)
        
        # Show classes with teachers
        if classes_with_teachers_list:
            st.write("**Classes with Assigned Teachers:**")
            for item in classes_with_teachers_list:
                cls = item["class"]
                teacher = item["teacher"]
                st.write(f"• **{cls.name}** ({cls.category}) → {teacher.first_name} {teacher.last_name}")
        
        # Show classes without teachers
        if classes_without_teachers_list:
            st.write("**Classes without Assigned Teachers:**")
            for cls in classes_without_teachers_list:
                st.write(f"• **{cls.name}** ({cls.category})")
        
        # Student count per class (if students exist)
        try:
            from services.db import Student
            students = session.exec(select(Student)).all()
            
            if students:
                st.subheader("Students per Class")
                
                class_student_counts = {}
                for student in students:
                    class_obj = session.get(Class, student.class_id)
                    if class_obj:
                        class_name = f"{class_obj.name} ({class_obj.category})"
                        if class_name not in class_student_counts:
                            class_student_counts[class_name] = 0
                        class_student_counts[class_name] += 1
                
                if class_student_counts:
                    for class_name, count in sorted(class_student_counts.items()):
                        st.write(f"• **{class_name}**: {count} student(s)")
                else:
                    st.info("No students assigned to classes yet.")
        except Exception:
            # Handle case where Student table doesn't exist yet
            pass
