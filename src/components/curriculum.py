import streamlit as st
import pandas as pd
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from services.db import (
    get_session, Curriculum, Assignment, GradingRubric, StudentAssignment, 
    ContinuousAssessment, LearningObjective, Student, Subject, Class, AcademicYear
)
from sqlmodel import select
from utils.rbac import get_current_user, has_permission


def render_curriculum_management():
    """Main curriculum management interface"""
    st.header("📚 Curriculum & Assessment Management")
    
    # Get current user
    user = get_current_user()
    if not user:
        st.error("Please log in to access this page")
        return
    
    # Check permissions
    if not has_permission(user['role'], 'curriculum.manage'):
        st.error("You don't have permission to manage curriculum")
        return
    
    # Create tabs for different functions
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📋 Curriculum Planning", 
        "📝 Assignment Management", 
        "📊 Grading Rubrics", 
        "🔄 Continuous Assessment",
        "📈 Assessment Analytics"
    ])
    
    with tab1:
        render_curriculum_planning()
    
    with tab2:
        render_assignment_management()
    
    with tab3:
        render_grading_rubrics()
    
    with tab4:
        render_continuous_assessment()
    
    with tab5:
        render_assessment_analytics()


def render_curriculum_planning():
    """Curriculum planning interface"""
    st.subheader("📋 Curriculum Planning")
    
    # Action selector
    action = st.selectbox(
        "Select Action",
        ["View Curriculums", "Create New Curriculum", "Edit Curriculum"],
        key="curriculum_action"
    )
    
    if action == "Create New Curriculum":
        create_curriculum_form()
    elif action == "Edit Curriculum":
        edit_curriculum_form()
    else:
        display_curriculums()


def create_curriculum_form():
    """Form to create a new curriculum"""
    st.subheader("Create New Curriculum")
    
    with get_session() as session:
        # Get subjects and classes for dropdowns
        subjects = session.exec(select(Subject)).all()
        classes = session.exec(select(Class)).all()
        academic_years = session.exec(select(AcademicYear)).all()
    
    if not subjects or not classes or not academic_years:
        st.warning("Please ensure you have subjects, classes, and academic years set up first.")
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        name = st.text_input("Curriculum Name", placeholder="e.g., Mathematics Curriculum - Grade 7")
        subject = st.selectbox("Subject", subjects, format_func=lambda x: f"{x.name} ({x.code})")
        class_obj = st.selectbox("Class", classes, format_func=lambda x: f"{x.name} - {x.category}")
    
    with col2:
        academic_year = st.selectbox("Academic Year", academic_years, format_func=lambda x: x.year)
        total_lessons = st.number_input("Total Lessons", min_value=1, value=30)
        duration_weeks = st.number_input("Duration (Weeks)", min_value=1, value=12)
    
    description = st.text_area("Description", placeholder="Brief description of the curriculum...")
    
    # Learning Objectives
    st.subheader("Learning Objectives")
    
    # Use session state to manage objectives
    if 'objectives' not in st.session_state:
        st.session_state.objectives = []
    
    # Add objective form
    with st.expander("➕ Add Learning Objective"):
        obj_col1, obj_col2, obj_col3 = st.columns([3, 1, 1])
        
        with obj_col1:
            obj_text = st.text_area("Objective", placeholder="Students will be able to...", key="new_objective")
        
        with obj_col2:
            obj_category = st.selectbox("Category", [
                "Knowledge", "Comprehension", "Application", 
                "Analysis", "Synthesis", "Evaluation"
            ], key="obj_category")
        
        with obj_col3:
            obj_priority = st.selectbox("Priority", ["High", "Medium", "Low"], key="obj_priority")
        
        if st.button("Add Objective"):
            if obj_text:
                st.session_state.objectives.append({
                    "text": obj_text,
                    "category": obj_category.lower(),
                    "priority": obj_priority.lower()
                })
                st.rerun()
    
    # Display current objectives
    if st.session_state.objectives:
        st.write("**Current Objectives:**")
        for i, obj in enumerate(st.session_state.objectives):
            col1, col2 = st.columns([4, 1])
            with col1:
                st.write(f"{i+1}. {obj['text']} *({obj['category']}, {obj['priority']} priority)*")
            with col2:
                if st.button(f"Remove", key=f"remove_obj_{i}"):
                    st.session_state.objectives.pop(i)
                    st.rerun()
    
    # Submit form
    if st.button("Create Curriculum", type="primary"):
        if name and subject and class_obj and academic_year:
            user = get_current_user()
            
            # Create curriculum
            with get_session() as session:
                curriculum = Curriculum(
                    name=name,
                    subject_id=subject.id,
                    class_id=class_obj.id,
                    academic_year_id=academic_year.id,
                    description=description,
                    learning_objectives=json.dumps(st.session_state.objectives),
                    total_lessons=total_lessons,
                    duration_weeks=duration_weeks,
                    created_by=user['id'],
                    status="draft"
                )
                session.add(curriculum)
                session.commit()
                
                # Create learning objectives
                for i, obj in enumerate(st.session_state.objectives):
                    learning_obj = LearningObjective(
                        curriculum_id=curriculum.id,
                        objective_text=obj['text'],
                        category=obj['category'],
                        priority=obj['priority'],
                        order_index=i
                    )
                    session.add(learning_obj)
                
                session.commit()
            
            st.success(f"Curriculum '{name}' created successfully!")
            st.session_state.objectives = []  # Clear objectives
            st.rerun()
        else:
            st.error("Please fill in all required fields")


def edit_curriculum_form():
    """Form to edit existing curriculum"""
    st.subheader("Edit Curriculum")
    
    with get_session() as session:
        curriculums = session.exec(select(Curriculum)).all()
    
    if not curriculums:
        st.info("No curriculums available to edit.")
        return
    
    curriculum_to_edit = st.selectbox(
        "Select Curriculum to Edit",
        curriculums,
        format_func=lambda x: x.name
    )
    
    if curriculum_to_edit:
        st.write(f"**Editing:** {curriculum_to_edit.name}")
        # Add editing functionality here
        st.info("Curriculum editing functionality coming soon!")


def display_curriculums():
    """Display existing curriculums"""
    st.subheader("Existing Curriculums")
    
    with get_session() as session:
        # Get all curriculums with related data
        curriculums = session.exec(select(Curriculum)).all()
        
        if not curriculums:
            st.info("No curriculums created yet. Create your first curriculum using the form above.")
            return
        
        subjects = {s.id: s for s in session.exec(select(Subject)).all()}
        classes = {c.id: c for c in session.exec(select(Class)).all()}
        academic_years = {a.id: a for a in session.exec(select(AcademicYear)).all()}
    
    # Create curriculum cards
    for curriculum in curriculums:
        subject = subjects.get(curriculum.subject_id)
        class_obj = classes.get(curriculum.class_id)
        academic_year = academic_years.get(curriculum.academic_year_id)
        
        with st.container():
            st.markdown("---")
            col1, col2, col3 = st.columns([3, 1, 1])
            
            with col1:
                st.subheader(curriculum.name)
                st.write(f"**Subject:** {subject.name if subject else 'Unknown'}")
                st.write(f"**Class:** {class_obj.name if class_obj else 'Unknown'}")
                st.write(f"**Academic Year:** {academic_year.year if academic_year else 'Unknown'}")
                if curriculum.description:
                    st.write(f"**Description:** {curriculum.description}")
            
            with col2:
                st.metric("Total Lessons", curriculum.total_lessons)
                st.metric("Duration", f"{curriculum.duration_weeks} weeks")
            
            with col3:
                status_color = {"draft": "🟡", "active": "🟢", "archived": "🔴"}
                st.write(f"**Status:** {status_color.get(curriculum.status, '⚪')} {curriculum.status.title()}")
                
                if st.button(f"View Details", key=f"view_curr_{curriculum.id}"):
                    display_curriculum_details(curriculum.id)


def display_curriculum_details(curriculum_id: int):
    """Display detailed curriculum information"""
    with get_session() as session:
        curriculum = session.get(Curriculum, curriculum_id)
        objectives = session.exec(
            select(LearningObjective).where(LearningObjective.curriculum_id == curriculum_id)
        ).all()
    
    if not curriculum:
        st.error("Curriculum not found")
        return
    
    st.subheader(f"Curriculum Details: {curriculum.name}")
    
    # Parse learning objectives
    try:
        objectives_data = json.loads(curriculum.learning_objectives) if curriculum.learning_objectives else []
    except:
        objectives_data = []
    
    # Display objectives
    if objectives_data or objectives:
        st.subheader("Learning Objectives")
        
        # Show objectives from JSON (legacy)
        for i, obj in enumerate(objectives_data):
            st.write(f"{i+1}. {obj.get('text', '')}")
            st.caption(f"Category: {obj.get('category', '').title()}, Priority: {obj.get('priority', '').title()}")
        
        # Show objectives from database
        for obj in objectives:
            st.write(f"• {obj.objective_text}")
            st.caption(f"Category: {obj.category.title()}, Priority: {obj.priority.title()}")


def render_assignment_management():
    """Assignment management interface"""
    st.subheader("📝 Assignment Management")
    
    # Action selector
    action = st.selectbox(
        "Select Action",
        ["View Assignments", "Create Assignment", "Grade Assignments"],
        key="assignment_action"
    )
    
    if action == "Create Assignment":
        create_assignment_form()
    elif action == "Grade Assignments":
        grade_assignments_interface()
    else:
        display_assignments()


def create_assignment_form():
    """Form to create a new assignment"""
    st.subheader("Create New Assignment")
    
    with get_session() as session:
        subjects = session.exec(select(Subject)).all()
        classes = session.exec(select(Class)).all()
        rubrics = session.exec(select(GradingRubric)).all()
        curriculums = session.exec(select(Curriculum)).all()
    
    if not subjects or not classes:
        st.warning("Please ensure you have subjects and classes set up first.")
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        title = st.text_input("Assignment Title", placeholder="e.g., Chapter 3 Math Problems")
        subject = st.selectbox("Subject", subjects, format_func=lambda x: f"{x.name} ({x.code})")
        class_obj = st.selectbox("Class", classes, format_func=lambda x: f"{x.name} - {x.category}")
        assignment_type = st.selectbox("Type", ["homework", "project", "quiz", "test", "essay"])
    
    with col2:
        due_date = st.date_input("Due Date", value=datetime.now().date() + timedelta(days=7))
        due_time = st.time_input("Due Time", value=datetime.now().time().replace(hour=23, minute=59))
        total_points = st.number_input("Total Points", min_value=0.0, value=100.0, step=0.5)
        
        # Optional curriculum linkage
        curriculum = st.selectbox(
            "Link to Curriculum (Optional)", 
            [None] + curriculums,
            format_func=lambda x: "No Curriculum" if x is None else x.name
        )
    
    description = st.text_area("Description", placeholder="Assignment description and requirements...")
    instructions = st.text_area("Instructions", placeholder="Detailed instructions for students...")
    
    # Optional rubric
    rubric = st.selectbox(
        "Grading Rubric (Optional)",
        [None] + rubrics,
        format_func=lambda x: "No Rubric" if x is None else x.name
    )
    
    if st.button("Create Assignment", type="primary"):
        if title and description and subject and class_obj:
            user = get_current_user()
            due_datetime = datetime.combine(due_date, due_time)
            
            with get_session() as session:
                assignment = Assignment(
                    title=title,
                    description=description,
                    subject_id=subject.id,
                    class_id=class_obj.id,
                    curriculum_id=curriculum.id if curriculum else None,
                    assignment_type=assignment_type,
                    due_date=due_datetime,
                    total_points=total_points,
                    instructions=instructions,
                    rubric_id=rubric.id if rubric else None,
                    created_by=user['id']
                )
                session.add(assignment)
                session.commit()
                
                # Create student assignments for all students in the class
                students = session.exec(
                    select(Student).where(Student.class_id == class_obj.id)
                ).all()
                
                for student in students:
                    student_assignment = StudentAssignment(
                        assignment_id=assignment.id,
                        student_id=student.id,
                        status="assigned"
                    )
                    session.add(student_assignment)
                
                session.commit()
            
            st.success(f"Assignment '{title}' created and distributed to {len(students)} students!")
            st.rerun()
        else:
            st.error("Please fill in all required fields")


def display_assignments():
    """Display existing assignments"""
    st.subheader("Assignment Overview")
    
    with get_session() as session:
        assignments = session.exec(select(Assignment)).all()
        
        if not assignments:
            st.info("No assignments created yet.")
            return
        
        subjects = {s.id: s for s in session.exec(select(Subject)).all()}
        classes = {c.id: c for c in session.exec(select(Class)).all()}
    
    # Filter options
    col1, col2, col3 = st.columns(3)
    with col1:
        filter_subject = st.selectbox("Filter by Subject", ["All"] + [s.name for s in subjects.values()])
    with col2:
        filter_type = st.selectbox("Filter by Type", ["All", "homework", "project", "quiz", "test", "essay"])
    with col3:
        filter_status = st.selectbox("Filter by Status", ["All", "active", "draft", "closed", "archived"])
    
    # Display assignments
    for assignment in assignments:
        subject = subjects.get(assignment.subject_id)
        class_obj = classes.get(assignment.class_id)
        
        # Apply filters
        if filter_subject != "All" and (not subject or subject.name != filter_subject):
            continue
        if filter_type != "All" and assignment.assignment_type != filter_type:
            continue
        if filter_status != "All" and assignment.status != filter_status:
            continue
        
        with st.container():
            st.markdown("---")
            col1, col2, col3 = st.columns([3, 1, 1])
            
            with col1:
                st.subheader(assignment.title)
                st.write(f"**Subject:** {subject.name if subject else 'Unknown'}")
                st.write(f"**Class:** {class_obj.name if class_obj else 'Unknown'}")
                st.write(f"**Type:** {assignment.assignment_type.title()}")
                st.write(f"**Description:** {assignment.description[:100]}...")
            
            with col2:
                st.metric("Total Points", assignment.total_points)
                days_until_due = (assignment.due_date - datetime.now()).days
                if days_until_due >= 0:
                    st.metric("Days Until Due", days_until_due)
                else:
                    st.metric("Days Overdue", abs(days_until_due))
            
            with col3:
                status_color = {"active": "🟢", "draft": "🟡", "closed": "🔴", "archived": "⚪"}
                st.write(f"**Status:** {status_color.get(assignment.status, '⚪')} {assignment.status.title()}")
                
                if st.button(f"View Details", key=f"view_assign_{assignment.id}"):
                    display_assignment_details(assignment.id)


def display_assignment_details(assignment_id: int):
    """Display detailed assignment information"""
    with get_session() as session:
        assignment = session.get(Assignment, assignment_id)
        student_assignments = session.exec(
            select(StudentAssignment).where(StudentAssignment.assignment_id == assignment_id)
        ).all()
    
    if not assignment:
        st.error("Assignment not found")
        return
    
    st.subheader(f"Assignment: {assignment.title}")
    
    # Assignment statistics
    col1, col2, col3, col4 = st.columns(4)
    
    total_students = len(student_assignments)
    submitted = len([sa for sa in student_assignments if sa.status in ["submitted", "graded", "returned"]])
    graded = len([sa for sa in student_assignments if sa.status in ["graded", "returned"]])
    
    with col1:
        st.metric("Total Students", total_students)
    with col2:
        st.metric("Submitted", submitted)
    with col3:
        st.metric("Graded", graded)
    with col4:
        completion_rate = (submitted / total_students * 100) if total_students > 0 else 0
        st.metric("Completion Rate", f"{completion_rate:.1f}%")


def render_grading_rubrics():
    """Grading rubrics management"""
    st.subheader("📊 Grading Rubrics")
    
    action = st.selectbox(
        "Select Action",
        ["View Rubrics", "Create Rubric"],
        key="rubric_action"
    )
    
    if action == "Create Rubric":
        create_rubric_form()
    else:
        display_rubrics()


def create_rubric_form():
    """Form to create a grading rubric"""
    st.subheader("Create Grading Rubric")
    
    with get_session() as session:
        subjects = session.exec(select(Subject)).all()
    
    col1, col2 = st.columns(2)
    
    with col1:
        name = st.text_input("Rubric Name", placeholder="e.g., Essay Grading Rubric")
        subject = st.selectbox(
            "Subject (Optional)", 
            [None] + subjects,
            format_func=lambda x: "General Rubric" if x is None else f"{x.name} ({x.code})"
        )
    
    with col2:
        scale_type = st.selectbox("Scale Type", ["points", "percentage", "letter_grade"])
        max_score = st.number_input("Maximum Score", min_value=1.0, value=100.0)
    
    description = st.text_area("Description", placeholder="Brief description of this rubric...")
    
    # Rubric criteria
    st.subheader("Grading Criteria")
    
    if 'rubric_criteria' not in st.session_state:
        st.session_state.rubric_criteria = []
    
    # Add criteria form
    with st.expander("➕ Add Criterion"):
        crit_col1, crit_col2, crit_col3 = st.columns([2, 1, 1])
        
        with crit_col1:
            crit_name = st.text_input("Criterion Name", placeholder="e.g., Content Quality", key="new_criterion")
            crit_desc = st.text_area("Description", placeholder="What this criterion evaluates...", key="crit_desc")
        
        with crit_col2:
            crit_weight = st.number_input("Weight (%)", min_value=1, max_value=100, value=25, key="crit_weight")
        
        with crit_col3:
            st.write("**Performance Levels:**")
            excellent = st.number_input("Excellent", value=4, key="excellent")
            good = st.number_input("Good", value=3, key="good")
            satisfactory = st.number_input("Satisfactory", value=2, key="satisfactory")
            needs_improvement = st.number_input("Needs Improvement", value=1, key="needs_improvement")
        
        if st.button("Add Criterion"):
            if crit_name:
                st.session_state.rubric_criteria.append({
                    "name": crit_name,
                    "description": crit_desc,
                    "weight": crit_weight,
                    "levels": {
                        "excellent": excellent,
                        "good": good,
                        "satisfactory": satisfactory,
                        "needs_improvement": needs_improvement
                    }
                })
                st.rerun()
    
    # Display current criteria
    if st.session_state.rubric_criteria:
        st.write("**Current Criteria:**")
        for i, crit in enumerate(st.session_state.rubric_criteria):
            col1, col2 = st.columns([4, 1])
            with col1:
                st.write(f"{i+1}. **{crit['name']}** ({crit['weight']}%)")
                st.caption(crit['description'])
            with col2:
                if st.button(f"Remove", key=f"remove_crit_{i}"):
                    st.session_state.rubric_criteria.pop(i)
                    st.rerun()
    
    # Submit form
    if st.button("Create Rubric", type="primary"):
        if name and st.session_state.rubric_criteria:
            user = get_current_user()
            
            with get_session() as session:
                rubric = GradingRubric(
                    name=name,
                    description=description,
                    subject_id=subject.id if subject else None,
                    criteria=json.dumps(st.session_state.rubric_criteria),
                    scale_type=scale_type,
                    max_score=max_score,
                    created_by=user['id']
                )
                session.add(rubric)
                session.commit()
            
            st.success(f"Rubric '{name}' created successfully!")
            st.session_state.rubric_criteria = []
            st.rerun()
        else:
            st.error("Please provide a name and at least one criterion")


def display_rubrics():
    """Display existing rubrics"""
    st.subheader("Existing Rubrics")
    
    with get_session() as session:
        rubrics = session.exec(select(GradingRubric)).all()
        
        if not rubrics:
            st.info("No rubrics created yet.")
            return
        
        subjects = {s.id: s for s in session.exec(select(Subject)).all()}
    
    for rubric in rubrics:
        subject = subjects.get(rubric.subject_id)
        
        with st.container():
            st.markdown("---")
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.subheader(rubric.name)
                if subject:
                    st.write(f"**Subject:** {subject.name}")
                else:
                    st.write("**Type:** General Rubric")
                
                if rubric.description:
                    st.write(f"**Description:** {rubric.description}")
            
            with col2:
                st.metric("Max Score", rubric.max_score)
                st.write(f"**Scale:** {rubric.scale_type.title()}")
                
                if st.button(f"View Details", key=f"view_rubric_{rubric.id}"):
                    display_rubric_details(rubric.id)


def display_rubric_details(rubric_id: int):
    """Display detailed rubric information"""
    with get_session() as session:
        rubric = session.get(GradingRubric, rubric_id)
    
    if not rubric:
        st.error("Rubric not found")
        return
    
    st.subheader(f"Rubric: {rubric.name}")
    
    try:
        criteria = json.loads(rubric.criteria)
        
        for crit in criteria:
            st.write(f"**{crit['name']}** ({crit['weight']}%)")
            st.write(crit['description'])
            
            # Display performance levels
            levels_df = pd.DataFrame([crit['levels']])
            st.dataframe(levels_df, use_container_width=True)
            st.markdown("---")
            
    except json.JSONDecodeError:
        st.error("Error loading rubric criteria")


def render_continuous_assessment():
    """Continuous assessment interface"""
    st.subheader("🔄 Continuous Assessment")
    
    action = st.selectbox(
        "Select Action",
        ["Record Assessment", "View Assessments"],
        key="assessment_action"
    )
    
    if action == "Record Assessment":
        record_assessment_form()
    else:
        display_assessments()


def record_assessment_form():
    """Form to record continuous assessment"""
    st.subheader("Record Continuous Assessment")
    
    with get_session() as session:
        students = session.exec(select(Student)).all()
        subjects = session.exec(select(Subject)).all()
    
    if not students or not subjects:
        st.warning("Please ensure you have students and subjects set up first.")
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        student = st.selectbox("Student", students, format_func=lambda x: f"{x.first_name} {x.last_name}")
        subject = st.selectbox("Subject", subjects, format_func=lambda x: f"{x.name} ({x.code})")
        assessment_date = st.date_input("Assessment Date", value=datetime.now().date())
    
    with col2:
        assessment_type = st.selectbox("Assessment Type", [
            "observation", "participation", "skill_check", "behavior"
        ])
        competency = st.text_input("Competency/Skill", placeholder="What skill is being assessed?")
        level = st.selectbox("Performance Level", [
            "needs_support", "developing", "proficient", "advanced"
        ])
    
    notes = st.text_area("Notes", placeholder="Additional observations or comments...")
    
    if st.button("Record Assessment", type="primary"):
        if student and subject and competency:
            user = get_current_user()
            
            with get_session() as session:
                assessment = ContinuousAssessment(
                    student_id=student.id,
                    subject_id=subject.id,
                    assessment_date=datetime.combine(assessment_date, datetime.now().time()),
                    assessment_type=assessment_type,
                    competency=competency,
                    level=level,
                    notes=notes,
                    teacher_id=user['id']
                )
                session.add(assessment)
                session.commit()
            
            st.success("Assessment recorded successfully!")
            st.rerun()
        else:
            st.error("Please fill in all required fields")


def display_assessments():
    """Display continuous assessments"""
    st.subheader("Continuous Assessment Records")
    
    with get_session() as session:
        assessments = session.exec(select(ContinuousAssessment)).all()
        
        if not assessments:
            st.info("No assessments recorded yet.")
            return
        
        students = {s.id: s for s in session.exec(select(Student)).all()}
        subjects = {s.id: s for s in session.exec(select(Subject)).all()}
    
    # Create assessments table
    assessment_data = []
    for assessment in assessments:
        student = students.get(assessment.student_id)
        subject = subjects.get(assessment.subject_id)
        
        assessment_data.append({
            "Date": assessment.assessment_date.strftime("%Y-%m-%d"),
            "Student": f"{student.first_name} {student.last_name}" if student else "Unknown",
            "Subject": subject.name if subject else "Unknown",
            "Type": assessment.assessment_type.replace("_", " ").title(),
            "Competency": assessment.competency,
            "Level": assessment.level.replace("_", " ").title(),
            "Notes": assessment.notes[:50] + "..." if assessment.notes and len(assessment.notes) > 50 else assessment.notes or ""
        })
    
    df = pd.DataFrame(assessment_data)
    st.dataframe(df, use_container_width=True)


def render_assessment_analytics():
    """Assessment analytics and insights"""
    st.subheader("📈 Assessment Analytics")
    
    with get_session() as session:
        assignments = session.exec(select(Assignment)).all()
        student_assignments = session.exec(select(StudentAssignment)).all()
        assessments = session.exec(select(ContinuousAssessment)).all()
    
    if not assignments and not assessments:
        st.info("No assessment data available yet.")
        return
    
    # Assignment completion rates
    if assignments:
        st.subheader("Assignment Completion Rates")
        
        completion_data = []
        for assignment in assignments:
            assignment_submissions = [sa for sa in student_assignments if sa.assignment_id == assignment.id]
            total = len(assignment_submissions)
            submitted = len([sa for sa in assignment_submissions if sa.status in ["submitted", "graded", "returned"]])
            completion_rate = (submitted / total * 100) if total > 0 else 0
            
            completion_data.append({
                "Assignment": assignment.title,
                "Total Students": total,
                "Submitted": submitted,
                "Completion Rate": completion_rate
            })
        
        completion_df = pd.DataFrame(completion_data)
        st.dataframe(completion_df, use_container_width=True)
    
    # Continuous assessment insights
    if assessments:
        st.subheader("Continuous Assessment Summary")
        
        # Performance level distribution
        level_counts = {}
        for assessment in assessments:
            level_counts[assessment.level] = level_counts.get(assessment.level, 0) + 1
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Performance Level Distribution:**")
            for level, count in level_counts.items():
                st.metric(level.replace("_", " ").title(), count)
        
        with col2:
            # Most assessed competencies
            competency_counts = {}
            for assessment in assessments:
                competency_counts[assessment.competency] = competency_counts.get(assessment.competency, 0) + 1
            
            if competency_counts:
                st.write("**Most Assessed Competencies:**")
                sorted_competencies = sorted(competency_counts.items(), key=lambda x: x[1], reverse=True)[:5]
                for competency, count in sorted_competencies:
                    st.write(f"• {competency}: {count} assessments")


def grade_assignments_interface():
    """Interface for grading assignments"""
    st.subheader("Grade Assignments")
    
    with get_session() as session:
        # Get assignments that need grading
        assignments = session.exec(select(Assignment)).all()
        
        if not assignments:
            st.info("No assignments available for grading.")
            return
    
    # Select assignment to grade
    assignment = st.selectbox(
        "Select Assignment to Grade",
        assignments,
        format_func=lambda x: f"{x.title} ({x.assignment_type})"
    )
    
    if assignment:
        with get_session() as session:
            student_assignments = session.exec(
                select(StudentAssignment).where(StudentAssignment.assignment_id == assignment.id)
            ).all()
            students = {s.id: s for s in session.exec(select(Student)).all()}
        
        # Filter to show only submitted assignments
        submitted_assignments = [sa for sa in student_assignments if sa.status == "submitted"]
        
        if not submitted_assignments:
            st.info("No submitted assignments to grade for this assignment.")
            return
        
        st.write(f"**Assignment:** {assignment.title}")
        st.write(f"**Total Points:** {assignment.total_points}")
        st.write(f"**Submitted Assignments:** {len(submitted_assignments)}")
        
        # Grade individual submissions
        for sa in submitted_assignments:
            student = students.get(sa.student_id)
            if not student:
                continue
            
            with st.expander(f"Grade: {student.first_name} {student.last_name}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    if sa.submission_text:
                        st.write("**Submission:**")
                        st.text_area("", value=sa.submission_text, height=100, disabled=True, key=f"submission_{sa.id}")
                    
                    if sa.submission_date:
                        st.write(f"**Submitted:** {sa.submission_date.strftime('%Y-%m-%d %H:%M')}")
                        
                        # Check if late
                        if sa.submission_date > assignment.due_date:
                            st.warning("Late Submission")
                
                with col2:
                    score = st.number_input(
                        "Score",
                        min_value=0.0,
                        max_value=assignment.total_points,
                        value=sa.score if sa.score else 0.0,
                        key=f"score_{sa.id}"
                    )
                    
                    feedback = st.text_area(
                        "Feedback",
                        value=sa.feedback if sa.feedback else "",
                        placeholder="Provide feedback to the student...",
                        key=f"feedback_{sa.id}"
                    )
                    
                    if st.button(f"Save Grade", key=f"save_{sa.id}"):
                        user = get_current_user()
                        
                        with get_session() as session:
                            sa_to_update = session.get(StudentAssignment, sa.id)
                            if sa_to_update:
                                sa_to_update.score = score
                                sa_to_update.feedback = feedback
                                sa_to_update.status = "graded"
                                sa_to_update.graded_by = user['id']
                                sa_to_update.graded_at = datetime.utcnow()
                                session.commit()
                        
                        st.success("Grade saved!")
                        st.rerun()