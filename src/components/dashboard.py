import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from services.db import get_session, Student, Subject, Mark, Class
from sqlmodel import select
from utils.rbac import get_current_user, get_user_accessible_students


def get_analytics_data():
    """Fetch and prepare data for analytics based on user role and permissions"""
    # Get current user for filtering
    current_user = get_current_user()
    if not current_user:
        st.error("Please log in to view dashboard.")
        return [], [], []
    
    user_role = current_user.get('role', '')
    user_id = current_user.get('id', 0)
    
    with get_session() as session:
        # Filter data based on user role
        if user_role == 'Teacher':
            # Get only students from teacher's assigned classes
            accessible_student_ids = get_user_accessible_students(user_id, user_role)
            
            if accessible_student_ids == [-1]:
                st.warning("No class assignments found. Please contact an administrator to assign you to classes.")
                return [], [], []
            elif accessible_student_ids == [-2]:
                st.info("You are assigned to classes, but there are no students in your assigned classes yet.")
                return [], [], []
            else:
                # Get students based on accessible IDs
                if accessible_student_ids:
                    students = []
                    for student_id in accessible_student_ids:
                        student = session.get(Student, student_id)
                        if student:
                            students.append(student)
                else:
                    students = []
        else:
            # Admin and Head can see all students
            students = session.exec(select(Student)).all()
        
        # Get all subjects (teachers can see subjects for their class categories)
        if user_role == 'Teacher' and students:
            # Get unique class categories for teacher's students
            class_categories = set()
            for student in students:
                student_class = session.get(Class, student.class_id)
                if student_class:
                    class_categories.add(student_class.category)
            
            # Get subjects for those categories
            subjects = []
            for category in class_categories:
                category_subjects = session.exec(select(Subject).where(Subject.category == category)).all()
                subjects.extend(category_subjects)
        else:
            # Admin and Head see all subjects
            subjects = session.exec(select(Subject)).all()
        
        # Get all classes (filtered for teachers)
        classes = session.exec(select(Class)).all()
        class_map = {cls.id: cls for cls in classes}
        
        # Filter marks based on accessible students
        if students:
            accessible_student_ids_set = set(s.id for s in students)
            all_marks = session.exec(select(Mark)).all()
            # Filter marks to only include those from accessible students
            marks = [mark for mark in all_marks if mark.student_id in accessible_student_ids_set]
        else:
            marks = []
        
        # Convert to simple list of dicts for processing
        marks_data = []
        for mark in marks:
            student = session.get(Student, mark.student_id)
            subject = session.get(Subject, mark.subject_id)
            
            # Skip marks with missing student or subject data
            if not student or not subject:
                continue
                
            student_class = class_map.get(student.class_id) if student else None
            
            marks_data.append({
                'score': mark.score,
                'term': mark.term,
                'student_name': f"{student.first_name} {student.last_name}",
                'class_name': f"{student_class.name} ({student_class.category})" if student_class else "Unknown",
                'student_id': student.id,
                'student_aggregate': student.aggregate,
                'subject_name': subject.name,
                'subject_code': subject.code
            })
        
        return students, subjects, marks_data


def render_summary_cards(students, subjects, marks_data):
    """Render summary statistics cards with role-aware context"""
    # Get current user for context
    current_user = get_current_user()
    user_role = current_user.get('role', '') if current_user else ''
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        if user_role == 'Teacher':
            st.metric("Your Students", len(students), help="Students in your assigned classes")
        else:
            st.metric("Total Students", len(students), help="All students in the system")
    
    with col2:
        if user_role == 'Teacher':
            st.metric("Your Subjects", len(subjects), help="Subjects taught in your classes")
        else:
            st.metric("Total Subjects", len(subjects), help="All subjects in the system")
    
    with col3:
        if marks_data:
            total_marks = len(marks_data)
            if user_role == 'Teacher':
                st.metric("Marks Entered", total_marks, help="Marks for your students")
            else:
                st.metric("Total Marks", total_marks, help="All marks in the system")
        else:
            st.metric("Marks Entered", 0)
    
    with col4:
        if marks_data:
            avg_score = sum(m['score'] for m in marks_data) / len(marks_data)
            if user_role == 'Teacher':
                st.metric("Class Average", f"{avg_score:.1f}%", help="Average score for your students")
            else:
                st.metric("Overall Average", f"{avg_score:.1f}%", help="System-wide average score")
        else:
            st.metric("Average Score", "N/A")
    
    with col5:
        # Calculate number of students who have reports (have at least one mark)
        if marks_data:
            students_with_reports = len(set(m['student_name'] for m in marks_data))
            if user_role == 'Teacher':
                st.metric("Students with Marks", students_with_reports, help="Your students who have marks entered")
            else:
                st.metric("Students with Reports", students_with_reports, help="Students who have marks entered")
        else:
            st.metric("Students with Reports", 0)


def render_grade_distribution(marks_data):
    """Render grade distribution chart"""
    if not marks_data:
        st.info("No marks data available for grade distribution")
        return
    
    # Define grade boundaries
    def get_grade(score):
        if score >= 90: return 'A'
        elif score >= 80: return 'B'
        elif score >= 70: return 'C'
        elif score >= 60: return 'D'
        else: return 'F'
    
    # Count grades
    grade_counts = {'A': 0, 'B': 0, 'C': 0, 'D': 0, 'F': 0}
    for mark in marks_data:
        grade = get_grade(mark['score'])
        grade_counts[grade] += 1
    
    fig = px.bar(
        x=list(grade_counts.keys()),
        y=list(grade_counts.values()),
        title="Grade Distribution",
        labels={'x': 'Grade', 'y': 'Number of Students'},
        color=list(grade_counts.values()),
        color_continuous_scale='RdYlGn_r'
    )
    
    st.plotly_chart(fig, use_container_width=True)


def render_class_performance(marks_data):
    """Render class-wise performance chart"""
    if not marks_data:
        st.info("No marks data available for class performance")
        return
    
    # Group by class
    class_scores = {}
    for mark in marks_data:
        class_name = mark['class_name']
        if class_name not in class_scores:
            class_scores[class_name] = []
        class_scores[class_name].append(mark['score'])
    
    # Calculate averages
    class_averages = {}
    for class_name, scores in class_scores.items():
        class_averages[class_name] = sum(scores) / len(scores)
    
    fig = px.bar(
        x=list(class_averages.keys()),
        y=list(class_averages.values()),
        title="Average Performance by Class",
        labels={'x': 'Class', 'y': 'Average Score (%)'},
        text=[f"{v:.1f}%" for v in class_averages.values()]
    )
    
    fig.update_traces(textposition='outside')
    st.plotly_chart(fig, use_container_width=True)


def render_subject_performance(marks_data):
    """Render subject-wise performance chart"""
    if not marks_data:
        st.info("No marks data available for subject performance")
        return
    
    # Group by subject
    subject_scores = {}
    for mark in marks_data:
        subject_name = mark['subject_name']
        if subject_name not in subject_scores:
            subject_scores[subject_name] = []
        subject_scores[subject_name].append(mark['score'])
    
    # Calculate averages
    subject_averages = {}
    for subject_name, scores in subject_scores.items():
        subject_averages[subject_name] = sum(scores) / len(scores)
    
    fig = px.bar(
        x=list(subject_averages.keys()),
        y=list(subject_averages.values()),
        title="Average Performance by Subject",
        labels={'x': 'Subject', 'y': 'Average Score (%)'},
        text=[f"{v:.1f}%" for v in subject_averages.values()]
    )
    
    fig.update_traces(textposition='outside')
    fig.update_xaxes(tickangle=45)
    st.plotly_chart(fig, use_container_width=True)


def render_term_comparison(marks_data):
    """Render term-wise performance comparison"""
    if not marks_data:
        st.info("No marks data available for term comparison")
        return
    
    # Group by term and subject
    term_subject_scores = {}
    for mark in marks_data:
        key = (mark['term'], mark['subject_name'])
        if key not in term_subject_scores:
            term_subject_scores[key] = []
        term_subject_scores[key].append(mark['score'])
    
    # Calculate averages and prepare data for plotting
    plot_data = []
    for (term, subject), scores in term_subject_scores.items():
        avg_score = sum(scores) / len(scores)
        plot_data.append({
            'term': term,
            'subject_name': subject,
            'score': avg_score
        })
    
    if not plot_data:
        return
    
    # Group by subject for line plotting
    subjects = list(set(d['subject_name'] for d in plot_data))
    fig = go.Figure()
    
    for subject in subjects:
        subject_data = [d for d in plot_data if d['subject_name'] == subject]
        terms = [d['term'] for d in subject_data]
        scores = [d['score'] for d in subject_data]
        
        fig.add_trace(go.Scatter(
            x=terms,
            y=scores,
            mode='lines+markers',
            name=subject,
            line=dict(width=2),
            marker=dict(size=8)
        ))
    
    fig.update_layout(
        title="Performance Trends Across Terms",
        xaxis_title="Term",
        yaxis_title="Average Score (%)",
        hovermode='x unified'
    )
    
    st.plotly_chart(fig, use_container_width=True)


def render_top_performers(marks_data):
    """Render top performing students"""
    if not marks_data:
        st.info("No marks data available for top performers")
        return
    
    # Group by student
    student_scores = {}
    for mark in marks_data:
        student_name = mark['student_name']
        if student_name not in student_scores:
            student_scores[student_name] = []
        student_scores[student_name].append(mark['score'])
    
    # Calculate averages
    student_averages = []
    for student_name, scores in student_scores.items():
        avg_score = sum(scores) / len(scores)
        student_averages.append({
            'name': student_name,
            'avg_score': avg_score,
            'num_subjects': len(scores)
        })
    
    # Sort by average score
    student_averages.sort(key=lambda x: x['avg_score'], reverse=True)
    
    st.subheader("🏆 Top 10 Performers")
    top_10 = student_averages[:10]
    
    for i, student in enumerate(top_10, 1):
        col1, col2, col3 = st.columns([1, 3, 1])
        with col1:
            st.write(f"#{i}")
        with col2:
            st.write(f"**{student['name']}**")
        with col3:
            st.write(f"{student['avg_score']:.1f}%")


def render_performance_heatmap(marks_data):
    """Render student-subject performance heatmap"""
    if not marks_data:
        st.info("No marks data available for performance heatmap")
        return
    
    # Create pivot-like structure
    students = list(set(m['student_name'] for m in marks_data))
    subjects = list(set(m['subject_name'] for m in marks_data))
    
    # Create matrix
    matrix = []
    student_labels = []
    
    for student in students:
        row = []
        for subject in subjects:
            # Find score for this student-subject combination
            score = None
            for mark in marks_data:
                if mark['student_name'] == student and mark['subject_name'] == subject:
                    score = mark['score']
                    break
            row.append(score if score is not None else 0)
        matrix.append(row)
        student_labels.append(student)
    
    if not matrix:
        return
    
    fig = px.imshow(
        matrix,
        labels=dict(x="Subject", y="Student", color="Score"),
        x=subjects,
        y=student_labels,
        title="Student-Subject Performance Heatmap",
        color_continuous_scale='RdYlGn',
        aspect="auto"
    )
    
    fig.update_layout(height=max(400, len(student_labels) * 25))
    st.plotly_chart(fig, use_container_width=True)


def render_dashboard():
    """Main dashboard rendering function"""
    # Get current user info for role display
    current_user = get_current_user()
    user_role = current_user.get('role', 'Guest') if current_user else 'Guest'
    username = current_user.get('username', 'Unknown') if current_user else 'Unknown'
    
    # Title with role indicator
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title("📊 Student Performance Dashboard")
    with col2:
        if user_role == 'Teacher':
            st.success(f"👨‍🏫 {user_role}: {username}")
            st.caption("Showing data for your assigned classes")
        elif user_role == 'Admin':
            st.info(f"🔧 {user_role}: {username}")
            st.caption("Full system access")
        elif user_role == 'Head':
            st.info(f"👩‍💼 {user_role}: {username}")
            st.caption("Full system access")
    
    # Get data
    students, subjects, marks_data = get_analytics_data()
    
    # Summary cards
    render_summary_cards(students, subjects, marks_data)
    
    st.divider()
    
    # Quick Action Buttons (role-based)
    current_user = get_current_user()
    user_role = current_user.get('role', '') if current_user else ''
    
    st.subheader("🚀 Quick Actions")
    
    if user_role == 'Teacher':
        st.write("Available actions for your assigned classes:")
        
        # Teacher actions - limited to what they can do
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("👥 View Students", use_container_width=True, type="primary"):
                st.switch_page("pages/1_Students.py")
        
        with col2:
            if st.button("📝 Enter Marks", use_container_width=True, type="primary"):
                st.switch_page("pages/4_Marks.py")
        
        with col3:
            if st.button("📋 Generate Reports", use_container_width=True, type="secondary"):
                st.switch_page("pages/6_Reports.py")
        
        with col4:
            st.write("")  # Empty space
    
    else:
        # Admin/Head actions - full access
        st.write("Quickly navigate to add new data or generate reports:")
        
        # First row of buttons
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("➕ Add Students", use_container_width=True, type="primary"):
                st.switch_page("pages/1_Students.py")
        
        with col2:
            if st.button("👥 Add Teachers", use_container_width=True, type="primary"):
                st.switch_page("pages/7_Teachers.py")
        
        with col3:
            if st.button("🏫 Add Classes", use_container_width=True, type="primary"):
                st.switch_page("pages/2_Classes.py")
        
        with col4:
            if st.button("📚 Add Subjects", use_container_width=True, type="primary"):
                st.switch_page("pages/3_Subjects.py")
        
        # Second row of buttons
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("📝 Add Marks", use_container_width=True, type="primary"):
                st.switch_page("pages/4_Marks.py")
        
        with col2:
            if st.button("📋 Generate Reports", use_container_width=True, type="secondary"):
                st.switch_page("pages/6_Reports.py")
        
        with col3:
            st.write("")  # Empty space
        
        with col4:
            st.write("")  # Empty space
    
    st.divider()
    
    # Charts in columns
    col1, col2 = st.columns(2)
    
    with col1:
        render_grade_distribution(marks_data)
        render_class_performance(marks_data)
    
    with col2:
        render_subject_performance(marks_data)
        render_term_comparison(marks_data)
    
    st.divider()
    
    # Full width charts
    col1, col2 = st.columns([2, 1])
    
    with col1:
        render_performance_heatmap(marks_data)
    
    with col2:
        render_top_performers(marks_data)
    
    # Data export section
    if marks_data:
        st.divider()
        
        # Report statistics section
        st.subheader("📈 Report Statistics")
        
        # Calculate detailed report metrics
        students_with_reports = set(m['student_name'] for m in marks_data)
        total_possible_reports = len(students)
        report_completion_rate = (len(students_with_reports) / total_possible_reports * 100) if total_possible_reports > 0 else 0
        
        # Term-wise report counts
        term_report_counts = {}
        for mark in marks_data:
            term = mark['term']
            student = mark['student_name']
            key = f"{term}_{student}"
            term_report_counts[key] = True
        
        reports_by_term = {}
        for term_student in term_report_counts.keys():
            term = term_student.split('_')[0]
            if term not in reports_by_term:
                reports_by_term[term] = 0
            reports_by_term[term] += 1
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "Report Completion Rate", 
                f"{report_completion_rate:.1f}%",
                f"{len(students_with_reports)}/{total_possible_reports} students"
            )
        
        with col2:
            total_individual_reports = sum(reports_by_term.values())
            st.metric("Total Individual Reports", total_individual_reports)
        
        with col3:
            if reports_by_term:
                most_active_term = max(reports_by_term.keys(), key=lambda x: reports_by_term[x])
                st.metric("Most Active Term", f"{most_active_term} ({reports_by_term[most_active_term]} reports)")
            else:
                st.metric("Most Active Term", "N/A")
        
        # Show term breakdown
        if reports_by_term:
            st.write("**Reports by Term:**")
            term_cols = st.columns(len(reports_by_term))
            for i, (term, count) in enumerate(reports_by_term.items()):
                with term_cols[i]:
                    st.write(f"**{term}:** {count}")
        
        st.divider()
        st.subheader("📤 Export Data")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Download Performance Report (CSV)"):
                # Convert to CSV format
                csv_lines = ["Student,Class,Subject,Term,Score"]
                for mark in marks_data:
                    line = f"{mark['student_name']},{mark['class_name']},{mark['subject_name']},{mark['term']},{mark['score']}"
                    csv_lines.append(line)
                csv_content = "\n".join(csv_lines)
                
                st.download_button(
                    label="Download CSV",
                    data=csv_content,
                    file_name="student_performance_report.csv",
                    mime="text/csv"
                )
        
        with col2:
            if st.button("Download Summary Statistics"):
                # Create summary statistics
                summary_lines = ["Class,Subject,Average_Score,Count"]
                
                # Group by class and subject
                class_subject_stats = {}
                for mark in marks_data:
                    key = (mark['class_name'], mark['subject_name'])
                    if key not in class_subject_stats:
                        class_subject_stats[key] = []
                    class_subject_stats[key].append(mark['score'])
                
                for (class_name, subject_name), scores in class_subject_stats.items():
                    avg_score = sum(scores) / len(scores)
                    count = len(scores)
                    line = f"{class_name},{subject_name},{avg_score:.2f},{count}"
                    summary_lines.append(line)
                
                summary_content = "\n".join(summary_lines)
                
                st.download_button(
                    label="Download Summary CSV",
                    data=summary_content,
                    file_name="performance_summary.csv",
                    mime="text/csv"
                )
