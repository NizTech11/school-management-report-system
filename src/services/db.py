from __future__ import annotations
from typing import Optional, List
from sqlmodel import SQLModel, Field, Session, create_engine, select
from datetime import datetime, timedelta

class User(SQLModel, table=True):
    __table_args__ = {'extend_existing': True}
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(unique=True)
    email: str = Field(unique=True)
    hashed_password: str
    full_name: str
    role: str = Field(default="Teacher")  # Teacher, Head, Admin
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None
    teacher_id: Optional[int] = None  # Link to Teacher table for teacher users

class Role(SQLModel, table=True):
    __table_args__ = {'extend_existing': True}
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True)  # Teacher, Head, Admin
    description: str
    permissions: str  # JSON string of permissions

class Teacher(SQLModel, table=True):
    __table_args__ = {'extend_existing': True}
    id: Optional[int] = Field(default=None, primary_key=True)
    first_name: str
    last_name: str
    email: str
    phone: Optional[str] = None
    subject_specialization: Optional[str] = None

class Class(SQLModel, table=True):
    __table_args__ = {'extend_existing': True}
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    category: str  # "Lower Primary", "Upper Primary", "JHS"
    description: Optional[str] = None
    teacher_id: Optional[int] = None  # Foreign key to Teacher table

class TeacherClass(SQLModel, table=True):
    """Many-to-many relationship between Users (teachers) and Classes"""
    __table_args__ = {'extend_existing': True}
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int  # Foreign key to User table (teacher user)
    class_id: int  # Foreign key to Class table
    assigned_date: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = Field(default=True)

class Student(SQLModel, table=True):
    __table_args__ = {'extend_existing': True}
    id: Optional[int] = Field(default=None, primary_key=True)
    first_name: str
    last_name: str
    class_id: int  # Foreign key to Class table
    aggregate: Optional[float] = None  # Student's exam aggregate score

class Subject(SQLModel, table=True):
    __table_args__ = {'extend_existing': True}
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    code: str
    category: str  # Class category (Lower Primary, Upper Primary, JHS)
    subject_type: str = Field(default='elective')  # 'core' or 'elective'

class Mark(SQLModel, table=True):
    __table_args__ = {'extend_existing': True}
    id: Optional[int] = Field(default=None, primary_key=True)
    student_id: int
    subject_id: int
    term: str
    score: float = Field(ge=0, le=100)  # Enforce 0-100 range
    grade: Optional[int] = None  # Grade (1-9) calculated from score
    exam_type: str = "Mid-term"  # Mid-term, External, End of Term

class Attendance(SQLModel, table=True):
    __table_args__ = {'extend_existing': True}
    id: Optional[int] = Field(default=None, primary_key=True)
    student_id: int  # Foreign key to Student
    date: datetime  # Date of attendance record
    visit_count: int = Field(default=1)  # Number of visits/sessions attended on this date
    session_type: str = Field(default="Regular")  # Regular, Extra, Tutorial, etc.
    teacher_id: int  # Foreign key to User (who recorded attendance)
    notes: Optional[str] = None  # Additional notes about attendance
    created_at: datetime = Field(default_factory=datetime.utcnow)

class AcademicYear(SQLModel, table=True):
    __table_args__ = {'extend_existing': True}
    id: Optional[int] = Field(default=None, primary_key=True)
    year: str = Field(unique=True)  # e.g., "2024-2025"
    start_date: datetime
    end_date: datetime
    is_current: bool = Field(default=False)
    description: Optional[str] = None

class Term(SQLModel, table=True):
    __table_args__ = {'extend_existing': True}
    id: Optional[int] = Field(default=None, primary_key=True)
    academic_year_id: int  # Foreign key to AcademicYear
    name: str  # e.g., "Term 1", "Term 2", "Term 3"
    start_date: datetime
    end_date: datetime
    is_current: bool = Field(default=False)

class CalendarEvent(SQLModel, table=True):
    __table_args__ = {'extend_existing': True}
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    description: Optional[str] = None
    event_type: str  # "holiday", "exam", "meeting", "event", "deadline"
    start_date: datetime
    end_date: Optional[datetime] = None
    is_all_day: bool = Field(default=True)
    academic_year_id: Optional[int] = None
    term_id: Optional[int] = None
    class_id: Optional[int] = None  # If event is class-specific
    created_by: int  # User ID who created the event
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Timetable(SQLModel, table=True):
    __table_args__ = {'extend_existing': True}
    id: Optional[int] = Field(default=None, primary_key=True)
    class_id: int  # Foreign key to Class
    subject_id: int  # Foreign key to Subject
    teacher_id: Optional[int] = None  # Foreign key to Teacher
    day_of_week: int  # 0=Monday, 1=Tuesday, ... 6=Sunday
    start_time: str  # e.g., "08:00"
    end_time: str  # e.g., "09:00"
    room: Optional[str] = None
    academic_year_id: int  # Foreign key to AcademicYear
    term_id: Optional[int] = None  # Foreign key to Term (if term-specific)

class ExamSchedule(SQLModel, table=True):
    __table_args__ = {'extend_existing': True}
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str  # e.g., "Mid-Term Exams", "Final Exams"
    subject_id: int  # Foreign key to Subject
    class_id: int  # Foreign key to Class
    exam_date: datetime
    start_time: str  # e.g., "08:00"
    end_time: str  # e.g., "10:00"
    room: Optional[str] = None
    duration_minutes: Optional[int] = None
    instructions: Optional[str] = None
    term_id: int  # Foreign key to Term
    created_by: int  # User ID who created the schedule
    created_at: datetime = Field(default_factory=datetime.utcnow)


# Curriculum & Assessment Models

class Curriculum(SQLModel, table=True):
    __table_args__ = {'extend_existing': True}
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str  # e.g., "Mathematics Curriculum - Grade 7"
    subject_id: int  # Foreign key to Subject
    class_id: int  # Foreign key to Class
    academic_year_id: int  # Foreign key to AcademicYear
    description: Optional[str] = None
    learning_objectives: str  # JSON string of objectives
    total_lessons: int
    duration_weeks: int
    created_by: int  # User ID who created the curriculum
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    status: str = "draft"  # draft, active, archived


class Assignment(SQLModel, table=True):
    __table_args__ = {'extend_existing': True}
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    description: str
    subject_id: int  # Foreign key to Subject
    class_id: int  # Foreign key to Class
    curriculum_id: Optional[int] = None  # Foreign key to Curriculum
    assignment_type: str  # homework, project, quiz, test, essay
    due_date: datetime
    total_points: float
    instructions: Optional[str] = None
    resources: Optional[str] = None  # JSON string of resource links
    rubric_id: Optional[int] = None  # Foreign key to GradingRubric
    created_by: int  # User ID who created the assignment
    created_at: datetime = Field(default_factory=datetime.utcnow)
    status: str = "active"  # active, draft, closed, archived


class GradingRubric(SQLModel, table=True):
    __table_args__ = {'extend_existing': True}
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str  # e.g., "Essay Grading Rubric"
    description: Optional[str] = None
    subject_id: Optional[int] = None  # Can be subject-specific or general
    criteria: str  # JSON string of grading criteria
    scale_type: str = "points"  # points, percentage, letter_grade, custom
    max_score: float
    created_by: int  # User ID who created the rubric
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_template: bool = False  # Whether this is a reusable template


class StudentAssignment(SQLModel, table=True):
    __table_args__ = {'extend_existing': True}
    id: Optional[int] = Field(default=None, primary_key=True)
    assignment_id: int  # Foreign key to Assignment
    student_id: int  # Foreign key to Student
    submission_date: Optional[datetime] = None
    submission_text: Optional[str] = None
    submission_files: Optional[str] = None  # JSON string of file paths
    score: Optional[float] = None
    feedback: Optional[str] = None
    rubric_scores: Optional[str] = None  # JSON string of rubric criterion scores
    status: str = "assigned"  # assigned, submitted, graded, returned
    late_submission: bool = False
    graded_by: Optional[int] = None  # User ID who graded
    graded_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ContinuousAssessment(SQLModel, table=True):
    __table_args__ = {'extend_existing': True}
    id: Optional[int] = Field(default=None, primary_key=True)
    student_id: int  # Foreign key to Student
    subject_id: int  # Foreign key to Subject
    assessment_date: datetime
    assessment_type: str  # observation, participation, skill_check, behavior
    competency: str  # What skill/competency being assessed
    level: str  # developing, proficient, advanced, needs_support
    notes: Optional[str] = None
    teacher_id: int  # User ID of teacher making assessment
    created_at: datetime = Field(default_factory=datetime.utcnow)


class LearningObjective(SQLModel, table=True):
    __table_args__ = {'extend_existing': True}
    id: Optional[int] = Field(default=None, primary_key=True)
    curriculum_id: int  # Foreign key to Curriculum
    objective_text: str
    category: str  # knowledge, comprehension, application, analysis, synthesis, evaluation
    priority: str = "medium"  # high, medium, low
    assessment_methods: Optional[str] = None  # JSON string of assessment methods
    resources: Optional[str] = None  # JSON string of teaching resources
    order_index: int = 0  # For ordering objectives within curriculum
    created_at: datetime = Field(default_factory=datetime.utcnow)


# Advanced Reporting System Models

class ReportTemplate(SQLModel, table=True):
    __table_args__ = {'extend_existing': True}
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str  # e.g., "Student Progress Report", "Class Performance Summary"
    description: Optional[str] = None
    category: str  # "student", "class", "teacher", "school", "custom"
    template_type: str  # "pdf", "excel", "csv", "html"
    data_sources: str  # JSON string of required data sources
    layout_config: str  # JSON string of layout configuration
    fields_config: str  # JSON string of field configurations
    filters_config: str  # JSON string of available filters
    is_system: bool = Field(default=False)  # System templates vs user-created
    is_active: bool = Field(default=True)
    created_by: int  # User ID who created the template
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class CustomReport(SQLModel, table=True):
    __table_args__ = {'extend_existing': True}
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    description: Optional[str] = None
    template_id: Optional[int] = None  # Foreign key to ReportTemplate (if based on template)
    report_type: str  # "student", "class", "teacher", "school", "custom"
    data_sources: str  # JSON string of data sources used
    filters_applied: str  # JSON string of applied filters
    fields_selected: str  # JSON string of selected fields
    layout_config: str  # JSON string of custom layout
    export_format: str  # "pdf", "excel", "csv", "html"
    is_scheduled: bool = Field(default=False)
    schedule_config: Optional[str] = None  # JSON string of schedule configuration
    created_by: int  # User ID who created the report
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_generated: Optional[datetime] = None

class ReportExecution(SQLModel, table=True):
    __table_args__ = {'extend_existing': True}
    id: Optional[int] = Field(default=None, primary_key=True)
    report_id: Optional[int] = None  # Foreign key to CustomReport
    template_id: Optional[int] = None  # Foreign key to ReportTemplate
    execution_type: str  # "manual", "scheduled", "api"
    status: str  # "pending", "running", "completed", "failed"
    parameters: str  # JSON string of execution parameters
    file_path: Optional[str] = None  # Path to generated report file
    file_size: Optional[int] = None
    error_message: Optional[str] = None
    execution_time_seconds: Optional[float] = None
    executed_by: int  # User ID who executed the report
    started_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None

class ReportShare(SQLModel, table=True):
    __table_args__ = {'extend_existing': True}
    id: Optional[int] = Field(default=None, primary_key=True)
    execution_id: int  # Foreign key to ReportExecution
    shared_with: str  # JSON string of user IDs or email addresses
    access_level: str  # "view", "download", "edit"
    expiry_date: Optional[datetime] = None
    access_key: Optional[str] = None  # For secure sharing
    is_public: bool = Field(default=False)
    download_count: int = Field(default=0)
    shared_by: int  # User ID who shared the report
    created_at: datetime = Field(default_factory=datetime.utcnow)


_engine = None

def get_engine(db_url: str = "sqlite:///students.db"):
    global _engine
    if _engine is None:
        _engine = create_engine(db_url, echo=False)
        SQLModel.metadata.create_all(_engine)
    return _engine

def get_session():
    engine = get_engine()
    return Session(engine)


def calculate_grade(score: float) -> int:
    """
    Convert a score (0-100) to a grade (1-9) for primary/basic schools
    
    Grade scale:
    80-100 = Grade 1 (HIGHEST)
    70-79  = Grade 2 (HIGHER)
    65-69  = Grade 3 (HIGH)
    60-64  = Grade 4 (HIGH AVERAGE)
    55-59  = Grade 5 (AVERAGE)
    50-54  = Grade 6 (LOW AVERAGE)
    45-49  = Grade 7 (LOW)
    35-44  = Grade 8 (LOWER)
    0-34   = Grade 9 (LOWEST)
    
    Args:
        score: The score between 0-100
    
    Returns:
        int: Grade from 1-9
    
    Raises:
        ValueError: If score is not between 0 and 100
    """
    if score < 0 or score > 100:
        raise ValueError(f"Score must be between 0 and 100, got {score}")
    
    if score >= 80:
        return 1
    elif score >= 70:
        return 2
    elif score >= 65:
        return 3
    elif score >= 60:
        return 4
    elif score >= 55:
        return 5
    elif score >= 50:
        return 6
    elif score >= 45:
        return 7
    elif score >= 35:
        return 8
    else:
        return 9  # 0-34 gets grade 9


def validate_score(score: float) -> bool:
    """
    Validate that a score is within the acceptable range (0-100).
    
    Args:
        score: The score to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    return 0 <= score <= 100


def validate_and_normalize_score(score: float) -> float:
    """
    Validate and normalize a score to ensure it's within 0-100 range.
    
    Args:
        score: The score to validate and normalize
        
    Returns:
        float: The validated score
        
    Raises:
        ValueError: If score is outside 0-100 range with specific error message
    """
    if score < 0:
        raise ValueError(f"Score cannot be negative. You entered: {score}%. Valid range: 0-100%")
    elif score > 100:
        raise ValueError(f"Score cannot exceed 100%. You entered: {score}%. Valid range: 0-100%")
    
    # Round to 1 decimal place for consistency
    return round(score, 1)


def get_grade_description(grade: int) -> str:
    """
    Get the description for a grade
    
    Args:
        grade: Grade number (1-9)
    
    Returns:
        str: Grade description
    """
    grade_descriptions = {
        1: "HIGHEST",
        2: "HIGHER", 
        3: "HIGH",
        4: "HIGH AVERAGE",
        5: "AVERAGE",
        6: "LOW AVERAGE",
        7: "LOW",
        8: "LOWER",
        9: "LOWEST"
    }
    return grade_descriptions.get(grade, "Unknown")


def calculate_student_aggregate(student_id: int, term: str = "Term 3", exam_type: str = "End of Term") -> Optional[float]:
    """
    Calculate student aggregate based on 4 core subjects + 2 best elective subjects
    The aggregate is the SUM OF GRADES (not scores) using the 1-9 grading scale
    
    Args:
        student_id: The student's ID
        term: The term to calculate for
        exam_type: The exam type to use (Mid-term, External, End of Term)
    
    Returns:
        float: The calculated aggregate (sum of 6 grades), or None if insufficient data
    """
    with get_session() as session:
        # Get the student
        student = session.get(Student, student_id)
        if not student:
            return None
        
        # Get the student's class to determine category
        student_class = session.get(Class, student.class_id)
        if not student_class:
            return None
        
        # Get all subjects for the student's class category
        subjects = session.exec(
            select(Subject).where(Subject.category == student_class.category)
        ).all()
        
        # If no subjects found for exact category, fall back to all subjects
        # This handles cases where class categories don't match subject categories
        if not subjects:
            subjects = session.exec(select(Subject)).all()
        
        # Separate core and elective subjects
        core_subjects = [s for s in subjects if s.subject_type == 'core']
        elective_subjects = [s for s in subjects if s.subject_type == 'elective']
        
        # Get marks for the specified term and exam type
        marks = session.exec(
            select(Mark).where(
                Mark.student_id == student_id,
                Mark.term == term,
                Mark.exam_type == exam_type
            )
        ).all()
        
        # Create subject_id to score mapping
        mark_scores = {mark.subject_id: mark.score for mark in marks}
        
        # Get core subject grades (need exactly 4)
        core_grades = []
        for subject in core_subjects:
            if subject.id in mark_scores:
                score = mark_scores[subject.id]
                grade = calculate_grade(score)  # Convert score to grade (1-9)
                core_grades.append(grade)
        
        # Get elective subject scores and select best 2 based on actual percentage scores
        elective_score_data = []
        for subject in elective_subjects:
            if subject.id in mark_scores:
                score = mark_scores[subject.id]
                elective_score_data.append({
                    'subject_id': subject.id,
                    'score': score,
                    'grade': calculate_grade(score)
                })
        
        # Sort by score in descending order (highest scores first) to get the best performing subjects
        elective_score_data.sort(key=lambda x: x['score'], reverse=True)
        
        # Get grades from the 2 best performing elective subjects (by score, not grade)
        best_elective_grades = [data['grade'] for data in elective_score_data[:2]]
        
        # Check if we have enough grades
        if len(core_grades) < 4:
            # Not enough core subjects - cannot calculate aggregate
            return None
        
        if len(best_elective_grades) < 2:
            # Not enough elective subjects - cannot calculate aggregate
            return None
        
        # Calculate aggregate: 4 core subjects + 2 best elective subjects (sum of grades)
        core_total = sum(core_grades[:4])  # Take first 4 core grades
        elective_total = sum(best_elective_grades)  # Sum of the 2 best elective grades (by score)
        
        # Total aggregate is sum of 6 grades (minimum 6, maximum 54)
        aggregate = core_total + elective_total
        
        return aggregate


def calculate_student_aggregate_detailed(student_id: int, term: str = "Term 3", exam_type: str = "End of Term") -> Optional[dict]:
    """
    Calculate student aggregate with detailed breakdown of selected subjects for transparency
    
    Args:
        student_id: The student's ID
        term: The term to calculate for
        exam_type: The exam type to use (Mid-term, External, End of Term)
    
    Returns:
        dict: Detailed breakdown including:
            - aggregate: The calculated aggregate (sum of 6 grades)
            - core_subjects: List of core subjects used
            - selected_electives: List of the 2 best elective subjects selected
            - all_electives: List of all elective subjects available
            - calculation_details: Breakdown of the calculation
        Or None if insufficient data
    """
    with get_session() as session:
        # Get the student
        student = session.get(Student, student_id)
        if not student:
            return None
        
        # Get the student's class to determine category
        student_class = session.get(Class, student.class_id)
        if not student_class:
            return None
        
        # Get all subjects for the student's class category
        subjects = session.exec(
            select(Subject).where(Subject.category == student_class.category)
        ).all()
        
        # If no subjects found for exact category, fall back to all subjects
        if not subjects:
            subjects = session.exec(select(Subject)).all()
        
        # Separate core and elective subjects
        core_subjects = [s for s in subjects if s.subject_type == 'core']
        elective_subjects = [s for s in subjects if s.subject_type == 'elective']
        
        # Get marks for the specified term and exam type
        marks = session.exec(
            select(Mark).where(
                Mark.student_id == student_id,
                Mark.term == term,
                Mark.exam_type == exam_type
            )
        ).all()
        
        # Create subject_id to score mapping
        mark_scores = {mark.subject_id: mark.score for mark in marks}
        
        # Get core subject details (need exactly 4)
        core_subject_details = []
        for subject in core_subjects:
            if subject.id in mark_scores:
                score = mark_scores[subject.id]
                grade = calculate_grade(score)
                core_subject_details.append({
                    'subject_name': subject.name,
                    'subject_code': subject.code,
                    'score': score,
                    'grade': grade,
                    'selected': True
                })
        
        # Get elective subject details and select best 2 based on actual scores
        all_elective_details = []
        for subject in elective_subjects:
            if subject.id in mark_scores:
                score = mark_scores[subject.id]
                grade = calculate_grade(score)
                all_elective_details.append({
                    'subject_name': subject.name,
                    'subject_code': subject.code,
                    'score': score,
                    'grade': grade,
                    'selected': False  # Will be updated for selected ones
                })
        
        # Sort by score in descending order (highest scores first)
        all_elective_details.sort(key=lambda x: x['score'], reverse=True)
        
        # Mark the best 2 as selected
        selected_elective_details = all_elective_details[:2]
        for detail in selected_elective_details:
            detail['selected'] = True
        
        # Check if we have enough subjects
        if len(core_subject_details) < 4:
            return {
                'aggregate': None,
                'error': f'Insufficient core subjects: {len(core_subject_details)}/4 required',
                'core_subjects': core_subject_details,
                'selected_electives': [],
                'all_electives': all_elective_details,
                'calculation_details': None
            }
        
        if len(selected_elective_details) < 2:
            return {
                'aggregate': None,
                'error': f'Insufficient elective subjects: {len(selected_elective_details)}/2 required',
                'core_subjects': core_subject_details,
                'selected_electives': selected_elective_details,
                'all_electives': all_elective_details,
                'calculation_details': None
            }
        
        # Calculate totals
        core_grades = [detail['grade'] for detail in core_subject_details[:4]]
        elective_grades = [detail['grade'] for detail in selected_elective_details]
        
        core_total = sum(core_grades)
        elective_total = sum(elective_grades)
        aggregate = core_total + elective_total
        
        # Create calculation details
        calculation_details = {
            'core_total': core_total,
            'elective_total': elective_total,
            'aggregate': aggregate,
            'core_count': len(core_grades),
            'elective_count': len(elective_grades),
            'selection_method': 'Highest scoring elective subjects selected'
        }
        
        return {
            'aggregate': aggregate,
            'error': None,
            'core_subjects': core_subject_details[:4],
            'selected_electives': selected_elective_details,
            'all_electives': all_elective_details,
            'calculation_details': calculation_details
        }


def update_student_aggregate(student_id: int, term: str = "Term 3", exam_type: str = "End of Term") -> bool:
    """
    Calculate and update a student's aggregate score
    
    Args:
        student_id: The student's ID
        term: The term to calculate for (default: Term 3)
        exam_type: The exam type to use (default: End of Term)
    
    Returns:
        bool: True if updated successfully, False otherwise
    """
    aggregate = calculate_student_aggregate(student_id, term, exam_type)
    
    if aggregate is None:
        return False
    
    with get_session() as session:
        student = session.get(Student, student_id)
        if student:
            student.aggregate = aggregate
            session.add(student)
            session.commit()
            return True
    
    return False


def update_all_student_aggregates(term: str = "Term 3", exam_type: str = "End of Term") -> dict:
    """
    Update aggregate scores for all students
    
    Args:
        term: The term to calculate for (default: Term 3)
        exam_type: The exam type to use (default: End of Term)
    
    Returns:
        dict: Summary of updates (updated_count, failed_count, total_students)
    """
    with get_session() as session:
        students = session.exec(select(Student)).all()
        
        updated_count = 0
        failed_count = 0
        
        for student in students:
            if student.id and update_student_aggregate(student.id, term, exam_type):
                updated_count += 1
            else:
                failed_count += 1
        
        return {
            'updated_count': updated_count,
            'failed_count': failed_count,
            'total_students': len(students)
        }


# Attendance Functions

def record_attendance(student_id: int, date: datetime, visit_count: int = 1, session_type: str = "Regular", teacher_id: Optional[int] = None, notes: Optional[str] = None) -> bool:
    """
    Record attendance visit count for a student
    
    Args:
        student_id: ID of the student
        date: Date of attendance (should be date only, not datetime)
        visit_count: Number of visits/sessions attended (default: 1)
        session_type: Type of session (Regular, Extra, Tutorial, etc.)
        teacher_id: ID of the teacher recording attendance
        notes: Optional notes about the attendance
    
    Returns:
        bool: True if attendance was recorded successfully
    """
    try:
        # Convert date to start of day if it has time component
        if hasattr(date, 'hour'):
            date = date.replace(hour=0, minute=0, second=0, microsecond=0)
            
        with get_session() as session:
            # Check if attendance already exists for this student and date
            existing = session.exec(
                select(Attendance).where(
                    Attendance.student_id == student_id,
                    Attendance.date == date
                )
            ).first()
            
            if existing:
                # Update existing record - add to visit count
                existing.visit_count += visit_count
                existing.session_type = session_type
                if teacher_id:
                    existing.teacher_id = teacher_id
                if notes:
                    existing.notes = notes
                session.add(existing)
            else:
                # Create new record
                attendance = Attendance(
                    student_id=student_id,
                    date=date,
                    visit_count=visit_count,
                    session_type=session_type,
                    teacher_id=teacher_id or 1,  # Default teacher if not provided
                    notes=notes
                )
                session.add(attendance)
            
            session.commit()
            return True
            
    except Exception as e:
        print(f"Error recording attendance: {e}")
        return False


def get_attendance_for_student(student_id: int, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> List[Attendance]:
    """
    Get attendance records for a specific student
    
    Args:
        student_id: ID of the student
        start_date: Start date for filtering (optional)
        end_date: End date for filtering (optional)
    
    Returns:
        list: List of attendance records
    """
    with get_session() as session:
        query = select(Attendance).where(Attendance.student_id == student_id)
        
        if start_date:
            query = query.where(Attendance.date >= start_date)
        if end_date:
            query = query.where(Attendance.date <= end_date)
        
        return list(session.exec(query).all())


def get_attendance_by_date(date: datetime, user_id: int, user_role: str) -> List[dict]:
    """
    Get attendance records for a specific date with RBAC filtering
    
    Args:
        date: Date to get attendance for
        user_id: ID of the current user
        user_role: Role of the current user
    
    Returns:
        list: List of attendance records with student info
    """
    # Convert date to start of day if it has time component
    if hasattr(date, 'hour'):
        date = date.replace(hour=0, minute=0, second=0, microsecond=0)
    
    # Get accessible student IDs using RBAC
    from src.utils.rbac import get_user_accessible_students
    accessible_student_ids = get_user_accessible_students(user_id, user_role)
    
    # Handle special return values
    if accessible_student_ids == [-1] or accessible_student_ids == [-2]:
        return []
    
    with get_session() as session:
        # If empty list (Admin/Head), get all students
        if not accessible_student_ids:
            students = session.exec(select(Student)).all()
        else:
            # Get specific students
            students = []
            for student_id in accessible_student_ids:
                student = session.get(Student, student_id)
                if student:
                    students.append(student)
        
        result = []
        for student in students:
            if student.id:
                # Get attendance record for this student on this date
                attendance = session.exec(
                    select(Attendance).where(
                        Attendance.student_id == student.id,
                        Attendance.date == date
                    )
                ).first()
                
                result.append({
                    'student_id': student.id,
                    'student_name': f"{student.first_name} {student.last_name}",
                    'class_id': student.class_id,
                    'visit_count': attendance.visit_count if attendance else 0,
                    'session_type': attendance.session_type if attendance else 'No Session',
                    'notes': attendance.notes if attendance else None,
                    'attendance_id': attendance.id if attendance else None
                })
        
        return result


def get_attendance_summary_for_student(student_id: int, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> dict:
    """
    Get attendance summary for a specific student based on visit counts
    
    Args:
        student_id: ID of the student
        start_date: Start date for filtering (optional)
        end_date: End date for filtering (optional)
    
    Returns:
        dict: Summary with total visits, days attended, and attendance metrics
    """
    attendance_records = get_attendance_for_student(student_id, start_date, end_date)
    
    summary = {
        'total_visits': 0,
        'days_attended': len(attendance_records),
        'regular_sessions': 0,
        'extra_sessions': 0,
        'tutorial_sessions': 0,
        'other_sessions': 0,
        'average_visits_per_day': 0.0
    }
    
    for record in attendance_records:
        summary['total_visits'] += record.visit_count
        
        session_type = record.session_type.lower()
        if session_type == 'regular':
            summary['regular_sessions'] += record.visit_count
        elif session_type == 'extra':
            summary['extra_sessions'] += record.visit_count
        elif session_type == 'tutorial':
            summary['tutorial_sessions'] += record.visit_count
        else:
            summary['other_sessions'] += record.visit_count
    
    if summary['days_attended'] > 0:
        summary['average_visits_per_day'] = round(
            summary['total_visits'] / summary['days_attended'], 2
        )
    
    return summary


def calculate_attendance_rate(student_id: int, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None, expected_visits_per_day: int = 1) -> dict:
    """
    Calculate attendance rate based on expected vs actual visits
    
    Args:
        student_id: ID of the student
        start_date: Start date for calculation
        end_date: End date for calculation
        expected_visits_per_day: Expected number of visits per day
    
    Returns:
        dict: Attendance rate calculation with percentages
    """
    summary = get_attendance_summary_for_student(student_id, start_date, end_date)
    
    # Calculate date range if not provided
    if not start_date and not end_date:
        # Default to current month
        from datetime import date
        today = date.today()
        start_date = datetime.combine(today.replace(day=1), datetime.min.time())
        end_date = datetime.combine(today, datetime.max.time())
    elif not start_date and end_date:
        start_date = end_date.replace(day=1)
    elif not end_date and start_date:
        end_date = datetime.now()
    elif not start_date and not end_date:
        # Both are None, set defaults
        from datetime import date
        today = date.today()
        start_date = datetime.combine(today.replace(day=1), datetime.min.time())
        end_date = datetime.combine(today, datetime.max.time())
    
    # Ensure we have valid dates at this point
    if not start_date or not end_date:
        return {
            'actual_visits': 0,
            'expected_visits': 0,
            'attendance_rate': 0.0,
            'days_attended': 0,
            'total_school_days': 0,
            'average_visits_per_day': 0.0
        }
    
    # Calculate total expected visits
    total_days = (end_date.date() - start_date.date()).days + 1
    # Exclude weekends (assuming school days only)
    weekdays = sum(1 for i in range(total_days) 
                   if (start_date.date() + timedelta(days=i)).weekday() < 5)
    
    expected_total_visits = weekdays * expected_visits_per_day
    actual_visits = summary['total_visits']
    
    rate = 0.0
    if expected_total_visits > 0:
        rate = round((actual_visits / expected_total_visits) * 100, 1)
    
    return {
        'actual_visits': actual_visits,
        'expected_visits': expected_total_visits,
        'attendance_rate': rate,
        'days_attended': summary['days_attended'],
        'total_school_days': weekdays,
        'average_visits_per_day': summary['average_visits_per_day']
    }
