import streamlit as st
from services.db import (get_session, Student, Subject, Mark, Class, calculate_grade, 
                        calculate_student_aggregate, calculate_student_aggregate_detailed,
                        record_attendance, get_attendance_by_date,
                        get_attendance_for_student, get_attendance_summary_for_student, 
                        calculate_attendance_rate, Attendance, get_grade_description)
from sqlmodel import select
from io import BytesIO
import io
import plotly.express as px
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from datetime import datetime
from utils.rbac import get_current_user, get_user_accessible_students
import os
import sys

# Load school configuration
try:
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config')
    if config_path not in sys.path:
        sys.path.insert(0, config_path)
    
    # Try to load from clean JSON configuration
    import json
    config_file = os.path.join(config_path, 'clean_school_settings.json')
    
    with open(config_file, 'r', encoding='utf-8') as f:
        school_json_config = json.load(f)
    
    # Create a compatibility class that reads from JSON
    class SchoolConfig:
        @property
        def SCHOOL_NAME(self):
            return school_json_config.get('school_name', 'KHAYYAM ACADEMY')
        
        @property
        def SCHOOL_SUBTITLE(self):
            return school_json_config.get('school_subtitle', 'Excellence in Islamic Education')
        
        @property
        def ADDRESS(self):
            return school_json_config.get('address', 'P.O. Box 123, School Street, City, Country')
        
        @property
        def EMAIL(self):
            return school_json_config.get('email', 'info@khayyamacademy.edu')
        
        @property
        def PHONE_NUMBERS(self):
            return school_json_config.get('phone_numbers', ['+123-456-7890', '+123-456-7891'])
        
        @property
        def LOGO_PATH(self):
            return school_json_config.get('logo_path', '')
        
        @property
        def SHOW_LOGO(self):
            return school_json_config.get('show_logo', False)
        
        @property
        def ACADEMIC_YEAR(self):
            return school_json_config.get('academic_year', '2024-2025')
        
        @property
        def CURRENT_TERM(self):
            return school_json_config.get('current_term', '3RD TERM')
        
        @property
        def REPORT_TITLES(self):
            return school_json_config.get('report_titles', {
                "Mid-term": "MID-TERM EXAMINATION REPORT",
                "End of Term": "END OF TERM EXAMINATION REPORT"
            })
        
        @property
        def GRADE_REMARKS(self):
            grade_remarks_str = school_json_config.get('grade_remarks', {})
            # Convert string keys to integers
            if grade_remarks_str:
                return {int(k): v for k, v in grade_remarks_str.items()}
            else:
                return {1: "HIGHEST", 2: "HIGHER", 3: "HIGH", 4: "GOOD", 5: "CREDIT",
                        6: "PASS", 7: "FAIR", 8: "POOR", 9: "FAIL"}
    
    # Create a global instance for easier access
    school_config = SchoolConfig()
    
except Exception as e:
    st.warning(f"Could not load JSON configuration ({str(e)}). Using default settings.")
    # Default configuration if file is not available
    class SchoolConfig:
        def __init__(self):
            pass
            
        @property
        def SCHOOL_NAME(self):
            return "KHAYYAM ACADEMY"
        
        @property  
        def SCHOOL_SUBTITLE(self):
            return "Excellence in Islamic Education"
        
        @property
        def ADDRESS(self):
            return "P.O. Box 123, School Street, City, Country"
        
        @property
        def EMAIL(self):
            return "info@khayyamacademy.edu"
        
        @property
        def PHONE_NUMBERS(self):
            return ["+123-456-7890", "+123-456-7891"]
        
        @property
        def LOGO_PATH(self):
            return ""
        
        @property
        def SHOW_LOGO(self):
            return False
        
        @property
        def ACADEMIC_YEAR(self):
            return "2024-2025"
        
        @property
        def CURRENT_TERM(self):
            return "3RD TERM"
        
        @property
        def REPORT_TITLES(self):
            return {
                "Mid-term": "MID-TERM EXAMINATION REPORT",
                "End of Term": "END OF TERM EXAMINATION REPORT"
            }
        
        @property
        def GRADE_REMARKS(self):
            return {1: "HIGHEST", 2: "HIGHER", 3: "HIGH", 4: "GOOD", 5: "CREDIT",
                    6: "PASS", 7: "FAIR", 8: "POOR", 9: "FAIL"}
    
    school_config = SchoolConfig()


def generate_professional_school_report(student_data, marks_data, aggregate_details, term="Term 3", exam_type="End of Term"):
    """
    Generate professional school report optimized for single A4 page with configurable school information
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, 
        pagesize=A4, 
        topMargin=40,
        bottomMargin=30, 
        leftMargin=45, 
        rightMargin=45
    )
    story = []
    
    # Professional color palette
    SCHOOL_BLUE = colors.Color(0.1, 0.2, 0.5)
    LIGHT_BLUE = colors.Color(0.85, 0.9, 1.0)
    ACCENT_GOLD = colors.Color(1.0, 0.8, 0.0)
    SUCCESS_GREEN = colors.Color(0.2, 0.7, 0.3)
    TEXT_GRAY = colors.Color(0.3, 0.3, 0.3)
    LIGHT_GRAY = colors.Color(0.95, 0.95, 0.95)
    
    # Compact typography styles for single page
    styles = getSampleStyleSheet()
    
    school_title_style = ParagraphStyle(
        'SchoolTitle',
        parent=styles['Title'],
        fontSize=16,
        fontName='Helvetica-Bold',
        textColor=SCHOOL_BLUE,
        alignment=TA_CENTER,
        spaceAfter=4
    )
    
    school_subtitle_style = ParagraphStyle(
        'SchoolSubtitle',
        parent=styles['Normal'],
        fontSize=10,
        fontName='Helvetica',
        textColor=TEXT_GRAY,
        alignment=TA_CENTER,
        spaceAfter=3
    )
    
    contact_style = ParagraphStyle(
        'Contact',
        parent=styles['Normal'],
        fontSize=9,
        fontName='Helvetica',
        textColor=TEXT_GRAY,
        alignment=TA_CENTER,
        spaceAfter=12
    )
    
    report_title_style = ParagraphStyle(
        'ReportTitle',
        parent=styles['Normal'],
        fontSize=12,
        fontName='Helvetica-Bold',
        textColor=colors.white,
        alignment=TA_CENTER,
        backColor=SCHOOL_BLUE,
        borderPadding=8,
        spaceAfter=15
    )
    
    section_header_style = ParagraphStyle(
        'SectionHeader',
        parent=styles['Normal'],
        fontSize=10,
        fontName='Helvetica-Bold',
        textColor=SCHOOL_BLUE,
        spaceAfter=5,
        spaceBefore=8
    )
    
    # === HEADER SECTION ===
    # Add school logo if enabled and path exists
    if school_config.SHOW_LOGO and school_config.LOGO_PATH:
        import os
        # Handle logo path - try multiple locations
        logo_path = school_config.LOGO_PATH
        possible_paths = [
            logo_path,  # Original path from config
            os.path.join("assets", "logos", os.path.basename(logo_path)),  # Relative to project root
            os.path.join("src", "assets", "logos", os.path.basename(logo_path)),  # In src folder
            os.path.join(os.path.dirname(__file__), "..", "..", "assets", "logos", os.path.basename(logo_path))  # Relative to this file
        ]
        
        working_logo_path = None
        for path in possible_paths:
            if os.path.exists(path):
                working_logo_path = path
                break
        
        if working_logo_path:
            try:
                # Create logo image with appropriate sizing
                logo_img = Image(working_logo_path, width=60, height=60)  # Small logo size for header
                logo_img.hAlign = 'CENTER'
                story.append(logo_img)
                story.append(Spacer(1, 10))
            except Exception as e:
                # If logo fails to load, continue without it
                print(f"Warning: Could not load logo from {working_logo_path}: {e}")
        else:
            print(f"Warning: Logo file not found. Tried paths: {possible_paths}")
    
    story.append(Paragraph(str(school_config.SCHOOL_NAME), school_title_style))
    story.append(Paragraph(str(school_config.SCHOOL_SUBTITLE), school_subtitle_style))
    
    # Build contact information dynamically
    contact_info = []
    if school_config.ADDRESS:
        contact_info.append(school_config.ADDRESS)
    if school_config.EMAIL:
        contact_info.append(f"📧 {school_config.EMAIL}")
    if school_config.PHONE_NUMBERS:
        contact_info.append(f"📞 {' / '.join(school_config.PHONE_NUMBERS)}")
    
    if contact_info:
        story.append(Paragraph(" | ".join(contact_info), contact_style))
    
    # Minimal separator
    story.append(Spacer(1, 8))
    
    # === REPORT TITLE ===
    current_year = school_config.ACADEMIC_YEAR.split('-')[0] if '-' in school_config.ACADEMIC_YEAR else str(datetime.now().year)
    exam_titles = {
        "Mid-term": f"{school_config.REPORT_TITLES.get('Mid-term', 'MID-TERM EXAMINATION REPORT')} ({school_config.CURRENT_TERM} {current_year})",
        "End of Term": f"{school_config.REPORT_TITLES.get('End of Term', 'END OF TERM EXAMINATION REPORT')} ({school_config.CURRENT_TERM} {current_year})",
        "External": f"EXTERNAL EXAMINATION REPORT ({school_config.CURRENT_TERM} {current_year})"
    }
    report_title = exam_titles.get(exam_type, f"EXAMINATION REPORT ({school_config.CURRENT_TERM} {current_year})")
    
    story.append(Paragraph(report_title, report_title_style))
    
    # === COMPACT STUDENT INFORMATION ===
    story.append(Paragraph("STUDENT INFORMATION", section_header_style))
    
    # Format date professionally
    current_date = datetime.now()
    formatted_date = current_date.strftime("%B %d, %Y")
    
    # More compact student info layout
    student_info_data = [
        ["Student ID:", student_data.get('student_id', 'N/A'), "", "Academic Year:", student_data.get('year', 'YEAR 1B')],
        ["Full Name:", student_data.get('name', ''), "", "Report Date:", formatted_date],
        ["Roll Number:", student_data.get('roll_number', '23'), "", "Term:", term.upper()]
    ]
    
    student_table = Table(student_info_data, colWidths=[75, 125, 20, 75, 115])
    student_table.setStyle(TableStyle([
        # Labels styling
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (3, 0), (3, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('TEXTCOLOR', (0, 0), (0, -1), SCHOOL_BLUE),
        ('TEXTCOLOR', (3, 0), (3, -1), SCHOOL_BLUE),
        
        # Data styling
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTNAME', (4, 0), (4, -1), 'Helvetica'),
        
        # Professional borders
        ('BOX', (1, 0), (1, 0), 1.5, SCHOOL_BLUE),
        ('BOX', (4, 0), (4, 0), 1.5, SCHOOL_BLUE),
        ('BOX', (1, 1), (1, 1), 1.5, SCHOOL_BLUE),
        ('BOX', (4, 1), (4, 1), 1.5, SCHOOL_BLUE),
        ('BOX', (1, 2), (1, 2), 1.5, SCHOOL_BLUE),
        ('BOX', (4, 2), (4, 2), 1.5, SCHOOL_BLUE),
        
        # Compact padding
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
    ]))
    story.append(student_table)
    story.append(Spacer(1, 15))
    
    # === ACADEMIC PERFORMANCE ===
    story.append(Paragraph("ACADEMIC PERFORMANCE", section_header_style))
    
    performance_header = ["SUBJECT", "SCORE (%)", "GRADE", "REMARKS"]
    performance_data = [performance_header]
    
    # Enhanced grade descriptions - Use configurable remarks
    performance_levels = school_config.GRADE_REMARKS
    
    # Process subjects with proper formatting
    for mark in marks_data:
        grade = mark.get('grade', '')
        score = mark.get('score', 0)
        subject_name = mark.get('subject_name', '').title()
        
        # Handle long subject names more aggressively for single page
        if len(subject_name) > 18:
            subject_name = subject_name[:15] + "..."
        
        score_display = f"{score:.1f}" if isinstance(score, float) else str(score)
        
        performance_data.append([
            subject_name,
            score_display,
            str(grade),
            performance_levels.get(grade, "N/A")  # Full remarks, not truncated
        ])
    
    # Add aggregate with special formatting
    if aggregate_details:
        performance_data.append([
            "AGGREGATE TOTAL",
            "—",
            str(aggregate_details.get('aggregate', '')),
            "FINAL GRADE"
        ])
    
    # Create more compact performance table - adjusted column widths for REMARKS
    performance_table = Table(performance_data, colWidths=[115, 70, 55, 130])
    
    perf_style = [
        # Professional header
        ('BACKGROUND', (0, 0), (-1, 0), SCHOOL_BLUE),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        
        # Content formatting
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        
        # Professional grid
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('LINEBELOW', (0, 0), (-1, 0), 2, SCHOOL_BLUE),
        
        # Compact padding
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6)
    ]
    
    # Alternating row colors for better readability
    subject_count = len(performance_data) - 1
    if aggregate_details:
        subject_count -= 1  # Exclude aggregate from alternating colors
    
    for i in range(1, subject_count + 1):
        if i % 2 == 0:
            perf_style.append(('BACKGROUND', (0, i), (-1, i), LIGHT_GRAY))
        else:
            perf_style.append(('BACKGROUND', (0, i), (-1, i), colors.white))
    
    # Special aggregate styling
    if aggregate_details:
        agg_row = len(performance_data) - 1
        perf_style.extend([
            ('BACKGROUND', (0, agg_row), (-1, agg_row), SUCCESS_GREEN),
            ('TEXTCOLOR', (0, agg_row), (-1, agg_row), colors.white),
            ('FONTNAME', (0, agg_row), (-1, agg_row), 'Helvetica-Bold'),
            ('LINEABOVE', (0, agg_row), (-1, agg_row), 2, SUCCESS_GREEN)
        ])
    
    performance_table.setStyle(TableStyle(perf_style))
    story.append(performance_table)
    story.append(Spacer(1, 12))
    
    # === SELECTED ELECTIVES (Compact) ===
    if aggregate_details and aggregate_details.get('selected_electives'):
        story.append(Paragraph("SELECTED ELECTIVE SUBJECTS", section_header_style))
        
        elective_note_style = ParagraphStyle(
            'ElectiveNote',
            parent=styles['Normal'],
            fontSize=8,
            fontName='Helvetica-Oblique',
            textColor=TEXT_GRAY,
            spaceAfter=6
        )
        
        story.append(Paragraph(
            "Best 2 elective subjects selected for aggregate calculation:",
            elective_note_style
        ))
        
        elective_data = [["SUBJECT", "SCORE (%)", "GRADE", "STATUS"]]
        
        for elective in aggregate_details['selected_electives']:
            score = elective.get('score', 0)
            subject_name = elective.get('subject_name', '').title()
            # More aggressive truncation for single page
            if len(subject_name) > 16:
                subject_name = subject_name[:13] + "..."
            
            score_display = f"{score:.1f}" if isinstance(score, float) else str(score)
            
            elective_data.append([
                subject_name,
                score_display,
                str(elective.get('grade', '')),
                "✓ SELECTED"
            ])
        
        elective_table = Table(elective_data, colWidths=[130, 70, 55, 115])
        elective_table.setStyle(TableStyle([
            # Gold header
            ('BACKGROUND', (0, 0), (-1, 0), ACCENT_GOLD),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            
            # Content styling
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            
            # Professional grid
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('LINEBELOW', (0, 0), (-1, 0), 2, ACCENT_GOLD),
            
            # Status column highlighting
            ('TEXTCOLOR', (3, 1), (3, -1), SUCCESS_GREEN),
            ('FONTNAME', (3, 1), (3, -1), 'Helvetica-Bold'),
            
            # Compact padding
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6)
        ]))
        story.append(elective_table)
    
    # === COMPACT FOOTER ===
    story.append(Spacer(1, 20))
    
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=7,
        fontName='Helvetica-Oblique',
        textColor=TEXT_GRAY,
        alignment=TA_CENTER
    )
    
    story.append(Paragraph(
        f"Report generated on {formatted_date} | Bright Kids International School",
        footer_style
    ))
    
    # Build PDF
    doc.build(story)
    buffer.seek(0)
    return buffer


def generate_school_report_pdf(student_data, marks_data, aggregate_details, term="Term 3", exam_type="End of Term"):
    """
    Generate professional school report with proper alignment and clean design
    """
    # Use the new professional template
    return generate_professional_school_report(
        student_data, 
        marks_data, 
        aggregate_details, 
        term, 
        exam_type
    )


def generate_pdf_report(title, data, headers, filename_prefix="report"):
    """Generate PDF report from data"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    story = []
    
    # Get styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=30,
        alignment=1,  # Center alignment
        textColor=colors.darkblue
    )
    
    # Add school logo if enabled and path exists
    if school_config.SHOW_LOGO and school_config.LOGO_PATH:
        import os
        # Handle logo path - try multiple locations
        logo_path = school_config.LOGO_PATH
        possible_paths = [
            logo_path,  # Original path from config
            os.path.join("assets", "logos", os.path.basename(logo_path)),  # Relative to project root
            os.path.join("src", "assets", "logos", os.path.basename(logo_path)),  # In src folder
            os.path.join(os.path.dirname(__file__), "..", "..", "assets", "logos", os.path.basename(logo_path))  # Relative to this file
        ]
        
        working_logo_path = None
        for path in possible_paths:
            if os.path.exists(path):
                working_logo_path = path
                break
        
        if working_logo_path:
            try:
                # Create logo image
                logo_img = Image(working_logo_path, width=50, height=50)
                logo_img.hAlign = 'CENTER'
                story.append(logo_img)
                story.append(Spacer(1, 15))
            except Exception as e:
                print(f"Warning: Could not load logo from {working_logo_path}: {e}")
        else:
            print(f"Warning: Logo file not found. Tried paths: {possible_paths}")
    # Add title
    story.append(Paragraph(title, title_style))
    story.append(Spacer(1, 12))
    
    # Add generation date
    date_str = datetime.now().strftime("%B %d, %Y at %I:%M %p")
    story.append(Paragraph(f"<b>Generated on:</b> {date_str}", styles['Normal']))
    story.append(Spacer(1, 20))
    
    if data:
        # Create table data
        table_data = [headers]
        for row in data:
            table_row = [str(row.get(header, "")) for header in headers]
            table_data.append(table_row)
        
        # Create table
        table = Table(table_data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
        ]))
        
        story.append(table)
        
        # Add summary statistics if numeric data exists
        numeric_columns = []
        for header in headers:
            try:
                values = [float(row.get(header, 0)) for row in data if str(row.get(header, "")).replace(".", "").replace("-", "").isdigit()]
                if values:
                    numeric_columns.append((header, values))
            except:
                continue
        
        if numeric_columns:
            story.append(Spacer(1, 20))
            story.append(Paragraph("<b>Summary Statistics</b>", styles['Heading2']))
            
            stats_data = [["Metric", "Value"]]
            for col_name, values in numeric_columns:
                if "Score" in col_name or "Grade" in col_name:
                    avg_val = sum(values) / len(values)
                    max_val = max(values)
                    min_val = min(values)
                    stats_data.extend([
                        [f"Average {col_name}", f"{avg_val:.1f}"],
                        [f"Highest {col_name}", f"{max_val:.1f}"],
                        [f"Lowest {col_name}", f"{min_val:.1f}"]
                    ])
            
            if len(stats_data) > 1:
                stats_table = Table(stats_data)
                stats_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 9),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ]))
                story.append(stats_table)
    else:
        story.append(Paragraph("No data available for this report.", styles['Normal']))
    
    # Build PDF
    doc.build(story)
    buffer.seek(0)
    return buffer


def render_reports_page():
    """Main reports page with various report generation options"""
    st.title("📋 Student Reports")
    
    # Report type selection
    report_type = st.selectbox(
        "Select Report Type",
        ["Individual Student Report", "Class Report", "Subject Report", "Term Report", "Bulk Student Exam Reports", "Attendance Management"]
    )
    
    with get_session() as session:
        # Apply role-based filtering for students
        current_user = get_current_user()
        if not current_user:
            st.error("Please log in to access reports.")
            return
            
        user_role = current_user.get('role', '')
        user_id = current_user.get('id', 0)
        
        if user_role == 'Teacher':
            # Get only students assigned to this teacher
            accessible_student_ids = get_user_accessible_students(user_id, user_role)
            
            # Handle special return values
            if accessible_student_ids == [-1]:
                st.warning("No class assignments found. Please contact an administrator to assign you to classes.")
                return
            elif accessible_student_ids == [-2]:
                st.info("You are assigned to classes, but there are no students in your assigned classes yet.")
                return
            elif accessible_student_ids:
                # Get students based on accessible IDs
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
        
        subjects = session.exec(select(Subject)).all()
        classes = session.exec(select(Class)).all()
        
        # Create class mapping for student display
        class_map = {cls.id: cls for cls in classes}
    
    if report_type == "Individual Student Report":
        render_individual_report(students, class_map)
    elif report_type == "Class Report":
        render_class_report(students, class_map)
    elif report_type == "Subject Report":
        render_subject_report(subjects)
    elif report_type == "Term Report":
        render_term_report()
    elif report_type == "Bulk Student Exam Reports":
        render_bulk_student_reports(students, class_map)
    elif report_type == "Attendance Management":
        render_attendance_management(students, class_map)


def render_individual_report(students, class_map):
    """Generate individual student report"""
    if not students:
        st.warning("No students found. Please add students first.")
        return
    
    student = st.selectbox(
        "Select Student",
        students,
        format_func=lambda x: f"{x.first_name} {x.last_name} ({class_map.get(x.class_id).name if class_map.get(x.class_id) else 'No Class'})"
    )
    
    # Check if student is selected
    if not student:
        st.info("Please select a student to generate the report.")
        return
    
    term = st.selectbox("Select Term", ["All Terms", "Term 1", "Term 2", "Term 3"])
    exam_type = st.selectbox("Select Exam Type", ["All Types", "Mid-term", "External", "End of Term"])
    
    if st.button("Generate Report"):
        with get_session() as session:
            # Display student info
            student_class = class_map.get(student.class_id)
            class_name = student_class.name if student_class else "No Class Assigned"
            
            st.subheader(f"Report for {student.first_name} {student.last_name}")
            st.write(f"**Class:** {class_name}")
            
            # Calculate aggregate score using detailed method for transparency
            # Use the actual selected term and exam type
            calc_term = term if term and term != "All Terms" else "Term 3"
            calc_exam_type = exam_type if exam_type and exam_type != "All Types" else "End of Term"
            
            detailed_aggregate = calculate_student_aggregate_detailed(student.id, calc_term, calc_exam_type)
            
            if detailed_aggregate and detailed_aggregate.get('aggregate') is not None:
                aggregate_score = detailed_aggregate['aggregate']
                
                # Show the aggregate score
                st.write(f"**Aggregate:** {aggregate_score:.0f} (Sum of 6 grades for {calc_term}, {calc_exam_type})")
                
                # Show transparency - which subjects were selected
                st.markdown("### 📊 Grade Calculation Breakdown")
                
                # Display core subjects
                if detailed_aggregate.get('core_subjects'):
                    st.write("**Core Subjects (4 subjects - all included):**")
                    core_data = []
                    for subject in detailed_aggregate['core_subjects']:
                        core_data.append({
                            "Subject": f"{subject['subject_name']} ({subject['subject_code']})",
                            "Score": f"{subject['score']:.1f}%",
                            "Grade": subject['grade']
                        })
                    st.table(core_data)
                
                # Display selected electives with transparency
                if detailed_aggregate.get('selected_electives'):
                    st.write("**Selected Elective Subjects (best 2 by highest scores):**")
                    selected_data = []
                    for subject in detailed_aggregate['selected_electives']:
                        selected_data.append({
                            "Subject": f"{subject['subject_name']} ({subject['subject_code']})",
                            "Score": f"{subject['score']:.1f}%",
                            "Grade": subject['grade'],
                            "Status": "✅ Selected"
                        })
                    st.table(selected_data)
                
                # Show all electives for complete transparency
                if detailed_aggregate.get('all_electives') and len(detailed_aggregate['all_electives']) > 2:
                    with st.expander("📝 View All Elective Subjects (for transparency)"):
                        st.write("**All elective subjects with scores:**")
                        all_electives_data = []
                        for subject in detailed_aggregate['all_electives']:
                            status = "✅ Selected" if subject['selected'] else "❌ Not selected"
                            all_electives_data.append({
                                "Subject": f"{subject['subject_name']} ({subject['subject_code']})",
                                "Score": f"{subject['score']:.1f}%",
                                "Grade": subject['grade'],
                                "Selection Status": status
                            })
                        st.table(all_electives_data)
                        
                        st.info("💡 **Selection Method:** The 2 elective subjects with the highest scores were automatically selected for your aggregate calculation to give you the best possible result.")
                
                # Show calculation details
                if detailed_aggregate.get('calculation_details'):
                    calc_details = detailed_aggregate['calculation_details']
                    st.markdown("### 🧮 Calculation Summary")
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Core Subjects Total", f"{calc_details['core_total']}")
                    with col2:
                        st.metric("Electives Total", f"{calc_details['elective_total']}")
                    with col3:
                        st.metric("Final Aggregate", f"{calc_details['aggregate']}")
                
                # Calculate overall performance indicator
                min_possible = 6  # Best possible: 6 subjects × grade 1
                max_possible = 54  # Worst possible: 6 subjects × grade 9
                performance_pct = ((max_possible - aggregate_score) / (max_possible - min_possible)) * 100
                
                if aggregate_score <= 12:  # Average grade 1-2
                    performance = "Excellent"
                elif aggregate_score <= 18:  # Average grade 2-3
                    performance = "Very Good"
                elif aggregate_score <= 24:  # Average grade 3-4
                    performance = "Good"
                elif aggregate_score <= 36:  # Average grade 4-6
                    performance = "Satisfactory"
                else:
                    performance = "Needs Improvement"
                    
                st.write(f"**Overall Performance:** {performance}")
            else:
                if detailed_aggregate and detailed_aggregate.get('error'):
                    st.error(f"**Aggregate:** {detailed_aggregate['error']}")
                else:
                    st.write(f"**Aggregate:** Cannot calculate (insufficient marks for {calc_term}, {calc_exam_type})")
            
            query = select(Mark).where(Mark.student_id == student.id)
            if term != "All Terms":
                query = query.where(Mark.term == term)
            if exam_type != "All Types":
                query = query.where(Mark.exam_type == exam_type)
            
            marks = session.exec(query).all()
            
            if not marks:
                st.warning("No marks found for this student.")
                return
            
            # Create report data
            report_data = []
            for mark in marks:
                subject = session.get(Subject, mark.subject_id)
                
                # Skip if subject doesn't exist (orphaned record)
                if not subject:
                    continue
                    
                report_data.append({
                    "Subject": subject.name,
                    "Code": subject.code,
                    "Term": mark.term,
                    "Exam Type": mark.exam_type,
                    "Score": f"{mark.score:.1f}%",
                    "Grade": get_grade(mark.score)
                })
            
            if term != "All Terms":
                st.write(f"**Term:** {term}")
            
            # Summary statistics
            # Extract numeric scores for calculations (remove % symbol)
            numeric_scores = [float(data["Score"].replace('%', '')) for data in report_data]
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Subjects", len(report_data))
            with col2:
                st.metric("Average Score", f"{sum(numeric_scores)/len(numeric_scores):.1f}%")
            with col3:
                st.metric("Highest Score", f"{max(numeric_scores):.1f}%")
            
            # Marks table
            st.subheader("Detailed Marks")
            st.table(report_data)
            
            # Performance chart
            if len(report_data) > 1:
                subjects = [data["Subject"] for data in report_data]
                # Use the already extracted numeric scores
                fig = px.bar(x=subjects, y=numeric_scores, title="Subject-wise Performance",
                           labels={'y': 'Score (%)', 'x': 'Subject'})
                st.plotly_chart(fig, use_container_width=True)
            
            # Download options
            col1, col2, col3 = st.columns(3)
            
            # CSV Download
            csv_lines = ["Subject,Code,Term,Exam Type,Score,Grade"]
            for data in report_data:
                line = f"{data['Subject']},{data['Code']},{data['Term']},{data['Exam Type']},{data['Score']},{data['Grade']}"
                csv_lines.append(line)
            csv_content = "\n".join(csv_lines)
            
            with col1:
                st.download_button(
                    label="📊 Download CSV",
                    data=csv_content,
                    file_name=f"{student.first_name}_{student.last_name}_report.csv",
                    mime="text/csv"
                )
            
            # Standard PDF Download
            pdf_title = f"Student Report: {student.first_name} {student.last_name}"
            if term != "All Terms":
                pdf_title += f" - {term}"
            if exam_type != "All Types":
                pdf_title += f" - {exam_type}"
            headers = ["Subject", "Code", "Term", "Exam Type", "Score", "Grade"]
            pdf_buffer = generate_pdf_report(pdf_title, report_data, headers)
            
            with col2:
                st.download_button(
                    label="📄 Download PDF",
                    data=pdf_buffer,
                    file_name=f"{student.first_name}_{student.last_name}_report.pdf",
                    mime="application/pdf"
                )
            
            # School Format PDF Download
            with col3:
                # Prepare data for school report
                student_data = {
                    'student_id': f"BKIS{student.id:04d}",  # Format student ID
                    'name': f"{student.first_name} {student.last_name}".upper(),
                    'year': 'YEAR 1B',  # You may want to make this dynamic based on class
                    'roll_number': '23'  # This could be derived from student data
                }
                
                # Get marks data in the format needed for the school report
                school_marks_data = []
                for data in report_data:
                    school_marks_data.append({
                        'subject_name': data['Subject'].upper(),
                        'subject_type': 'core' if data['Subject'].lower() in ['english', 'mathematics', 'science', 'history', 'social studies'] else 'elective',
                        'score': float(data['Score'].replace('%', '')),
                        'grade': int(data['Grade'])
                    })
                
                # Get detailed aggregate for transparency
                detailed_aggregate = calculate_student_aggregate_detailed(student.id, calc_term, calc_exam_type)
                
                if detailed_aggregate:
                    school_pdf_buffer = generate_school_report_pdf(
                        student_data, 
                        school_marks_data, 
                        detailed_aggregate,
                        calc_term,
                        calc_exam_type
                    )
                    
                    st.download_button(
                        label="🎓 School Report PDF",
                        data=school_pdf_buffer,
                        file_name=f"{student.first_name}_{student.last_name}_school_report.pdf",
                        mime="application/pdf",
                        help="Download in official school report format"
                    )


def render_class_report(students, class_map):
    """Generate class-wise report"""
    if not students:
        st.warning("No students found.")
        return
    
    # Get unique classes from students
    class_names = list(set([class_map.get(s.class_id).name for s in students if class_map.get(s.class_id)]))
    if not class_names:
        st.warning("No classes found for students.")
        return
        
    selected_class = st.selectbox("Select Class", class_names)
    term = st.selectbox("Select Term", ["All Terms", "Term 1", "Term 2", "Term 3"])
    exam_type = st.selectbox("Select Exam Type", ["All Types", "Mid-term", "External", "End of Term"])
    
    if st.button("Generate Class Report"):
        with get_session() as session:
            # Get students in selected class
            class_students = [s for s in students if class_map.get(s.class_id) and class_map.get(s.class_id).name == selected_class]
            
            report_data = []
            for student in class_students:
                query = select(Mark).where(Mark.student_id == student.id)
                if term != "All Terms":
                    query = query.where(Mark.term == term)
                if exam_type != "All Types":
                    query = query.where(Mark.exam_type == exam_type)
                
                marks = session.exec(query).all()
                
                if marks:
                    avg_score = sum(m.score for m in marks) / len(marks)
                    
                    # Calculate proper aggregate (sum of grades for 4 core + 2 best elective)
                    calc_term = term if term and term != "All Terms" else "Term 3"
                    calc_exam_type = exam_type if exam_type and exam_type != "All Types" else "End of Term"
                    aggregate_score = calculate_student_aggregate(student.id, calc_term, calc_exam_type)
                    
                    # Aggregate is now sum of grades (6-54 range)
                    if aggregate_score is not None:
                        aggregate_display = f"{aggregate_score:.0f}"
                        
                        # Determine performance level based on aggregate
                        if aggregate_score <= 12:  # Average grade 1-2
                            performance = "Excellent"
                        elif aggregate_score <= 18:  # Average grade 2-3
                            performance = "Very Good"
                        elif aggregate_score <= 24:  # Average grade 3-4
                            performance = "Good"
                        elif aggregate_score <= 36:  # Average grade 4-6
                            performance = "Satisfactory"
                        else:
                            performance = "Needs Improvement"
                    else:
                        aggregate_display = "N/A"
                        performance = "N/A"
                    
                    report_data.append({
                        "Student Name": f"{student.first_name} {student.last_name}",
                        "Student ID": student.id,
                        "Aggregate": aggregate_display,
                        "Performance": performance,
                        "Total Subjects": len(marks),
                        "Average Score": round(avg_score, 1),
                        "Grade": get_grade(avg_score)
                    })
            
            if not report_data:
                st.warning("No marks found for this class.")
                return
            
            # Process and display class report without pandas
            if not report_data:
                st.warning("No marks found for this class.")
                return
            
            # Display class summary
            st.subheader(f"Class Report: {selected_class}")
            if term != "All Terms":
                st.write(f"**Term:** {term}")
            
            # Calculate summary stats
            avg_scores = [data["Average Score"] for data in report_data]
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Students", len(report_data))
            with col2:
                st.metric("Class Average", f"{sum(avg_scores)/len(avg_scores):.1f}%")
            with col3:
                st.metric("Top Score", f"{max(avg_scores):.1f}%")
            
            # Sort by average score
            report_data.sort(key=lambda x: x["Average Score"], reverse=True)
            
            # Students table
            st.table(report_data)
            
            # Grade distribution
            grades = [data["Grade"] for data in report_data]
            grade_counts = {g: grades.count(g) for g in set(grades)}
            fig = px.bar(x=list(grade_counts.keys()), y=list(grade_counts.values()), 
                        title="Grade Distribution in Class")
            st.plotly_chart(fig, use_container_width=True)
            
            # Download options
            col1, col2 = st.columns(2)
            
            # CSV Download
            csv_lines = ["Student Name,Student ID,Aggregate,Performance,Total Subjects,Average Score,Grade"]
            for data in report_data:
                line = f"{data['Student Name']},{data['Student ID']},{data['Aggregate']},{data['Performance']},{data['Total Subjects']},{data['Average Score']},{data['Grade']}"
                csv_lines.append(line)
            csv_content = "\n".join(csv_lines)
            
            with col1:
                st.download_button(
                    label="📊 Download CSV",
                    data=csv_content,
                    file_name=f"{selected_class}_report.csv",
                    mime="text/csv"
                )
            
            # PDF Download
            pdf_title = f"Class Report: {selected_class}"
            if term != "All Terms":
                pdf_title += f" - {term}"
            if exam_type != "All Types":
                pdf_title += f" - {exam_type}"
            headers = ["Student Name", "Student ID", "Aggregate", "Performance", "Total Subjects", "Average Score", "Grade"]
            pdf_buffer = generate_pdf_report(pdf_title, report_data, headers)
            
            with col2:
                st.download_button(
                    label="📄 Download PDF",
                    data=pdf_buffer,
                    file_name=f"{selected_class}_report.pdf",
                    mime="application/pdf"
                )


def render_subject_report(subjects):
    """Generate subject-wise report"""
    if not subjects:
        st.warning("No subjects found.")
        return
    
    subject = st.selectbox(
        "Select Subject",
        subjects,
        format_func=lambda x: f"{x.name} ({x.code})"
    )
    
    # Check if subject is selected
    if not subject:
        st.info("Please select a subject to generate the report.")
        return
    
    term = st.selectbox("Select Term", ["All Terms", "Term 1", "Term 2", "Term 3"])
    exam_type = st.selectbox("Select Exam Type", ["All Types", "Mid-term", "External", "End of Term"])
    
    if st.button("Generate Subject Report"):
        with get_session() as session:
            query = select(Mark).where(Mark.subject_id == subject.id)
            if term != "All Terms":
                query = query.where(Mark.term == term)
            if exam_type != "All Types":
                query = query.where(Mark.exam_type == exam_type)
            
            marks = session.exec(query).all()
            
            if not marks:
                st.warning("No marks found for this subject.")
                return
            
            report_data = []
            for mark in marks:
                student = session.get(Student, mark.student_id)
                
                # Skip if student doesn't exist (orphaned record)
                if not student:
                    continue
                    
                # Get class info for the student
                student_class = session.get(Class, student.class_id) if student.class_id else None
                class_name = student_class.name if student_class else "No Class"
                
                report_data.append({
                    "Student Name": f"{student.first_name} {student.last_name}",
                    "Class": class_name,
                    "Aggregate": f"{student.aggregate:.1f}%" if student.aggregate is not None else "Not recorded",
                    "Term": mark.term,
                    "Exam Type": mark.exam_type,
                    "Score": f"{mark.score:.1f}%",
                    "Grade": get_grade(mark.score)
                })
            
            # Process and display subject report without pandas
            # Display subject summary
            st.subheader(f"Subject Report: {subject.name} ({subject.code})")
            if term != "All Terms":
                st.write(f"**Term:** {term}")
            if exam_type != "All Types":
                st.write(f"**Exam Type:** {exam_type}")
            
            # Calculate summary stats
            # Extract numeric scores for calculations (remove % symbol)
            numeric_scores = [float(data["Score"].replace('%', '')) for data in report_data]
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Students", len(report_data))
            with col2:
                st.metric("Average Score", f"{sum(numeric_scores)/len(numeric_scores):.1f}%")
            with col3:
                st.metric("Highest Score", f"{max(numeric_scores):.1f}%")
            with col4:
                st.metric("Lowest Score", f"{min(numeric_scores):.1f}%")
            
            # Sort by score (extract numeric value for sorting)
            report_data.sort(key=lambda x: float(x["Score"].replace('%', '')), reverse=True)
            
            # Marks table
            st.table(report_data)
            
            # Performance distribution
            # Use the already extracted numeric scores for histogram
            fig = px.histogram(x=numeric_scores, nbins=20, title="Score Distribution",
                             labels={'x': 'Score (%)', 'y': 'Number of Students'})
            st.plotly_chart(fig, use_container_width=True)
            
            # Download option
            csv_lines = ["Student Name,Class,Term,Exam Type,Score,Grade"]
            for data in report_data:
                line = f"{data['Student Name']},{data['Class']},{data['Term']},{data['Exam Type']},{data['Score']},{data['Grade']}"
                csv_lines.append(line)
            csv_content = "\n".join(csv_lines)
            
            # Download options
            col1, col2 = st.columns(2)
            
            with col1:
                st.download_button(
                    label="📊 Download CSV",
                    data=csv_content,
                    file_name=f"{subject.name}_report.csv",
                    mime="text/csv"
                )
            
            # PDF Download
            pdf_title = f"Subject Report: {subject.name} ({subject.code})"
            if term != "All Terms":
                pdf_title += f" - {term}"
            if exam_type != "All Types":
                pdf_title += f" - {exam_type}"
            headers = ["Student Name", "Class", "Term", "Exam Type", "Score", "Grade"]
            pdf_buffer = generate_pdf_report(pdf_title, report_data, headers)
            
            with col2:
                st.download_button(
                    label="📄 Download PDF",
                    data=pdf_buffer,
                    file_name=f"{subject.name}_report.pdf",
                    mime="application/pdf"
                )


def render_term_report():
    """Generate term-wise comparison report"""
    term = st.selectbox("Select Term", ["Term 1", "Term 2", "Term 3"])
    exam_type = st.selectbox("Select Exam Type", ["All Types", "Mid-term", "External", "End of Term"])
    
    if st.button("Generate Term Report"):
        with get_session() as session:
            query = select(Mark).where(Mark.term == term)
            if exam_type != "All Types":
                query = query.where(Mark.exam_type == exam_type)
            marks = session.exec(query).all()
            
            if not marks:
                st.warning("No marks found for this term.")
                return
            
            # Get summary by class and subject
            report_data = []
            for mark in marks:
                student = session.get(Student, mark.student_id)
                subject = session.get(Subject, mark.subject_id)
                
                # Skip if student or subject doesn't exist (orphaned record)
                if not student or not subject:
                    continue
                
                # Get class info for the student
                student_class = session.get(Class, student.class_id) if student.class_id else None
                class_name = student_class.name if student_class else "No Class"
                
                report_data.append({
                    "Class": class_name,
                    "Subject": subject.name,
                    "Student": f"{student.first_name} {student.last_name}",
                    "Exam Type": mark.exam_type,
                    "Score": f"{mark.score:.1f}%"
                })
            
            # Process and display term report without pandas
            # Display term summary
            st.subheader(f"Term Report: {term}")
            if exam_type != "All Types":
                st.write(f"**Exam Type:** {exam_type}")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Marks Entered", len(report_data))
            with col2:
                scores = [data["Score"] for data in report_data]
                st.metric("Average Score", f"{sum(scores)/len(scores):.1f}%")
            with col3:
                classes = list(set(data["Class"] for data in report_data))
                st.metric("Classes Covered", len(classes))
            
            # Summary by class
            class_summary = {}
            for data in report_data:
                class_name = data["Class"]
                if class_name not in class_summary:
                    class_summary[class_name] = []
                class_summary[class_name].append(data["Score"])
            
            class_summary_data = []
            for class_name, scores in class_summary.items():
                class_summary_data.append({
                    "Class": class_name,
                    "Average Score": round(sum(scores)/len(scores), 1),
                    "Number of Marks": len(scores)
                })
            
            st.subheader("Class Performance Summary")
            st.table(class_summary_data)
            
            # Summary by subject
            subject_summary = {}
            for data in report_data:
                subject_name = data["Subject"]
                if subject_name not in subject_summary:
                    subject_summary[subject_name] = []
                subject_summary[subject_name].append(data["Score"])
            
            subject_summary_data = []
            for subject_name, scores in subject_summary.items():
                subject_summary_data.append({
                    "Subject": subject_name,
                    "Average Score": round(sum(scores)/len(scores), 1),
                    "Number of Marks": len(scores)
                })
            
            st.subheader("Subject Performance Summary")
            st.table(subject_summary_data)
            
            # Download options
            col1, col2 = st.columns(2)
            
            # CSV Download
            csv_lines = ["Class,Subject,Student,Exam Type,Score"]
            for data in report_data:
                line = f"{data['Class']},{data['Subject']},{data['Student']},{data['Exam Type']},{data['Score']}"
                csv_lines.append(line)
            csv_content = "\n".join(csv_lines)
            
            with col1:
                st.download_button(
                    label="📊 Download CSV",
                    data=csv_content,
                    file_name=f"{term}_report.csv",
                    mime="text/csv"
                )
            
            # PDF Download
            pdf_title = f"Term Report: {term}"
            if exam_type != "All Types":
                pdf_title += f" - {exam_type}"
            headers = ["Class", "Subject", "Student", "Exam Type", "Score"]
            pdf_buffer = generate_pdf_report(pdf_title, report_data, headers)
            
            with col2:
                st.download_button(
                    label="📄 Download PDF",
                    data=pdf_buffer,
                    file_name=f"{term}_report.pdf",
                    mime="application/pdf"
                )


def get_grade(score):
    """Convert score to grade using primary school 1-9 scale"""
    return calculate_grade(score)


def render_attendance_management(students, class_map):
    """Attendance management interface for teachers"""
    st.subheader("📅 Attendance Management")
    
    # Get current user
    current_user = get_current_user()
    if not current_user:
        st.error("Please log in to access this page.")
        return
    
    user_id = current_user.get('id')
    user_role = current_user.get('role')
    
    # Validate user data
    if not user_id or not user_role:
        st.error("Invalid user session. Please log in again.")
        return
    
    # Create tabs for different attendance functions
    tab1, tab2, tab3 = st.tabs(["📝 Record Visits", "📊 View Visit Records", "📈 Visit Summary"])
    
    with tab1:
        st.subheader("Record Student Visits")
        
        # Date picker
        attendance_date = st.date_input(
            "Select Date",
            value=datetime.now().date(),
            help="Select the date to record student visits for"
        )
        
        # Handle different return types from st.date_input
        if isinstance(attendance_date, tuple):
            if len(attendance_date) > 0:
                attendance_date = attendance_date[0]
            else:
                st.error("Please select a valid date.")
                return
        
        if not attendance_date:
            st.error("Please select a valid date.")
            return
        
        # Convert date to datetime for database
        attendance_datetime = datetime.combine(attendance_date, datetime.min.time())
        
        # Get students accessible to this user based on RBAC
        if user_role == 'Teacher':
            accessible_student_ids = get_user_accessible_students(user_id, user_role)
            
            # Handle special return values
            if accessible_student_ids == [-1]:
                st.warning("No class assignments found. Please contact an administrator to assign you to classes.")
                return
            elif accessible_student_ids == [-2]:
                st.info("You are assigned to classes, but there are no students in your assigned classes yet.")
                return
            elif accessible_student_ids:
                # Get students based on accessible IDs
                accessible_students = []
                for student_id in accessible_student_ids:
                    student = next((s for s in students if s.id == student_id), None)
                    if student:
                        accessible_students.append(student)
            else:
                accessible_students = []
        else:
            # Admin/Head can see all students
            accessible_students = students
        
        if not accessible_students:
            st.warning("No students available for visit recording.")
            return
        
        # Get existing attendance records for this date
        existing_attendance = get_attendance_by_date(attendance_datetime, user_id, user_role)
        existing_by_student = {rec['student_id']: rec for rec in existing_attendance}
        
        st.write(f"**Recording visits for {attendance_date.strftime('%B %d, %Y')}**")
        st.write(f"**Students in your classes:** {len(accessible_students)}")
        
        # Create form for visit recording
        with st.form("attendance_form"):
            attendance_records = {}
            
            # Group students by class for better organization
            students_by_class = {}
            for student in accessible_students:
                class_id = student.class_id
                if class_id not in students_by_class:
                    students_by_class[class_id] = []
                students_by_class[class_id].append(student)
            
            # Display visit recording form by class
            for class_id, class_students in students_by_class.items():
                class_name = class_map.get(class_id).name if class_map.get(class_id) else f"Class {class_id}"
                st.write(f"**{class_name}**")
                
                for student in class_students:
                    if student.id:
                        col1, col2, col3, col4 = st.columns([3, 1.5, 1.5, 3])
                        
                        with col1:
                            st.write(f"{student.first_name} {student.last_name}")
                        
                        with col2:
                            # Get current visit count if exists
                            current_visits = existing_by_student.get(student.id, {}).get('visit_count', 0)
                                
                            visit_count = st.number_input(
                                f"Visits",
                                min_value=0,
                                max_value=10,
                                value=current_visits,
                                step=1,
                                key=f"visits_{student.id}",
                                help="Number of times student attended today"
                            )
                        
                        with col3:
                            # Session type
                            current_session_type = existing_by_student.get(student.id, {}).get('session_type', 'Regular')
                            if current_session_type == 'No Session':
                                current_session_type = 'Regular'
                                
                            session_type = st.selectbox(
                                f"Session Type",
                                options=['Regular', 'Extra', 'Tutorial', 'Makeup'],
                                index=['Regular', 'Extra', 'Tutorial', 'Makeup'].index(current_session_type),
                                key=f"session_{student.id}"
                            )
                        
                        with col4:
                            # Get current notes if exists
                            current_notes = existing_by_student.get(student.id, {}).get('notes', '') or ''
                            notes = st.text_input(
                                f"Notes",
                                value=current_notes,
                                key=f"notes_{student.id}",
                                placeholder="Optional notes about visits"
                            )
                        
                        attendance_records[student.id] = {
                            'visit_count': visit_count,
                            'session_type': session_type,
                            'notes': notes if notes else None
                        }
                
                st.divider()
            
            # Submit button
            submit_attendance = st.form_submit_button("💾 Save Visit Records")
            
            if submit_attendance:
                success_count = 0
                error_count = 0
                
                with st.spinner("Saving visit records..."):
                    for student_id, record in attendance_records.items():
                        try:
                            # Only save if there are actual visits recorded
                            if record['visit_count'] > 0:
                                success = record_attendance(
                                    student_id=student_id,
                                    date=attendance_datetime,
                                    visit_count=record['visit_count'],
                                    session_type=record['session_type'],
                                    teacher_id=user_id,
                                    notes=record['notes']
                                )
                                if success:
                                    success_count += 1
                                else:
                                    error_count += 1
                        except Exception as e:
                            st.error(f"Error recording visits for student {student_id}: {e}")
                            error_count += 1
                
                if success_count > 0:
                    st.success(f"✅ Successfully recorded visits for {success_count} students!")
                if error_count > 0:
                    st.error(f"❌ Failed to record visits for {error_count} students.")
                
                # Refresh the page data
                st.rerun()
    
    with tab2:
        st.subheader("View Visit Records")
        
        col1, col2 = st.columns(2)
        with col1:
            view_date = st.date_input(
                "Select Date to View",
                value=datetime.now().date(),
                key="view_date"
            )
        
        with col2:
            # Student filter for individual view
            if accessible_students:
                selected_student = st.selectbox(
                    "Filter by Student (Optional)",
                    options=[None] + accessible_students,
                    format_func=lambda x: "All Students" if x is None else f"{x.first_name} {x.last_name}",
                    key="view_student"
                )
            else:
                selected_student = None
        
        # Handle different return types from st.date_input
        if isinstance(view_date, tuple):
            if len(view_date) > 0:
                view_date = view_date[0]
            else:
                st.error("Please select a valid date.")
                return
        
        if not view_date:
            st.error("Please select a valid date.")
            return
            
        view_datetime = datetime.combine(view_date, datetime.min.time())
        
        if st.button("🔍 View Visit Records", key="view_btn"):
            if selected_student:
                # Show individual student visits
                attendance_records = get_attendance_for_student(
                    selected_student.id,
                    start_date=view_datetime,
                    end_date=view_datetime
                )
                
                if attendance_records:
                    st.write(f"**Visit Records for {selected_student.first_name} {selected_student.last_name} on {view_date}**")
                    for record in attendance_records:
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.write(f"**Visits:** {record.visit_count}")
                        with col2:
                            st.write(f"**Session:** {record.session_type}")
                        with col3:
                            st.write(f"**Notes:** {record.notes or 'None'}")
                        with col4:
                            st.write(f"**Recorded:** {record.created_at.strftime('%I:%M %p')}")
                else:
                    st.info(f"No visit records found for {selected_student.first_name} {selected_student.last_name} on {view_date}")
            else:
                # Show all students visits for the date
                attendance_records = get_attendance_by_date(view_datetime, user_id, user_role)
                
                if attendance_records:
                    st.write(f"**Class Visit Records for {view_date.strftime('%B %d, %Y')}**")
                    
                    # Create a nice table display
                    col1, col2, col3, col4, col5 = st.columns([3, 1, 2, 2, 3])
                    with col1:
                        st.write("**Student Name**")
                    with col2:
                        st.write("**Visits**")
                    with col3:
                        st.write("**Session Type**")
                    with col4:
                        st.write("**Class**")
                    with col5:
                        st.write("**Notes**")
                    
                    st.divider()
                    
                    total_visits = 0
                    for record in attendance_records:
                        col1, col2, col3, col4, col5 = st.columns([3, 1, 2, 2, 3])
                        with col1:
                            st.write(record['student_name'])
                        with col2:
                            visits = record['visit_count']
                            if visits > 0:
                                st.success(f"{visits}")
                                total_visits += visits
                            else:
                                st.info("0")
                        with col3:
                            st.write(record['session_type'])
                        with col4:
                            class_name = class_map.get(record['class_id']).name if class_map.get(record['class_id']) else f"Class {record['class_id']}"
                            st.write(class_name)
                        with col5:
                            st.write(record['notes'] or '-')
                    
                    st.divider()
                    st.metric("Total Visits Today", total_visits)
                else:
                    st.info(f"No visit records found for {view_date}")
    
    with tab3:
        st.subheader("Visit Summary & Statistics")
        
        col1, col2 = st.columns(2)
        with col1:
            summary_start = st.date_input(
                "Start Date",
                value=datetime.now().date().replace(day=1),  # First day of current month
                key="summary_start"
            )
        
        with col2:
            summary_end = st.date_input(
                "End Date", 
                value=datetime.now().date(),
                key="summary_end"
            )
        
        # Handle different return types from st.date_input
        if isinstance(summary_start, tuple):
            summary_start = summary_start[0] if len(summary_start) > 0 else None
        if isinstance(summary_end, tuple):
            summary_end = summary_end[0] if len(summary_end) > 0 else None
            
        if not summary_start or not summary_end:
            st.error("Please select valid start and end dates.")
            return
        
        # Expected visits per day setting
        col1, col2 = st.columns(2)
        with col1:
            expected_daily_visits = st.number_input(
                "Expected Visits Per School Day",
                min_value=1,
                max_value=10,
                value=1,
                help="How many visits do you expect per student per school day?"
            )
        
        if st.button("📊 Generate Visit Summary", key="summary_btn"):
            if summary_start <= summary_end:
                # Convert to datetime
                start_datetime = datetime.combine(summary_start, datetime.min.time())
                end_datetime = datetime.combine(summary_end, datetime.max.time())
                
                st.write(f"**Visit Summary: {summary_start} to {summary_end}**")
                
                if accessible_students:
                    summaries = []
                    
                    for student in accessible_students:
                        if student.id:
                            # Get basic summary
                            summary = get_attendance_summary_for_student(
                                student.id, start_datetime, end_datetime
                            )
                            
                            # Get attendance rate calculation
                            rate_calc = calculate_attendance_rate(
                                student.id, start_datetime, end_datetime, int(expected_daily_visits)
                            )
                            
                            # Combine the data
                            combined_summary = {
                                'student_name': f"{student.first_name} {student.last_name}",
                                'class': class_map.get(student.class_id).name if class_map.get(student.class_id) else f"Class {student.class_id}",
                                **summary,
                                **rate_calc
                            }
                            summaries.append(combined_summary)
                    
                    if summaries:
                        # Display summary table
                        col1, col2, col3, col4, col5, col6 = st.columns([3, 1, 1, 1, 1, 2])
                        with col1:
                            st.write("**Student**")
                        with col2:
                            st.write("**Total Visits**")
                        with col3:
                            st.write("**Days Attended**")
                        with col4:
                            st.write("**Avg/Day**")
                        with col5:
                            st.write("**Expected**")
                        with col6:
                            st.write("**Attendance Rate**")
                        
                        st.divider()
                        
                        total_visits = 0
                        total_days = 0
                        total_expected = 0
                        
                        for summary in summaries:
                            col1, col2, col3, col4, col5, col6 = st.columns([3, 1, 1, 1, 1, 2])
                            with col1:
                                st.write(f"{summary['student_name']} ({summary['class']})")
                            with col2:
                                visits = summary['total_visits']
                                st.write(visits)
                                total_visits += visits
                            with col3:
                                days = summary['days_attended']
                                st.write(days)
                                total_days += days
                            with col4:
                                avg = summary['average_visits_per_day']
                                st.write(f"{avg:.1f}")
                            with col5:
                                expected = summary['expected_visits']
                                st.write(expected)
                                total_expected += expected
                            with col6:
                                rate = summary['attendance_rate']
                                if rate >= 90:
                                    st.success(f"{rate}%")
                                elif rate >= 75:
                                    st.warning(f"{rate}%")
                                else:
                                    st.error(f"{rate}%")
                        
                        # Overall statistics
                        st.divider()
                        st.subheader("📈 Overall Statistics")
                        
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("Total Visits", total_visits)
                        with col2:
                            st.metric("Total Expected", total_expected)
                        with col3:
                            avg_rate = round((total_visits / total_expected) * 100, 1) if total_expected > 0 else 0
                            st.metric("Overall Rate", f"{avg_rate}%")
                        with col4:
                            avg_per_student = round(total_visits / len(summaries), 1) if summaries else 0
                            st.metric("Avg Visits/Student", avg_per_student)
                        
                        # Session type breakdown
                        st.subheader("📚 Session Type Breakdown")
                        regular_total = sum(s['regular_sessions'] for s in summaries)
                        extra_total = sum(s['extra_sessions'] for s in summaries)
                        tutorial_total = sum(s['tutorial_sessions'] for s in summaries)
                        other_total = sum(s['other_sessions'] for s in summaries)
                        
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("Regular Sessions", regular_total)
                        with col2:
                            st.metric("Extra Sessions", extra_total)
                        with col3:
                            st.metric("Tutorial Sessions", tutorial_total)
                        with col4:
                            st.metric("Other Sessions", other_total)
                        
                    else:
                        st.info("No visit records found for the selected period.")
                else:
                    st.warning("No students available for visit summary.")
            else:
                st.error("Start date must be before or equal to end date.")


def generate_individual_student_report(student_obj, term="Term 3", exam_type="End of Term"):
    """Generate detailed PDF report for a single student"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.5*inch, bottomMargin=0.5*inch)
    story = []
    
    # Styles
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'StudentTitle',
        parent=styles['Title'],
        fontSize=16,
        spaceAfter=15,
        alignment=1,
        textColor=colors.darkblue
    )
    
    header_style = ParagraphStyle(
        'SectionHeader',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=10,
        textColor=colors.darkgreen,
        backColor=colors.lightgrey
    )
    
    # Get student class information
    with get_session() as session:
        class_obj = session.get(Class, student_obj.class_id)
        class_name = class_obj.name if class_obj else "Unknown Class"
        
        # Student header
        title = Paragraph(f"Academic Report - {student_obj.first_name} {student_obj.last_name}", title_style)
        story.append(title)
        
        # Student information
        student_info = [
            f"Student Name: {student_obj.first_name} {student_obj.last_name}",
            f"Class: {class_name}",
            f"Academic Period: {term} - {exam_type}",
            f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        ]
        
        for info in student_info:
            story.append(Paragraph(info, styles['Normal']))
        
        story.append(Spacer(1, 20))
        
        # Get student marks for the specified term and exam type
        marks_query = select(Mark).where(
            Mark.student_id == student_obj.id,
            Mark.term == term,
            Mark.exam_type == exam_type
        )
        
        marks = session.exec(marks_query).all()
        
        if marks:
            # Subjects and marks table
            story.append(Paragraph("📚 Subject Marks & Grades", header_style))
            
            # Table headers
            table_data = [["Subject", "Code", "Score (%)", "Grade", "Description"]]
            
            total_score = 0
            total_subjects = 0
            
            for mark in marks:
                subject = session.get(Subject, mark.subject_id)
                if subject:
                    grade_desc = get_grade_description(mark.grade) if mark.grade else "Not calculated"
                    table_data.append([
                        subject.name,
                        subject.code,
                        f"{mark.score:.1f}%",
                        str(mark.grade) if mark.grade else "N/A",
                        grade_desc
                    ])
                    total_score += mark.score
                    total_subjects += 1
            
            # Add summary row
            average_score = total_score / total_subjects if total_subjects > 0 else 0
            table_data.append([
                "AVERAGE",
                "",
                f"{average_score:.1f}%",
                str(calculate_grade(average_score)),
                get_grade_description(calculate_grade(average_score))
            ])
            
            # Create and style the table
            table = Table(table_data, colWidths=[2*inch, 1*inch, 1*inch, 0.8*inch, 1.5*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -2), colors.beige),
                ('BACKGROUND', (0, -1), (-1, -1), colors.lightblue),
                ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(table)
            story.append(Spacer(1, 20))
            
            # Performance Analysis
            story.append(Paragraph("📊 Performance Analysis", header_style))
            
            # Calculate aggregate if possible
            aggregate = calculate_student_aggregate(student_obj.id, term, exam_type)
            if aggregate is not None:
                story.append(Paragraph(f"<b>Aggregate Score:</b> {aggregate:.1f}/600", styles['Normal']))
                percentage = (aggregate / 600) * 100
                story.append(Paragraph(f"<b>Aggregate Percentage:</b> {percentage:.1f}%", styles['Normal']))
            else:
                story.append(Paragraph("<b>Aggregate Score:</b> Cannot be calculated (insufficient marks)", styles['Normal']))
            
            story.append(Spacer(1, 10))
            
            # Performance level
            if average_score >= 80:
                performance_level = "Excellent"
                color = "green"
            elif average_score >= 70:
                performance_level = "Very Good"
                color = "blue"
            elif average_score >= 60:
                performance_level = "Good"
                color = "orange"
            elif average_score >= 50:
                performance_level = "Satisfactory"
                color = "brown"
            else:
                performance_level = "Needs Improvement"
                color = "red"
            
            story.append(Paragraph(f"<b>Overall Performance Level:</b> <font color='{color}'>{performance_level}</font>", styles['Normal']))
            
            # Subject breakdown by type
            core_subjects = []
            elective_subjects = []
            
            for mark in marks:
                subject = session.get(Subject, mark.subject_id)
                if subject:
                    if subject.subject_type == 'core':
                        core_subjects.append((subject.name, mark.score, mark.grade))
                    else:
                        elective_subjects.append((subject.name, mark.score, mark.grade))
            
            if core_subjects:
                story.append(Spacer(1, 15))
                story.append(Paragraph("🎯 Core Subjects Performance", header_style))
                core_avg = sum([score for _, score, _ in core_subjects]) / len(core_subjects)
                story.append(Paragraph(f"<b>Core Subjects Average:</b> {core_avg:.1f}%", styles['Normal']))
                
                for subject_name, score, grade in core_subjects:
                    story.append(Paragraph(f"• {subject_name}: {score:.1f}% (Grade {grade})", styles['Normal']))
            
            if elective_subjects:
                story.append(Spacer(1, 15))
                story.append(Paragraph("🎨 Elective Subjects Performance", header_style))
                elective_avg = sum([score for _, score, _ in elective_subjects]) / len(elective_subjects)
                story.append(Paragraph(f"<b>Elective Subjects Average:</b> {elective_avg:.1f}%", styles['Normal']))
                
                for subject_name, score, grade in elective_subjects:
                    story.append(Paragraph(f"• {subject_name}: {score:.1f}% (Grade {grade})", styles['Normal']))
        else:
            story.append(Paragraph("No marks found for this student in the specified term and exam type.", styles['Normal']))
    
    # Build PDF
    doc.build(story)
    buffer.seek(0)
    return buffer


def generate_individual_student_pdfs(selected_classes, term="Term 3", exam_type="End of Term"):
    """Generate separate PDF files for each student in the selected classes"""
    student_pdfs = {}
    
    with get_session() as session:
        for class_obj in selected_classes:
            # Get all students in this class
            students_in_class = session.exec(
                select(Student).where(Student.class_id == class_obj.id).order_by(Student.first_name, Student.last_name)
            ).all()
            
            for student in students_in_class:
                try:
                    # Generate individual student report
                    pdf_buffer = generate_individual_student_report(student, term, exam_type)
                    
                    # Create filename with student name
                    filename = f"{student.first_name}_{student.last_name}_{class_obj.name}_{term}_{exam_type}.pdf"
                    # Clean filename from special characters
                    filename = "".join(c for c in filename if c.isalnum() or c in "._- ").strip()
                    filename = filename.replace(" ", "_")
                    
                    student_pdfs[filename] = {
                        'buffer': pdf_buffer,
                        'student': student,
                        'class': class_obj,
                        'display_name': f"{student.first_name} {student.last_name} ({class_obj.name})"
                    }
                except Exception as e:
                    # Log error but continue with other students
                    print(f"Error generating PDF for {student.first_name} {student.last_name}: {str(e)}")
    
    return student_pdfs


def render_bulk_student_reports(students, class_map):
    """Render bulk individual student exam reports"""
    if not students:
        st.warning("No students found.")
        return
    
    st.subheader("📄 Bulk Student Exam Reports")
    st.write("Generate individual PDF exam reports for each student in selected classes.")
    
    # Get unique classes from students
    class_names = list(set([class_map.get(s.class_id).name for s in students if class_map.get(s.class_id)]))
    if not class_names:
        st.warning("No classes found for students.")
        return
    
    # Class selection
    selected_class_names = st.multiselect(
        "Select Classes",
        class_names,
        default=class_names[:1] if class_names else []
    )
    
    if not selected_class_names:
        st.info("Please select at least one class to generate reports.")
        return
    
    # Get class objects for selected classes
    with get_session() as session:
        selected_classes = []
        for class_name in selected_class_names:
            class_obj = session.exec(select(Class).where(Class.name == class_name)).first()
            if class_obj:
                selected_classes.append(class_obj)
    
    # Term and exam type selection
    col1, col2 = st.columns(2)
    with col1:
        report_term = st.selectbox("Select Term", ["Term 1", "Term 2", "Term 3"], index=2)
    with col2:
        report_exam_type = st.selectbox("Select Exam Type", ["Mid-term", "External", "End of Term"], index=2)
    
    # Preview students
    if selected_classes:
        total_students = 0
        for class_obj in selected_classes:
            students_count = len([s for s in students if s.class_id == class_obj.id])
            total_students += students_count
            st.write(f"📚 **{class_obj.name}**: {students_count} students")
        
        st.info(f"**Total students to generate reports for: {total_students}**")
    
    # Generate reports button
    if st.button("🎯 Generate Individual Student Reports", type="primary"):
        if not selected_classes:
            st.error("Please select at least one class.")
            return
        
        with st.spinner(f"Generating individual reports for {total_students} students..."):
            try:
                student_pdfs = generate_individual_student_pdfs(selected_classes, report_term, report_exam_type)
                
                if student_pdfs:
                    st.success(f"✅ Generated {len(student_pdfs)} individual student reports!")
                    
                    # Display download options for each student
                    st.subheader("📥 Download Individual Student Reports")
                    
                    # Create columns for better layout
                    num_columns = min(3, len(student_pdfs))
                    columns = st.columns(num_columns)
                    
                    for idx, (filename, pdf_data) in enumerate(student_pdfs.items()):
                        col_idx = idx % num_columns
                        with columns[col_idx]:
                            st.download_button(
                                label=f"📄 {pdf_data['display_name']}",
                                data=pdf_data['buffer'].getvalue(),
                                file_name=filename,
                                mime="application/pdf",
                                key=f"download_{idx}_{filename}",
                                help=f"Download exam report for {pdf_data['display_name']}"
                            )
                    
                    # Show summary
                    st.divider()
                    st.write("📊 **Generation Summary:**")
                    st.write(f"• Total PDFs generated: {len(student_pdfs)}")
                    st.write(f"• Term: {report_term}")
                    st.write(f"• Exam Type: {report_exam_type}")
                    st.write(f"• Classes: {', '.join(selected_class_names)}")
                
                else:
                    st.warning("No reports were generated. Please check if students have marks for the selected term and exam type.")
            
            except Exception as e:
                st.error(f"Error generating reports: {str(e)}")
                st.write("Please check your data and try again.")


# Main page
render_reports_page()
