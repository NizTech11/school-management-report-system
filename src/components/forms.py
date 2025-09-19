import streamlit as st
import pandas as pd
from services.db import get_session, Student, Subject, Mark, Class, User, TeacherClass, update_student_aggregate, update_all_student_aggregates, calculate_student_aggregate, calculate_student_aggregate_detailed, calculate_grade, get_grade_description, validate_score, validate_and_normalize_score
from utils.rbac import get_user_accessible_students, get_current_user, require_permission, has_permission
from sqlmodel import select, text
import io
import time
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from datetime import datetime


def generate_student_pdf(filtered_df):
    """Generate PDF report for students"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    story = []
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=20,
        alignment=1,  # Center alignment
    )
    
    # Add title
    title = Paragraph("Student List Report", title_style)
    story.append(title)
    story.append(Spacer(1, 20))
    
    # Add generation info
    generated_text = f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    generated_para = Paragraph(generated_text, styles['Normal'])
    story.append(generated_para)
    story.append(Spacer(1, 10))
    
    total_text = f"Total Students: {len(filtered_df)}"
    total_para = Paragraph(total_text, styles['Normal'])
    story.append(total_para)
    story.append(Spacer(1, 20))
    
    # Prepare table data
    table_data = [['Student Name', 'Class', 'Aggregate Score']]  # Header
    
    for _, row in filtered_df.iterrows():
        table_data.append([
            str(row['Full Name']),
            str(row['Class']),
            str(row['Aggregate'])
        ])
    
    # Create table
    table = Table(table_data, colWidths=[3*inch, 2.5*inch, 1.5*inch])
    
    # Style the table
    table.setStyle(TableStyle([
        # Header styling
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        
        # Data styling
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        
        # Alternating row colors
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.lightgrey, colors.white]),
    ]))
    
    story.append(table)
    
    # Build PDF
    doc.build(story)
    buffer.seek(0)
    return buffer


def generate_student_excel(filtered_df):
    """Generate Excel report for students"""
    buffer = io.BytesIO()
    
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        # Prepare data for Excel (clean version)
        excel_df = filtered_df[['Full Name', 'Class', 'Aggregate']].copy()
        excel_df.columns = ['Student Name', 'Class', 'Aggregate Score']
        
        # Write to Excel
        excel_df.to_excel(writer, sheet_name='Student List', index=False)
        
        # Get the workbook and worksheet
        workbook = writer.book
        worksheet = writer.sheets['Student List']
        
        # Add some formatting
        from openpyxl.styles import Font, PatternFill, Alignment
        
        # Header formatting
        header_font = Font(bold=True, color="FFFFFF")
        header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
        
        for cell in worksheet[1]:  # First row (headers)
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = Alignment(horizontal="center")
        
        # Adjust column widths
        worksheet.column_dimensions['A'].width = 25  # Student Name
        worksheet.column_dimensions['B'].width = 20  # Class
        worksheet.column_dimensions['C'].width = 15  # Aggregate Score
        
        # Add a summary sheet
        summary_df = pd.DataFrame({
            'Report Information': [
                'Generated on',
                'Total Students',
                'Report Type'
            ],
            'Value': [
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                len(filtered_df),
                'Student List Export'
            ]
        })
        
        summary_df.to_excel(writer, sheet_name='Summary', index=False)
        
        # Format summary sheet
        summary_ws = writer.sheets['Summary']
        for cell in summary_ws[1]:
            cell.font = header_font
            cell.fill = header_fill
        
        summary_ws.column_dimensions['A'].width = 20
        summary_ws.column_dimensions['B'].width = 25
    
    buffer.seek(0)
    return buffer


def generate_class_detailed_report(class_obj, students_in_class, term="Term 3", exam_type="End of Term"):
    """Generate detailed PDF report for a specific class with all student marks"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.5*inch, bottomMargin=0.5*inch)
    story = []
    
    # Styles
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'ClassTitle',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=15,
        alignment=1,  # Center alignment
        textColor=colors.darkblue
    )
    
    subtitle_style = ParagraphStyle(
        'ClassSubtitle',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=12,
        alignment=1,
        textColor=colors.darkgreen
    )
    
    section_style = ParagraphStyle(
        'SectionHeader',
        parent=styles['Heading3'],
        fontSize=12,
        spaceAfter=8,
        textColor=colors.darkred
    )
    
    # Class header
    title = Paragraph(f"Detailed Academic Report - {class_obj.name}", title_style)
    story.append(title)
    
    subtitle = Paragraph(f"Category: {class_obj.category} | {term} - {exam_type}", subtitle_style)
    story.append(subtitle)
    story.append(Spacer(1, 15))
    
    # Report metadata
    metadata = [
        f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"Total Students: {len(students_in_class)}",
        f"Academic Term: {term} - {exam_type}"
    ]
    
    for meta in metadata:
        para = Paragraph(meta, styles['Normal'])
        story.append(para)
    story.append(Spacer(1, 20))
    
    # Class summary statistics
    story.append(Paragraph("📊 Class Performance Summary", section_style))
    
    # Calculate class statistics
    aggregates = [s.aggregate for s in students_in_class if s.aggregate is not None]
    if aggregates:
        avg_aggregate = sum(aggregates) / len(aggregates)
        high_performers = len([a for a in aggregates if a >= 80])
        low_performers = len([a for a in aggregates if a < 40])
        
        stats_data = [
            ['Metric', 'Value'],
            ['Average Class Aggregate', f"{avg_aggregate:.1f}%"],
            ['High Performers (≥80%)', f"{high_performers} students"],
            ['Students Needing Support (<40%)', f"{low_performers} students"],
            ['Students with Aggregates', f"{len(aggregates)} of {len(students_in_class)}"]
        ]
        
        stats_table = Table(stats_data, colWidths=[3*inch, 2*inch])
        stats_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.lightgrey, colors.white]),
        ]))
        
        story.append(stats_table)
        story.append(Spacer(1, 20))
    
    # Individual student reports
    story.append(Paragraph("👥 Individual Student Performance", section_style))
    story.append(Spacer(1, 10))
    
    for idx, student in enumerate(students_in_class):
        # Student header
        student_title = f"{student.first_name} {student.last_name}"
        if student.aggregate:
            student_title += f" (Aggregate: {student.aggregate:.1f}%)"
        
        student_para = Paragraph(student_title, ParagraphStyle(
            'StudentName', parent=styles['Heading3'], fontSize=11, 
            textColor=colors.darkblue, spaceAfter=5
        ))
        
        # Get student's marks for the specified term and exam type
        with get_session() as s:
            student_marks = s.exec(
                select(Mark, Subject).join(Subject).where(
                    Mark.student_id == student.id,
                    Mark.term == term,
                    Mark.exam_type == exam_type
                ).order_by(Subject.name)
            ).all()
        
        if student_marks:
            # Create marks table
            marks_data = [['Subject', 'Score (%)', 'Grade', 'Description']]
            
            core_total = 0
            elective_scores = []
            
            for mark, subject in student_marks:
                grade_desc = get_grade_description(mark.grade) if mark.grade else "Not graded"
                marks_data.append([
                    f"{subject.name} ({subject.code})",
                    f"{mark.score:.1f}%",
                    str(mark.grade) if mark.grade else "N/A",
                    grade_desc
                ])
                
                # Track for aggregate calculation display
                if subject.subject_type == 'core':
                    core_total += mark.score
                else:
                    elective_scores.append(mark.score)
            
            # Add aggregate calculation if applicable
            if len([m for m, s in student_marks if s.subject_type == 'core']) >= 4 and len(elective_scores) >= 2:
                best_electives = sorted(elective_scores, reverse=True)[:2]
                calculated_aggregate = core_total + sum(best_electives)
                marks_data.append(['', '', '', ''])  # Separator
                marks_data.append(['CALCULATED AGGREGATE', f"{calculated_aggregate:.1f}/600", 
                                 f"{(calculated_aggregate/6):.1f}%", "Auto-calculated"])
            
            # Style and add marks table
            marks_table = Table(marks_data, colWidths=[2*inch, 1*inch, 0.8*inch, 1.7*inch])
            marks_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 9),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
                ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, colors.lightgrey]),
                ('BACKGROUND', (-1, -1), (-1, -1), colors.lightyellow),  # Highlight aggregate
            ]))
            
            # Keep student data together
            student_content = [student_para, Spacer(1, 5), marks_table]
            story.append(KeepTogether(student_content))
        else:
            # No marks found
            no_marks = Paragraph("No marks recorded for this term/exam type", styles['Normal'])
            student_content = [student_para, Spacer(1, 5), no_marks]
            story.append(KeepTogether(student_content))
        
        # Add spacing between students, page break for last few students if needed
        if idx < len(students_in_class) - 1:
            story.append(Spacer(1, 15))
            # Add page break every 3 students to avoid crowding
            if (idx + 1) % 3 == 0:
                story.append(PageBreak())
    
    # Build PDF
    doc.build(story)
    buffer.seek(0)
    return buffer


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


def generate_bulk_class_reports(selected_classes, term="Term 3", exam_type="End of Term"):
    """Generate combined PDF report for multiple classes"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.5*inch, bottomMargin=0.5*inch)
    story = []
    
    # Styles
    styles = getSampleStyleSheet()
    
    main_title_style = ParagraphStyle(
        'MainTitle',
        parent=styles['Title'],
        fontSize=18,
        spaceAfter=20,
        alignment=1,
        textColor=colors.darkblue
    )
    
    # Main report title
    title = Paragraph(f"Bulk Academic Reports - {term} ({exam_type})", main_title_style)
    story.append(title)
    
    # Summary information
    total_students = 0
    with get_session() as s:
        for class_obj in selected_classes:
            students_count = len(s.exec(select(Student).where(Student.class_id == class_obj.id)).all())
            total_students += students_count
    
    summary_info = [
        f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"Classes included: {len(selected_classes)}",
        f"Total students: {total_students}",
        f"Academic period: {term} - {exam_type}"
    ]
    
    for info in summary_info:
        para = Paragraph(info, styles['Normal'])
        story.append(para)
    
    story.append(Spacer(1, 20))
    story.append(PageBreak())
    
    # Generate report for each class
    for idx, class_obj in enumerate(selected_classes):
        with get_session() as s:
            students_in_class = s.exec(
                select(Student).where(Student.class_id == class_obj.id).order_by(Student.first_name, Student.last_name)
            ).all()
        
        if students_in_class:
            # Add class report content (reuse the single class function logic)
            class_buffer = generate_class_detailed_report(class_obj, students_in_class, term, exam_type)
            
            # Parse the existing buffer content and add to main story
            # For now, we'll create a simple class section
            class_title = Paragraph(f"Class: {class_obj.name} ({class_obj.category})", 
                                   ParagraphStyle('ClassTitle', parent=styles['Heading1'], 
                                                fontSize=16, spaceAfter=15, textColor=colors.darkgreen))
            story.append(class_title)
            
            # Add class summary
            summary_text = f"Students in class: {len(students_in_class)}"
            aggregates = [s.aggregate for s in students_in_class if s.aggregate is not None]
            if aggregates:
                avg_aggregate = sum(aggregates) / len(aggregates)
                summary_text += f" | Average Aggregate: {avg_aggregate:.1f}%"
            
            story.append(Paragraph(summary_text, styles['Normal']))
            story.append(Spacer(1, 10))
            
            # Simple student list for bulk report
            if students_in_class:
                student_data = [['Student Name', 'Aggregate Score', 'Performance Level']]
                
                for student in students_in_class:
                    if student.aggregate:
                        if student.aggregate >= 80:
                            performance = "Excellent"
                        elif student.aggregate >= 60:
                            performance = "Good"
                        elif student.aggregate >= 40:
                            performance = "Average"
                        else:
                            performance = "Needs Support"
                        
                        student_data.append([
                            f"{student.first_name} {student.last_name}",
                            f"{student.aggregate:.1f}%",
                            performance
                        ])
                    else:
                        student_data.append([
                            f"{student.first_name} {student.last_name}",
                            "Not calculated",
                            "Pending"
                        ])
                
                student_table = Table(student_data, colWidths=[2.5*inch, 1.5*inch, 1.5*inch])
                student_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.darkgreen),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 1), (-1, -1), 9),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.lightgrey, colors.white]),
                ]))
                
                story.append(student_table)
        
        # Add page break between classes (except for the last one)
        if idx < len(selected_classes) - 1:
            story.append(PageBreak())
    
    # Build PDF
    doc.build(story)
    buffer.seek(0)
    return buffer


def display_students():
    """Display students filtered by teacher's class assignments"""
    st.header("All Students")
    
    # Get current user information
    current_user = get_current_user()
    if not current_user:
        st.error("Please log in to view students")
        return
    
    with get_session() as session:
        # Get accessible student IDs based on user role and class assignments
        accessible_student_ids = get_user_accessible_students(current_user['id'], current_user['role'])
        
        # Get students based on access permissions
        if not accessible_student_ids:  # Empty list means access to all (Admin/Head)
            students = session.exec(select(Student).order_by(Student.last_name, Student.first_name)).all()
        elif accessible_student_ids == [-1]:  # No access to any students - not assigned to classes
            st.warning("⚠️ You are not assigned to any classes. Please contact an administrator to assign you to classes.")
            return
        elif accessible_student_ids == [-2]:  # Teacher has classes but no students in those classes
            st.info("📚 You are assigned to classes, but there are currently no students in your assigned classes.")
            
            # Show which classes the teacher is assigned to
            from utils.rbac import get_teacher_classes
            teacher_classes = get_teacher_classes(current_user['id'])
            if teacher_classes:
                classes = session.exec(select(Class)).all()
                class_map = {cls.id: cls for cls in classes}
                assigned_class_names = []
                for class_id in teacher_classes:
                    class_obj = class_map.get(class_id)
                    if class_obj:
                        assigned_class_names.append(f"{class_obj.name} ({class_obj.category})")
                if assigned_class_names:
                    st.write(f"**Your assigned classes:** {', '.join(assigned_class_names)}")
            return
        else:  # Limited access to specific students
            # Filter students by accessible IDs
            all_students = session.exec(select(Student)).all()
            students = [s for s in all_students if s.id in accessible_student_ids]
            students.sort(key=lambda x: (x.last_name, x.first_name))
        
        # Get all classes for mapping
        classes = session.exec(select(Class)).all()
        
        # Create a mapping of class_id to class info
        class_map = {cls.id: cls for cls in classes}
    
    # Initialize class_counts early to avoid UnboundLocalError
    class_counts = {}
    for student in students:
        class_info = class_map.get(student.class_id)
        class_name = class_info.name if class_info else "No Class"
        class_counts[class_name] = class_counts.get(class_name, 0) + 1
    
    if not students:
        if current_user['role'] == 'Teacher':
            st.info("No students found in your assigned classes.")
        else:
            st.info("No students have been added yet.")
        return
    
        # Display role-based information
        if current_user['role'] == 'Teacher':
            from utils.rbac import get_teacher_classes
            teacher_classes = get_teacher_classes(current_user['id'])
            if teacher_classes:
                assigned_class_names = [class_map.get(class_id).name for class_id in teacher_classes 
                                      if class_map.get(class_id) is not None]
                st.info(f"📚 Showing students from your assigned classes: {', '.join(assigned_class_names)}")
        else:
            st.info(f"👁️ Showing all students (Role: {current_user['role']})")    # Prepare data for the table
    student_data = []
    for student in students:
        class_info = class_map.get(student.class_id)
        class_name = f"{class_info.name} ({class_info.category})" if class_info else "No Class Assigned"
        
        # Format aggregate score
        aggregate_display = f"{student.aggregate:.1f}%" if student.aggregate is not None else "Not recorded"
        
        student_data.append({
            "ID": student.id,
            "First Name": student.first_name,
            "Last Name": student.last_name,
            "Full Name": f"{student.first_name} {student.last_name}",
            "Class": class_name,
            "Aggregate": aggregate_display,
            "Aggregate_Raw": student.aggregate  # For sorting/filtering
        })
    
    # Convert to DataFrame for better display
    df = pd.DataFrame(student_data)
    
    # Display summary statistics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Students", len(students))
    
    with col2:
        students_with_aggregate = len([s for s in students if s.aggregate is not None])
        st.metric("Students with Aggregate", students_with_aggregate)
    
    with col3:
        # Calculate average aggregate
        aggregates = [s.aggregate for s in students if s.aggregate is not None]
        avg_aggregate = sum(aggregates) / len(aggregates) if aggregates else 0
        st.metric("Average Aggregate", f"{avg_aggregate:.1f}%")
    
    with col4:
        # Count students by performance level
        high_performers = len([s for s in students if s.aggregate and s.aggregate >= 80])
        st.metric("High Performers (≥80%)", high_performers)
    
    st.divider()
    
    # Search and filter functionality
    col1, col2 = st.columns([2, 1])
    
    with col1:
        search_term = st.text_input("🔍 Search students (by name or aggregate score)", 
                                  placeholder="Type to search...")
    
    with col2:
        # Filter by class
        class_filter_options = ["All Classes"] + [f"{cls.name} ({cls.category})" for cls in classes]
        selected_class_filter = st.selectbox("Filter by Class", class_filter_options)
    
    # Apply filters
    filtered_df = df.copy()
    
    if search_term:
        mask = (
            filtered_df["First Name"].str.contains(search_term, case=False, na=False) |
            filtered_df["Last Name"].str.contains(search_term, case=False, na=False) |
            filtered_df["Full Name"].str.contains(search_term, case=False, na=False) |
            filtered_df["Aggregate"].str.contains(search_term, case=False, na=False)
        )
        filtered_df = filtered_df[mask]
    
    if selected_class_filter != "All Classes":
        filtered_df = filtered_df[filtered_df["Class"] == selected_class_filter]
    
    # Display the filtered table
    if len(filtered_df) == 0:
        st.warning("No students match your search criteria.")
    else:
        st.write(f"**Showing {len(filtered_df)} of {len(students)} students**")
        
        # Enhanced student table with action buttons
        st.subheader("📋 Student List")
        
        # Table header
        header_col1, header_col2, header_col3, header_col4, header_col5, header_col6 = st.columns([1, 3, 2, 2, 1, 1])
        with header_col1:
            st.write("**🆔 ID**")
        with header_col2:
            st.write("**👤 Student Name**")
        with header_col3:
            st.write("**🏫 Class**")
        with header_col4:
            st.write("**📊 Aggregate**")
        with header_col5:
            st.write("**✏️ Edit**")
        with header_col6:
            st.write("**🗑️ Delete**")
        
        st.divider()
        
        # Create interactive table with action buttons
        for idx, (_, student_row) in enumerate(filtered_df.iterrows()):
            # Get the actual student object for actions
            student_obj = next(s for s in students if s.id == student_row["ID"])
            
            # Create container for each student row
            with st.container():
                # Create columns for student info and actions
                col1, col2, col3, col4, col5, col6 = st.columns([1, 3, 2, 2, 1, 1])
                
                with col1:
                    st.write(f"**#{student_row['ID']}**")
                with col2:
                    st.write(f"**{student_row['Full Name']}**")
                with col3:
                    st.write(student_row['Class'])
                with col4:
                    st.write(student_row['Aggregate'])
                with col5:
                    # Edit button - check both permission and class assignment for teachers
                    from utils.rbac import has_permission, get_teacher_classes
                    current_user = get_current_user()
                    can_edit = False
                    edit_reason = ""
                    
                    if current_user and has_permission(current_user['role'], 'students.edit'):
                        if current_user['role'] in ['Admin', 'Head']:
                            # Admin and Head can edit any student
                            can_edit = True
                        elif current_user['role'] == 'Teacher':
                            # Teachers can only edit students in their assigned classes
                            teacher_classes = get_teacher_classes(current_user['id'])
                            if student_obj.class_id in teacher_classes:
                                can_edit = True
                            else:
                                edit_reason = "Student not in your assigned classes"
                        else:
                            edit_reason = "Role not authorized"
                    else:
                        edit_reason = "No edit permission"
                    
                    if can_edit:
                        edit_key = f"edit_{student_obj.id}_{idx}"
                        if st.button("✏️ Edit", key=edit_key, help=f"Edit {student_row['Full Name']}", use_container_width=True):
                            st.session_state[f"editing_student_{student_obj.id}"] = True
                            st.rerun()
                    else:
                        st.markdown("*Cannot edit*", help=edit_reason)
                with col6:
                    # Delete button - check both permission and class assignment for teachers
                    can_delete = False
                    delete_reason = ""
                    
                    if current_user and has_permission(current_user['role'], 'students.delete'):
                        if current_user['role'] in ['Admin', 'Head']:
                            # Admin and Head can delete any student
                            can_delete = True
                        elif current_user['role'] == 'Teacher':
                            # Teachers can only delete students in their assigned classes
                            teacher_classes = get_teacher_classes(current_user['id'])
                            if student_obj.class_id in teacher_classes:
                                can_delete = True
                            else:
                                delete_reason = "Student not in your assigned classes"
                        else:
                            delete_reason = "Role not authorized"
                    else:
                        delete_reason = "No delete permission"
                    
                    if can_delete:
                        delete_key = f"delete_{student_obj.id}_{idx}"
                        if st.button("🗑️", key=delete_key, help=f"Delete {student_row['Full Name']}", type="secondary", use_container_width=True):
                            st.session_state[f"confirm_delete_{student_obj.id}"] = True
                            st.rerun()
                    else:
                        st.markdown("*Cannot delete*", help=delete_reason)
            
            # Edit form (appears when edit button is clicked)
            if st.session_state.get(f"editing_student_{student_obj.id}", False):
                with st.expander(f"✏️ Editing {student_row['Full Name']}", expanded=True):
                    with st.form(f"edit_form_{student_obj.id}"):
                        edit_col1, edit_col2 = st.columns(2)
                        
                        with edit_col1:
                            new_first_name = st.text_input("First Name", value=student_obj.first_name)
                            
                        with edit_col2:
                            new_last_name = st.text_input("Last Name", value=student_obj.last_name)
                        
                        # Class selection - restricted to teacher's assigned classes if applicable
                        with get_session() as session:
                            if current_user['role'] in ['Admin', 'Head']:
                                # Admin and Head can move students to any class
                                all_classes = session.exec(select(Class)).all()
                            elif current_user['role'] == 'Teacher':
                                # Teachers can only move students between their assigned classes
                                teacher_classes = get_teacher_classes(current_user['id'])
                                if teacher_classes:
                                    all_classes = []
                                    classes_from_db = session.exec(select(Class)).all()
                                    all_classes = [cls for cls in classes_from_db if cls.id in teacher_classes]
                                    all_classes.sort(key=lambda x: (x.category, x.name))
                                else:
                                    all_classes = []
                            else:
                                all_classes = session.exec(select(Class)).all()
                        
                        if not all_classes:
                            st.error("No classes available for this student.")
                            return
                        
                        # Show information for teachers about class restrictions
                        if current_user['role'] == 'Teacher':
                            available_class_names = [f"{cls.name} ({cls.category})" for cls in all_classes]
                            st.info(f"📚 Available classes: {', '.join(available_class_names)}")
                        
                        current_class_index = 0
                        for i, cls in enumerate(all_classes):
                            if cls.id == student_obj.class_id:
                                current_class_index = i
                                break
                        
                        new_class = st.selectbox(
                            "Class",
                            options=all_classes,
                            index=current_class_index,
                            format_func=lambda x: f"{x.name} ({x.category})"
                        )
                        
                        new_aggregate = st.number_input(
                            "Aggregate Score (%)", 
                            value=float(student_obj.aggregate) if student_obj.aggregate else 0.0,
                            min_value=0.0, 
                            max_value=100.0,
                            step=0.1
                        )
                        
                        form_col1, form_col2, form_col3 = st.columns(3)
                        
                        with form_col1:
                            if st.form_submit_button("💾 Save Changes", type="primary"):
                                try:
                                    with get_session() as session:
                                        student_to_update = session.get(Student, student_obj.id)
                                        if student_to_update:
                                            student_to_update.first_name = new_first_name
                                            student_to_update.last_name = new_last_name
                                            student_to_update.class_id = new_class.id
                                            student_to_update.aggregate = new_aggregate
                                            session.add(student_to_update)
                                            session.commit()
                                            st.success(f"✅ Updated {new_first_name} {new_last_name}")
                                            del st.session_state[f"editing_student_{student_obj.id}"]
                                            time.sleep(1)
                                            st.rerun()
                                        else:
                                            st.error("Student not found")
                                except Exception as e:
                                    st.error(f"Error updating student: {str(e)}")
                        
                        with form_col2:
                            if st.form_submit_button("❌ Cancel"):
                                del st.session_state[f"editing_student_{student_obj.id}"]
                                st.rerun()
            
            # Delete confirmation (appears when delete button is clicked)
            if st.session_state.get(f"confirm_delete_{student_obj.id}", False):
                with st.container():
                    st.error(f"⚠️ **Confirm deletion of {student_row['Full Name']}**")
                    
                    # Show associated marks count
                    with get_session() as session:
                        marks_count = len(session.exec(
                            select(Mark).where(Mark.student_id == student_obj.id)
                        ).all())
                    
                    if marks_count > 0:
                        st.warning(f"This student has **{marks_count} associated marks** that will also be deleted!")
                    
                    confirm_col1, confirm_col2, confirm_col3 = st.columns(3)
                    
                    with confirm_col1:
                        confirm_key = f"confirm_final_{student_obj.id}"
                        if st.button(f"🗑️ Yes, Delete {student_obj.first_name}", key=confirm_key, type="primary"):
                            try:
                                with get_session() as session:
                                    # Delete associated marks first
                                    marks_to_delete = session.exec(
                                        select(Mark).where(Mark.student_id == student_obj.id)
                                    ).all()
                                    
                                    for mark in marks_to_delete:
                                        session.delete(mark)
                                    
                                    # Delete the student
                                    student_to_delete = session.get(Student, student_obj.id)
                                    if student_to_delete:
                                        session.delete(student_to_delete)
                                        session.commit()
                                        st.success(f"✅ Deleted {student_obj.first_name} {student_obj.last_name} and {len(marks_to_delete)} marks")
                                        del st.session_state[f"confirm_delete_{student_obj.id}"]
                                        time.sleep(1)
                                        st.rerun()
                                    else:
                                        st.error("Student not found")
                            except Exception as e:
                                st.error(f"Error deleting student: {str(e)}")
                                session.rollback()
                    
                    with confirm_col2:
                        cancel_key = f"cancel_delete_{student_obj.id}"
                        if st.button("❌ Cancel", key=cancel_key, type="secondary"):
                            del st.session_state[f"confirm_delete_{student_obj.id}"]
                            st.rerun()
            
            # Add divider between students (except for the last one)
            if idx < len(filtered_df) - 1:
                st.divider()
        
        # Student actions section
        st.divider()
        st.subheader("🔧 Bulk Actions")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Quick stats by class
            if class_counts:
                st.write("**Students per Class:**")
                for class_name, count in sorted(class_counts.items()):
                    st.write(f"• **{class_name}**: {count} student(s)")
        
        with col2:
            # Export functionality
            st.write("**Export Options:**")
            
            # Create CSV content
            csv_content = filtered_df.to_csv(index=False)
            
            # Create three columns for export buttons
            exp_col1, exp_col2, exp_col3 = st.columns(3)
            
            with exp_col1:
                st.download_button(
                    label="📄 CSV",
                    data=csv_content,
                    file_name="student_list.csv",
                    mime="text/csv",
                    use_container_width=True,
                    help="Download as CSV file"
                )
            
            with exp_col2:
                # Generate PDF content
                try:
                    pdf_buffer = generate_student_pdf(filtered_df)
                    st.download_button(
                        label="📕 PDF",
                        data=pdf_buffer,
                        file_name=f"student_list_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                        mime="application/pdf",
                        use_container_width=True,
                        help="Download as PDF report"
                    )
                except Exception as e:
                    st.error(f"PDF Error: {str(e)[:50]}...")
            
            with exp_col3:
                # Generate Excel content
                try:
                    excel_buffer = generate_student_excel(filtered_df)
                    st.download_button(
                        label="📊 Excel",
                        data=excel_buffer,
                        file_name=f"student_list_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True,
                        help="Download as Excel spreadsheet"
                    )
                except Exception as e:
                    st.error(f"Excel Error: {str(e)[:50]}...")

        # Bulk Delete All Students Section
        st.divider()
        st.subheader("⚠️ Danger Zone - Bulk Operations")
        
        with st.expander("🗑️ Delete All Students", expanded=False):
            st.error("⚠️ **EXTREME CAUTION**: This action will permanently delete ALL students and ALL associated marks!")
            
            # Show impact statistics
            total_marks = 0
            with get_session() as session:
                all_marks = session.exec(select(Mark)).all()
                total_marks = len(all_marks)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("📚 Total Students", len(students), help="All students will be deleted")
            with col2:
                st.metric("📝 Total Marks", total_marks, help="All marks will be deleted")
            with col3:
                st.metric("🏫 Classes Affected", len(class_counts), help="All classes will be emptied")
            
            st.warning("**What will be deleted:**")
            st.write(f"• **{len(students)} students** from all classes")
            st.write(f"• **{total_marks} marks** from all terms and exam types")
            st.write("• All student performance data")
            st.write("• All academic records")
            
            # Multi-step confirmation process
            if len(students) > 0:
                st.write("---")
                st.write("**Confirmation Steps:**")
                
                # Step 1: Understanding checkbox
                step1 = st.checkbox(
                    "☑️ I understand this will delete ALL students and their academic records permanently",
                    key="bulk_delete_step1"
                )
                
                # Step 2: Backup confirmation
                step2 = False
                if step1:
                    step2 = st.checkbox(
                        "☑️ I have backed up all important data (exported reports, etc.)",
                        key="bulk_delete_step2"
                    )
                
                # Step 3: Type confirmation
                step3 = False
                if step2:
                    confirmation_text = st.text_input(
                        "☑️ Type 'DELETE ALL STUDENTS' to confirm:",
                        key="bulk_delete_confirmation_text",
                        placeholder="Type exactly: DELETE ALL STUDENTS"
                    )
                    step3 = confirmation_text == "DELETE ALL STUDENTS"
                
                # Final deletion button
                if step1 and step2 and step3:
                    st.write("---")
                    col1, col2, col3 = st.columns([1, 2, 1])
                    with col2:
                        if st.button(
                            "🗑️ DELETE ALL STUDENTS PERMANENTLY",
                            type="primary",
                            key="final_bulk_delete_button",
                            use_container_width=True
                        ):
                            try:
                                with get_session() as session:
                                    # Get counts for confirmation message
                                    students_to_delete = session.exec(select(Student)).all()
                                    marks_to_delete = session.exec(select(Mark)).all()
                                    
                                    students_count = len(students_to_delete)
                                    marks_count = len(marks_to_delete)
                                    
                                    # Delete all marks first
                                    for mark in marks_to_delete:
                                        session.delete(mark)
                                    
                                    # Then delete all students
                                    for student in students_to_delete:
                                        session.delete(student)
                                    
                                    # Commit all changes
                                    session.commit()
                                    
                                    # Clear session state
                                    for key in list(st.session_state.keys()):
                                        if isinstance(key, str) and key.startswith(('bulk_delete_', 'editing_student_', 'confirm_delete_')):
                                            del st.session_state[key]
                                    
                                    # Show success message
                                    st.success(f"✅ Successfully deleted {students_count} students and {marks_count} marks!")
                                    st.balloons()
                                    time.sleep(2)
                                    st.rerun()
                                    
                            except Exception as e:
                                st.error(f"❌ Error during bulk deletion: {str(e)}")
                                session.rollback()
                                
            else:
                st.info("ℹ️ No students to delete.")
    
    # Bulk Class Reports Section
    st.divider()
    st.subheader("📚 Bulk Class Reports")
    st.info("Generate comprehensive PDF reports for entire classes with detailed student marks and performance analysis.")
    
    # Get all available classes
    with get_session() as session:
        all_classes = session.exec(select(Class).order_by(Class.category, Class.name)).all()
    
    if all_classes:
        # Class selection interface
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.write("**Select Classes for Bulk Reports:**")
            
            # Group classes by category for better organization
            classes_by_category = {}
            for cls in all_classes:
                if cls.category not in classes_by_category:
                    classes_by_category[cls.category] = []
                classes_by_category[cls.category].append(cls)
            
            selected_classes = []
            
            # Category-based selection with checkboxes
            for category, category_classes in classes_by_category.items():
                st.write(f"**{category}:**")
                
                # Select all classes in category option
                select_all_key = f"select_all_{category.replace(' ', '_')}"
                select_all = st.checkbox(f"Select All {category} Classes", key=select_all_key)
                
                for cls in category_classes:
                    class_key = f"class_{cls.id}"
                    # Auto-select if "Select All" is checked
                    default_value = select_all
                    if st.checkbox(
                        f"  • {cls.name} ({len([s for s in students if s.class_id == cls.id])} students)", 
                        key=class_key,
                        value=default_value
                    ):
                        selected_classes.append(cls)
                
                st.write("")  # Spacing between categories
        
        with col2:
            st.write("**Report Configuration:**")
            
            # Term and exam type selection for reports
            report_term = st.selectbox(
                "Term for Reports", 
                ["Term 1", "Term 2", "Term 3"], 
                index=2,
                key="bulk_report_term",
                help="Select which term's marks to include in the reports"
            )
            
            report_exam_type = st.selectbox(
                "Exam Type", 
                ["Mid-term", "External", "End of Term"], 
                index=2,
                key="bulk_report_exam_type",
                help="Select which exam type to focus on"
            )
            
            # Report type selection
            report_type = st.radio(
                "Report Type:",
                ["Individual Class Reports", "Combined Report", "Both Class & Combined"],
                key="bulk_report_type",
                help="Choose the type of reports to generate. For individual student exam reports, use the Reports section."
            )
        
        # Display selection summary and generate reports
        if selected_classes:
            st.write("---")
            st.write(f"**Selected Classes ({len(selected_classes)}):**")
            
            total_students_selected = 0
            for cls in selected_classes:
                students_in_class = len([s for s in students if s.class_id == cls.id])
                total_students_selected += students_in_class
                st.write(f"• **{cls.name}** ({cls.category}): {students_in_class} students")
            
            st.write(f"**Total Students in Reports: {total_students_selected}**")
            
            # Report generation buttons
            st.write("---")
            report_col1, report_col2, report_col3 = st.columns(3)
            
            with report_col1:
                if report_type in ["Individual Class Reports", "Both Class & Combined"]:
                    if st.button(
                        "📄 Class Reports", 
                        key="generate_individual",
                        help="Generate separate PDF report for each selected class",
                        use_container_width=True
                    ):
                        st.session_state["generate_individual_reports"] = True
                        st.rerun()
            
            with report_col2:
                if report_type in ["Combined Report", "Both Class & Combined"]:
                    if st.button(
                        "📋 Combined Report", 
                        key="generate_combined",
                        help="Generate one PDF containing all selected classes",
                        use_container_width=True
                    ):
                        try:
                            with st.spinner("Generating combined report..."):
                                bulk_pdf = generate_bulk_class_reports(selected_classes, report_term, report_exam_type)
                                
                                # Create filename with timestamp and class info
                                class_names = "_".join([cls.name.replace(" ", "") for cls in selected_classes[:3]])
                                if len(selected_classes) > 3:
                                    class_names += f"_and_{len(selected_classes)-3}_more"
                                
                                filename = f"Combined_Report_{class_names}_{report_term}_{report_exam_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                                
                                st.download_button(
                                    label="⬇️ Download Combined Report",
                                    data=bulk_pdf,
                                    file_name=filename,
                                    mime="application/pdf",
                                    use_container_width=True,
                                    key="download_combined"
                                )
                                st.success(f"✅ Combined report generated for {len(selected_classes)} classes!")
                        except Exception as e:
                            st.error(f"❌ Error generating combined report: {str(e)}")
            
            with report_col3:
                st.info("📋 For individual student exam reports, please use the **Reports** section.")
                if st.button(
                    "🔄 Clear Selection", 
                    key="clear_selection",
                    help="Clear all class selections",
                    use_container_width=True
                ):
                    # Clear all class selection states
                    for category in classes_by_category.keys():
                        select_all_key = f"select_all_{category.replace(' ', '_')}"
                        if select_all_key in st.session_state:
                            del st.session_state[select_all_key]
                    
                    for cls in all_classes:
                        class_key = f"class_{cls.id}"
                        if class_key in st.session_state:
                            del st.session_state[class_key]
                    
                    st.rerun()
            
            # Handle individual report generation
            if st.session_state.get("generate_individual_reports", False):
                st.write("---")
                st.write("**📄 Individual Class Reports:**")
                
                # Generate and provide download for each class
                for idx, cls in enumerate(selected_classes):
                    students_in_class = [s for s in students if s.class_id == cls.id]
                    
                    if students_in_class:
                        try:
                            with st.spinner(f"Generating report for {cls.name}..."):
                                class_pdf = generate_class_detailed_report(cls, students_in_class, report_term, report_exam_type)
                                
                                filename = f"Class_Report_{cls.name.replace(' ', '_')}_{report_term}_{report_exam_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                                
                                col_a, col_b, col_c = st.columns([2, 1, 1])
                                with col_a:
                                    st.write(f"**{cls.name}** ({cls.category})")
                                    st.caption(f"{len(students_in_class)} students • {report_term} • {report_exam_type}")
                                
                                with col_b:
                                    st.download_button(
                                        label="⬇️ Download",
                                        data=class_pdf,
                                        file_name=filename,
                                        mime="application/pdf",
                                        key=f"download_class_{cls.id}",
                                        use_container_width=True
                                    )
                                
                                with col_c:
                                    st.success("✅ Ready")
                                
                        except Exception as e:
                            st.error(f"❌ Error generating report for {cls.name}: {str(e)}")
                    else:
                        st.warning(f"⚠️ No students found in {cls.name}")
                
                # Clear the generation flag
                st.session_state["generate_individual_reports"] = False
        else:
            st.info("👆 Select one or more classes above to generate reports")
    else:
        st.warning("No classes found. Please add classes first.")
    
    # Enhanced Student Management Section
    st.divider()
    st.subheader("🗂️ Student Management")
    
    # Create tabs for different management actions
    mgmt_tab1, mgmt_tab2 = st.tabs(["🗑️ Delete Student", "📝 Edit Student"])
    
    with mgmt_tab1:
        st.warning("⚠️ **Danger Zone**: Student deletion is permanent and will remove all associated marks!")
        
        if len(students) == 0:
            st.info("No students to delete.")
        else:
            # Create a more detailed student selection
            student_options = {}
            for student in students:
                class_info = class_map.get(student.class_id)
                class_name = class_info.name if class_info else "No Class"
                display_name = f"{student.first_name} {student.last_name} - {class_name} (ID: {student.id})"
                student_options[display_name] = student
            
            selected_student_display = st.selectbox(
                "Select Student to Delete",
                options=[""] + list(student_options.keys()),
                key="delete_student_select",
                help="Select a student to delete permanently"
            )
            
            if selected_student_display:
                selected_student = student_options[selected_student_display]
                
                # Show student details and associated data
                with st.container():
                    st.write("**Student Details:**")
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.write(f"**Name:** {selected_student.first_name} {selected_student.last_name}")
                    with col2:
                        class_info = class_map.get(selected_student.class_id)
                        st.write(f"**Class:** {class_info.name if class_info else 'No Class'}")
                    with col3:
                        aggregate_text = f"{selected_student.aggregate:.1f}%" if selected_student.aggregate else "Not recorded"
                        st.write(f"**Aggregate:** {aggregate_text}")
                
                # Check for associated marks
                with get_session() as session:
                    marks_count = session.exec(
                        select(Mark).where(Mark.student_id == selected_student.id)
                    ).all()
                    
                if marks_count:
                    st.warning(f"⚠️ This student has **{len(marks_count)} associated marks** that will also be deleted!")
                    
                    # Show marks breakdown
                    marks_by_term = {}
                    marks_by_exam_type = {}
                    for mark in marks_count:
                        # Count by term
                        marks_by_term[mark.term] = marks_by_term.get(mark.term, 0) + 1
                        # Count by exam type
                        marks_by_exam_type[mark.exam_type] = marks_by_exam_type.get(mark.exam_type, 0) + 1
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write("**Marks by Term:**")
                        for term, count in marks_by_term.items():
                            st.write(f"• {term}: {count} marks")
                    with col2:
                        st.write("**Marks by Exam Type:**")
                        for exam_type, count in marks_by_exam_type.items():
                            st.write(f"• {exam_type}: {count} marks")
                
                # Confirmation checkbox
                confirm_deletion = st.checkbox(
                    f"I understand that deleting {selected_student.first_name} {selected_student.last_name} will permanently remove the student and all associated marks",
                    key="confirm_student_deletion"
                )
                
                if confirm_deletion:
                    if st.button(
                        f"🗑️ Permanently Delete {selected_student.first_name} {selected_student.last_name}",
                        type="primary",
                        key="final_delete_button"
                    ):
                        try:
                            with get_session() as session:
                                # First, delete all associated marks
                                marks_to_delete = session.exec(
                                    select(Mark).where(Mark.student_id == selected_student.id)
                                ).all()
                                
                                for mark in marks_to_delete:
                                    session.delete(mark)
                                
                                # Then delete the student
                                student_to_delete = session.get(Student, selected_student.id)
                                if student_to_delete:
                                    session.delete(student_to_delete)
                                    session.commit()
                                    
                                    st.success(f"✅ Successfully deleted {selected_student.first_name} {selected_student.last_name} and {len(marks_to_delete)} associated marks.")
                                    st.balloons()
                                    time.sleep(2)
                                    st.rerun()
                                else:
                                    st.error("❌ Student not found.")
                                    
                        except Exception as e:
                            st.error(f"❌ Error deleting student: {str(e)}")
                            session.rollback()
    
    with mgmt_tab2:
        st.info("📝 Student editing functionality can be implemented here in the future.")
        st.write("Features to consider:")
        st.write("• Update student name")
        st.write("• Change student class")
        st.write("• Update aggregate scores")
        st.write("• Transfer student to different class")


@require_permission("students.create")
def student_form():
    st.header("Add / Edit Student")
    
    # Get current user information for role-based filtering
    current_user = get_current_user()
    if not current_user:
        st.error("Please log in to add students")
        return
    
    # Get available classes based on user role
    with get_session() as session:
        if current_user['role'] in ['Admin', 'Head']:
            # Admin and Head can add students to any class
            classes = session.exec(select(Class).order_by(Class.category, Class.name)).all()
        elif current_user['role'] == 'Teacher':
            # Teachers can only add students to their assigned classes
            from utils.rbac import get_teacher_classes
            teacher_class_ids = get_teacher_classes(current_user['id'])
            
            if not teacher_class_ids:
                st.warning("⚠️ You are not assigned to any classes. Please contact an administrator to assign you to classes before adding students.")
                return
            
            # Get only the classes assigned to this teacher
            classes = []
            if teacher_class_ids:
                all_classes = session.exec(select(Class)).all()
                classes = [cls for cls in all_classes if cls.id in teacher_class_ids]
                classes.sort(key=lambda x: (x.category, x.name))
        else:
            classes = []
    
    if not classes:
        if current_user['role'] == 'Teacher':
            st.warning("No classes assigned to you. Please contact an administrator.")
        else:
            st.warning("No classes available. Please add classes first in the Classes page.")
        return
    
    # Show information about accessible classes for teachers
    if current_user['role'] == 'Teacher':
        class_names = [f"{cls.name} ({cls.category})" for cls in classes]
        st.info(f"📚 You can add students to your assigned classes: {', '.join(class_names)}")
    
    # Create tabs for different student management actions
    tab1, tab2, tab3 = st.tabs(["➕ Add Single Student", "📊 Bulk Upload Students", "📋 Download Template"])
    
    with tab1:
        st.subheader("Add Individual Student")
        
        with st.form("student_form"):
            first = st.text_input("First name")
            last = st.text_input("Last name")
            
            # Class selection with category grouping
            class_options = {}
            for cls in classes:
                category = cls.category
                if category not in class_options:
                    class_options[category] = []
                class_options[category].append(cls)
            
            # Create a flat list for selectbox with category labels
            class_choices = []
            class_map = {}
            for category, cls_list in class_options.items():
                for cls in cls_list:
                    display_name = f"{cls.name} ({category})"
                    class_choices.append(display_name)
                    class_map[display_name] = cls
            
            selected_class_display = st.selectbox("Class", class_choices)
            selected_class = class_map[selected_class_display]
            
            # Aggregate field with validation
            aggregate = st.number_input(
                "Aggregate Score (%)", 
                min_value=0.0, 
                max_value=100.0, 
                value=None,
                step=0.1,
                help="Enter the student's exam aggregate score as a percentage (0-100)"
            )
            
            submitted = st.form_submit_button("Save")
        
        if submitted and first and last:
            with get_session() as session:
                student = Student(
                    first_name=first, 
                    last_name=last, 
                    class_id=selected_class.id,
                    aggregate=aggregate
                )
                session.add(student)
                session.commit()
                st.success(f"Student {first} {last} saved to {selected_class.name}")
                st.rerun()
        elif submitted:
            st.error("Please fill in both first name and last name")
    
    with tab2:
        st.subheader("📊 Bulk Upload Students")
        st.info("Upload multiple students at once using CSV or Excel files. Download the template first to see the required format.")
        
        # File uploader
        uploaded_file = st.file_uploader(
            "Choose a CSV or Excel file",
            type=['csv', 'xlsx', 'xls'],
            help="Upload a CSV or Excel file with student data. Make sure to use the template format."
        )
        
        if uploaded_file is not None:
            try:
                # Read the uploaded file
                if uploaded_file.name.endswith('.csv'):
                    df = pd.read_csv(uploaded_file)
                else:
                    df = pd.read_excel(uploaded_file)
                
                st.success(f"✅ File uploaded successfully! Found {len(df)} rows.")
                
                # Display the uploaded data for preview
                st.subheader("📋 Preview of Uploaded Data")
                st.dataframe(df.head(10))
                
                if len(df) > 10:
                    st.info(f"Showing first 10 rows. Total rows: {len(df)}")
                
                # Validate the data structure
                required_columns = ['first_name', 'last_name', 'class_name']
                missing_columns = [col for col in required_columns if col not in df.columns]
                
                if missing_columns:
                    st.error(f"❌ Missing required columns: {', '.join(missing_columns)}")
                    st.info("Please make sure your file has these columns: first_name, last_name, class_name")
                    return
                
                # Validate classes exist and user has access
                unique_class_names = df['class_name'].unique()
                available_class_names = [cls.name for cls in classes]
                invalid_classes = [cls for cls in unique_class_names if cls not in available_class_names]
                
                if invalid_classes:
                    st.error(f"❌ Invalid or inaccessible classes found: {', '.join(invalid_classes)}")
                    st.info(f"Available classes for you: {', '.join(available_class_names)}")
                    return
                
                # Create class name to ID mapping
                class_name_to_id = {cls.name: cls.id for cls in classes}
                
                # Show validation summary
                st.subheader("✅ Validation Summary")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Students", len(df))
                with col2:
                    st.metric("Valid Classes", len(unique_class_names))
                with col3:
                    students_with_aggregate = len(df[df['aggregate'].notna()]) if 'aggregate' in df.columns else 0
                    st.metric("With Aggregate", students_with_aggregate)
                
                # Show class distribution
                st.subheader("📊 Students by Class")
                class_distribution = df['class_name'].value_counts()
                for class_name, count in class_distribution.items():
                    st.write(f"• **{class_name}**: {count} students")
                
                # Process and upload button
                st.subheader("🚀 Upload Students")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button("📤 Upload All Students", type="primary", use_container_width=True):
                        
                        upload_results = bulk_upload_students(df, class_name_to_id)
                        
                        if upload_results['success_count'] > 0:
                            st.success(f"✅ Successfully added {upload_results['success_count']} students!")
                        
                        if upload_results['error_count'] > 0:
                            st.warning(f"⚠️ {upload_results['error_count']} students could not be added:")
                            for error in upload_results['errors']:
                                st.error(f"• {error}")
                        
                        if upload_results['duplicate_count'] > 0:
                            st.info(f"ℹ️ {upload_results['duplicate_count']} duplicate students were skipped")
                            
                        # Show summary
                        total_processed = upload_results['success_count'] + upload_results['error_count'] + upload_results['duplicate_count']
                        st.write(f"**Summary:** {total_processed} students processed")
                        
                        if upload_results['success_count'] > 0:
                            st.balloons()
                
                with col2:
                    st.button("❌ Cancel Upload", use_container_width=True)
                
            except Exception as e:
                st.error(f"❌ Error reading file: {str(e)}")
                st.info("Please make sure your file is in the correct format (CSV or Excel) and is not corrupted.")
    
    with tab3:
        st.subheader("📋 Download Upload Template")
        st.info("Download this template file to ensure your bulk upload data is in the correct format.")
        
        # Create sample template data
        template_data = {
            'student_id': ['', '', '', ''],  # Optional - leave empty for auto-assignment
            'first_name': ['John', 'Jane', 'Michael', 'Sarah'],
            'last_name': ['Smith', 'Doe', 'Johnson', 'Williams'],
            'class_name': [], 
            'aggregate': [85.5, 92.0, 78.5, 88.0]
        }
        
        # Fill class names with available classes (cycling through them)
        available_class_names = [cls.name for cls in classes]
        if available_class_names:
            for i in range(len(template_data['first_name'])):
                template_data['class_name'].append(available_class_names[i % len(available_class_names)])
        else:
            template_data['class_name'] = ['Class1A', 'Class1B', 'Class2A', 'Class2B']
        
        template_df = pd.DataFrame(template_data)
        
        # Show template preview
        st.write("**Template Preview:**")
        st.dataframe(template_df)
        
        # Column descriptions
        st.write("**Column Descriptions:**")
        st.write("• **student_id**: Student's unique ID number (optional - leave empty for auto-assignment)")
        st.write("• **first_name**: Student's first name (required)")
        st.write("• **last_name**: Student's last name (required)")
        st.write("• **class_name**: Exact class name as it appears in your system (required)")
        st.write("• **aggregate**: Student's aggregate score as percentage (optional, 0-100)")
        
        # Download buttons
        col1, col2 = st.columns(2)
        
        with col1:
            # CSV download
            csv = template_df.to_csv(index=False)
            st.download_button(
                label="📁 Download CSV Template",
                data=csv,
                file_name="student_upload_template.csv",
                mime="text/csv",
                use_container_width=True
            )
        
        with col2:
            # Excel download
            excel_buffer = io.BytesIO()
            with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                template_df.to_excel(writer, sheet_name='Students', index=False)
                
                # Auto-adjust column widths
                worksheet = writer.sheets['Students']
                for column in worksheet.columns:
                    max_length = 0
                    column_letter = column[0].column_letter
                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass
                    adjusted_width = min(max_length + 2, 50)
                    worksheet.column_dimensions[column_letter].width = adjusted_width
            
            excel_buffer.seek(0)
            st.download_button(
                label="📊 Download Excel Template",
                data=excel_buffer.getvalue(),
                file_name="student_upload_template.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
        
        # Available classes info
        st.subheader("📚 Available Classes")
        if classes:
            st.write("Use these exact class names in your upload file:")
            for idx, cls in enumerate(classes, 1):
                st.write(f"{idx}. **{cls.name}** ({cls.category})")
        else:
            st.warning("No classes available. Please create classes first.")


def bulk_upload_students(df, class_name_to_id):
    """Process bulk student upload from DataFrame"""
    results = {
        'success_count': 0,
        'error_count': 0,
        'duplicate_count': 0,
        'errors': []
    }
    
    with get_session() as session:
        for index, row in df.iterrows():
            try:
                # Extract data from row
                first_name = str(row['first_name']).strip()
                last_name = str(row['last_name']).strip()
                class_name = str(row['class_name']).strip()
                
                # Handle student_id (optional field)
                student_id = None
                if 'student_id' in row and pd.notna(row['student_id']) and str(row['student_id']).strip():
                    try:
                        student_id = int(row['student_id'])
                        # Check if this ID already exists
                        existing_id = session.exec(
                            select(Student).where(Student.id == student_id)
                        ).first()
                        if existing_id:
                            results['errors'].append(f"Row {index + 1}: Student ID {student_id} already exists")
                            results['error_count'] += 1
                            continue
                    except (ValueError, TypeError):
                        results['errors'].append(f"Row {index + 1}: Invalid student ID format (must be a number)")
                        results['error_count'] += 1
                        continue
                
                # Handle aggregate (optional field)
                aggregate = None
                if 'aggregate' in row and pd.notna(row['aggregate']):
                    try:
                        aggregate = float(row['aggregate'])
                        if aggregate < 0 or aggregate > 100:
                            results['errors'].append(f"Row {index + 1}: Invalid aggregate score {aggregate} (must be 0-100)")
                            results['error_count'] += 1
                            continue
                    except (ValueError, TypeError):
                        results['errors'].append(f"Row {index + 1}: Invalid aggregate score format")
                        results['error_count'] += 1
                        continue
                
                # Validate required fields
                if not first_name or first_name.lower() == 'nan':
                    results['errors'].append(f"Row {index + 1}: Missing first name")
                    results['error_count'] += 1
                    continue
                    
                if not last_name or last_name.lower() == 'nan':
                    results['errors'].append(f"Row {index + 1}: Missing last name")
                    results['error_count'] += 1
                    continue
                
                if class_name not in class_name_to_id:
                    results['errors'].append(f"Row {index + 1}: Invalid class name '{class_name}'")
                    results['error_count'] += 1
                    continue
                
                # Check for duplicates
                existing_student = session.exec(
                    select(Student).where(
                        Student.first_name == first_name,
                        Student.last_name == last_name,
                        Student.class_id == class_name_to_id[class_name]
                    )
                ).first()
                
                if existing_student:
                    results['duplicate_count'] += 1
                    continue
                
                # Create new student
                student = Student(
                    first_name=first_name,
                    last_name=last_name,
                    class_id=class_name_to_id[class_name],
                    aggregate=aggregate
                )
                
                # Set custom ID if provided
                if student_id is not None:
                    student.id = student_id
                
                session.add(student)
                results['success_count'] += 1
                
            except Exception as e:
                results['errors'].append(f"Row {index + 1}: {str(e)}")
                results['error_count'] += 1
        
        # Commit all successful additions
        try:
            session.commit()
        except Exception as e:
            session.rollback()
            results['errors'].append(f"Database error: {str(e)}")
            results['error_count'] += results['success_count']
            results['success_count'] = 0
    
    return results


def subject_form():
    st.header("Manage Subjects")
    
    # Create tabs for different actions
    tab1, tab2, tab3 = st.tabs(["➕ Add Subject", "📋 View & Edit Subjects", "🎯 Subject Types & Aggregates"])
    
    with tab1:
        st.subheader("Add New Subject")
        # Define available categories
        categories = ["Lower Primary", "Upper Primary", "JHS"]
        
        with st.form("subject_form"):
            category_selection = st.selectbox(
                "Category", 
                options=categories
            )
            name = st.text_input("Subject name")
            code = st.text_input("Subject code")
            subject_type = st.selectbox(
                "Subject Type",
                options=["core", "elective"],
                help="Core subjects are required for aggregate calculation. Elective subjects are optional."
            )
            submitted = st.form_submit_button("Save Subject")
            
        if submitted and category_selection and name and code:
            with get_session() as s:
                # Check if subject with same code already exists for this category
                existing = s.exec(
                    select(Subject).where(
                        Subject.code == code, 
                        Subject.category == category_selection
                    )
                ).first()
                
                if existing:
                    st.error(f"Subject with code '{code}' already exists for {category_selection}")
                else:
                    subj = Subject(
                        name=name, 
                        code=code, 
                        category=category_selection,
                        subject_type=subject_type
                    )
                    s.add(subj)
                    s.commit()
                    st.success(f"Subject '{name}' added to {category_selection} as {subject_type} subject")
        elif submitted:
            st.error("Please fill in all fields")
    
    with tab2:
        st.subheader("All Subjects")
        
        # Display existing subjects grouped by category
        with get_session() as s:
            subjects = s.exec(select(Subject).order_by(Subject.category, Subject.name)).all()
            
        if subjects:
            # Group subjects by category
            subjects_by_category = {}
            
            for subject in subjects:
                category = subject.category
                if category not in subjects_by_category:
                    subjects_by_category[category] = []
                subjects_by_category[category].append(subject)
            
            # Display summary statistics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Subjects", len(subjects))
            with col2:
                st.metric("Categories", len(subjects_by_category))
            with col3:
                # Count marks for all subjects
                with get_session() as s:
                    marks_count = len(s.exec(select(Mark)).all())
                st.metric("Total Marks", marks_count)
            
            st.divider()
            
            # Display subjects grouped by category
            for category, category_subjects in subjects_by_category.items():
                st.subheader(f"📚 {category}")
                
                # Table header
                header_col1, header_col2, header_col3, header_col4, header_col5 = st.columns([3, 2, 1, 1, 1])
                with header_col1:
                    st.write("**Subject Name**")
                with header_col2:
                    st.write("**Code**")
                with header_col3:
                    st.write("**Marks Count**")
                with header_col4:
                    st.write("**✏️ Edit**")
                with header_col5:
                    st.write("**🗑️ Delete**")
                
                st.divider()
                
                for idx, subject in enumerate(category_subjects):
                    # Get marks count for this subject
                    with get_session() as s:
                        marks_count = len(s.exec(select(Mark).where(Mark.subject_id == subject.id)).all())
                    
                    # Create columns for subject info and actions
                    col1, col2, col3, col4, col5 = st.columns([3, 2, 1, 1, 1])
                    
                    with col1:
                        st.write(f"**{subject.name}**")
                    with col2:
                        st.write(subject.code)
                    with col3:
                        st.write(str(marks_count))
                    with col4:
                        # Edit button
                        edit_key = f"edit_subject_{subject.id}_{idx}"
                        if st.button("✏️ Edit", key=edit_key, help=f"Edit {subject.name}", use_container_width=True):
                            st.session_state[f"editing_subject_{subject.id}"] = True
                            st.rerun()
                    with col5:
                        # Delete button
                        delete_key = f"delete_subject_{subject.id}_{idx}"
                        if st.button("🗑️", key=delete_key, help=f"Delete {subject.name}", type="secondary", use_container_width=True):
                            st.session_state[f"confirm_delete_subject_{subject.id}"] = True
                            st.rerun()
                    
                    # Edit form (appears when edit button is clicked)
                    if st.session_state.get(f"editing_subject_{subject.id}", False):
                        with st.expander(f"✏️ Editing {subject.name}", expanded=True):
                            with st.form(f"edit_subject_form_{subject.id}"):
                                edit_col1, edit_col2 = st.columns(2)
                                
                                with edit_col1:
                                    new_name = st.text_input("Subject Name", value=subject.name)
                                    new_code = st.text_input("Subject Code", value=subject.code)
                                    
                                with edit_col2:
                                    categories = ["Lower Primary", "Upper Primary", "JHS"]
                                    current_category_index = categories.index(subject.category) if subject.category in categories else 0
                                    new_category = st.selectbox(
                                        "Category",
                                        options=categories,
                                        index=current_category_index
                                    )
                                    
                                    # Subject type selection
                                    subject_types = ["core", "elective"]
                                    current_type_index = subject_types.index(subject.subject_type) if subject.subject_type in subject_types else 1
                                    new_subject_type = st.selectbox(
                                        "Subject Type",
                                        options=subject_types,
                                        index=current_type_index,
                                        help="Core subjects are required for aggregate calculation"
                                    )
                                
                                form_col1, form_col2, form_col3 = st.columns(3)
                                
                                with form_col1:
                                    if st.form_submit_button("💾 Save Changes", type="primary"):
                                        try:
                                            with get_session() as s:
                                                # Check for duplicate code in the same category (excluding current subject)
                                                existing = s.exec(
                                                    select(Subject).where(
                                                        Subject.code == new_code,
                                                        Subject.category == new_category,
                                                        Subject.id != subject.id
                                                    )
                                                ).first()
                                                
                                                if existing:
                                                    st.error(f"Subject with code '{new_code}' already exists in {new_category}")
                                                else:
                                                    subject_to_update = s.get(Subject, subject.id)
                                                    if subject_to_update:
                                                        subject_to_update.name = new_name
                                                        subject_to_update.code = new_code
                                                        subject_to_update.category = new_category
                                                        subject_to_update.subject_type = new_subject_type
                                                        s.add(subject_to_update)
                                                        s.commit()
                                                        st.success(f"✅ Updated {new_name} as {new_subject_type} subject")
                                                        del st.session_state[f"editing_subject_{subject.id}"]
                                                        time.sleep(1)
                                                        st.rerun()
                                                    else:
                                                        st.error("Subject not found")
                                        except Exception as e:
                                            st.error(f"Error updating subject: {str(e)}")
                                
                                with form_col2:
                                    if st.form_submit_button("❌ Cancel"):
                                        del st.session_state[f"editing_subject_{subject.id}"]
                                        st.rerun()
                    
                    # Delete confirmation (appears when delete button is clicked)
                    if st.session_state.get(f"confirm_delete_subject_{subject.id}", False):
                        with st.container():
                            st.error(f"⚠️ **Confirm deletion of {subject.name}**")
                            
                            if marks_count > 0:
                                st.warning(f"This subject has **{marks_count} associated marks** that will also be deleted!")
                            
                            confirm_col1, confirm_col2 = st.columns(2)
                            
                            with confirm_col1:
                                confirm_key = f"confirm_final_subject_{subject.id}"
                                if st.button(f"🗑️ Yes, Delete {subject.name}", key=confirm_key, type="primary"):
                                    try:
                                        with get_session() as s:
                                            # Delete associated marks first
                                            marks_to_delete = s.exec(
                                                select(Mark).where(Mark.subject_id == subject.id)
                                            ).all()
                                            
                                            for mark in marks_to_delete:
                                                s.delete(mark)
                                            
                                            # Delete the subject
                                            subject_to_delete = s.get(Subject, subject.id)
                                            if subject_to_delete:
                                                s.delete(subject_to_delete)
                                                s.commit()
                                                st.success(f"✅ Deleted {subject.name} and {len(marks_to_delete)} marks")
                                                del st.session_state[f"confirm_delete_subject_{subject.id}"]
                                                time.sleep(1)
                                                st.rerun()
                                            else:
                                                st.error("Subject not found")
                                    except Exception as e:
                                        st.error(f"Error deleting subject: {str(e)}")
                                        s.rollback()
                            
                            with confirm_col2:
                                cancel_key = f"cancel_delete_subject_{subject.id}"
                                if st.button("❌ Cancel", key=cancel_key, type="secondary"):
                                    del st.session_state[f"confirm_delete_subject_{subject.id}"]
                                    st.rerun()
                    
                    # Add divider between subjects (except for the last one)
                    if idx < len(category_subjects) - 1:
                        st.divider()
                
                # Add spacing between categories
                if category != list(subjects_by_category.keys())[-1]:
                    st.write("")
                    st.write("")
        else:
            st.info("No subjects created yet.")
    
    with tab3:
        st.subheader("🎯 Subject Types & Aggregate Calculation")
        
        # Display current subject type distribution
        with get_session() as s:
            subjects = s.exec(select(Subject)).all()
            core_subjects = [s for s in subjects if s.subject_type == 'core']
            elective_subjects = [s for s in subjects if s.subject_type == 'elective']
        
        st.info("**Aggregate Calculation Rule**: 4 Core Subjects + 2 Best Elective Subjects = 600 points maximum")
        
        # Summary metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Core Subjects", len(core_subjects), help="Required for aggregate calculation")
        with col2:
            st.metric("Elective Subjects", len(elective_subjects), help="Best 2 scores used for aggregate")
        with col3:
            st.metric("Total Subjects", len(subjects))
        
        st.divider()
        
        # Subject type management
        st.subheader("📋 Manage Subject Types")
        
        if subjects:
            # Display subjects with their types
            for category in ["Lower Primary", "Upper Primary", "JHS"]:
                category_subjects = [s for s in subjects if s.category == category]
                if category_subjects:
                    st.write(f"**{category}**")
                    
                    for subject in category_subjects:
                        col1, col2, col3 = st.columns([3, 2, 2])
                        
                        with col1:
                            st.write(f"• {subject.name} ({subject.code})")
                        
                        with col2:
                            current_type = subject.subject_type
                            if current_type == 'core':
                                st.success("🎯 CORE")
                            else:
                                st.info("📚 ELECTIVE")
                        
                        with col3:
                            # Toggle button
                            new_type = "elective" if current_type == "core" else "core"
                            toggle_key = f"toggle_type_{subject.id}"
                            
                            if st.button(f"→ Make {new_type.title()}", key=toggle_key):
                                with get_session() as session:
                                    subject_to_update = session.get(Subject, subject.id)
                                    if subject_to_update:
                                        subject_to_update.subject_type = new_type
                                        session.add(subject_to_update)
                                        session.commit()
                                        st.success(f"Changed {subject.name} to {new_type.title()}")
                                        st.rerun()
                    
                    st.write("")
        
        st.divider()
        
        # Aggregate calculation tools
        st.subheader("🧮 Aggregate Calculation Tools")
        
        # Individual student aggregate calculation
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Individual Student Calculation**")
            
            # Student selection
            with get_session() as s:
                students = s.exec(select(Student)).all()
            
            if students:
                selected_student = st.selectbox(
                    "Select Student",
                    options=students,
                    format_func=lambda x: f"{x.first_name} {x.last_name}",
                    key="aggregate_student_select"
                )
                
                term_select = st.selectbox("Select Term", ["Term 1", "Term 2", "Term 3"], index=2)
                exam_type_select = st.selectbox("Select Exam Type", ["Mid-term", "External", "End of Term"], index=2)
                
                if st.button("Calculate Aggregate", key="calc_individual"):
                    if selected_student and selected_student.id:
                        aggregate = calculate_student_aggregate(selected_student.id, term_select, exam_type_select)
                        
                        if aggregate is not None:
                            st.success(f"🎯 **Aggregate Score: {aggregate:.1f}/600**")
                            
                            # Update the student record
                            if update_student_aggregate(selected_student.id, term_select, exam_type_select):
                                st.info("✅ Student record updated")
                        else:
                            st.error("❌ Cannot calculate aggregate - insufficient marks")
                            st.write("Required: 4 core subject marks + 2 elective subject marks")
        
        with col2:
            st.write("**Bulk Aggregate Calculation**")
            
            bulk_term = st.selectbox("Select Term for All", ["Term 1", "Term 2", "Term 3"], index=2, key="bulk_term")
            bulk_exam = st.selectbox("Select Exam Type for All", ["Mid-term", "External", "End of Term"], index=2, key="bulk_exam")
            
            if st.button("Calculate All Students", key="calc_all", type="primary"):
                with st.spinner("Calculating aggregates for all students..."):
                    result = update_all_student_aggregates(bulk_term, bulk_exam)
                    
                    col_a, col_b, col_c = st.columns(3)
                    
                    with col_a:
                        st.metric("✅ Updated", result['updated_count'])
                    with col_b:
                        st.metric("❌ Failed", result['failed_count'])
                    with col_c:
                        st.metric("📊 Total", result['total_students'])
                    
                    if result['updated_count'] > 0:
                        st.success(f"Successfully updated {result['updated_count']} student aggregates!")
                    
                    if result['failed_count'] > 0:
                        st.warning(f"{result['failed_count']} students couldn't be calculated (insufficient marks)")
        
        st.divider()
        
        # Aggregate requirements info
        with st.expander("ℹ️ Aggregate Calculation Information"):
            st.markdown("""
            **How Aggregate is Calculated:**
            
            1. **Core Subjects (4 required)**: All 4 core subject scores are included
            2. **Elective Subjects (2 best)**: The 2 highest elective scores are selected
            3. **Total Score**: Sum of 4 core + 2 best elective = X/600
            
            **Requirements:**
            - Student must have marks in at least 4 core subjects
            - Student must have marks in at least 2 elective subjects
            - Calculation uses specified term and exam type
            - Missing subjects will prevent aggregate calculation
            
            **Subject Type Assignment:**
            - Use the toggle buttons above to change subjects between Core and Elective
            - Core subjects are typically: English, Mathematics, Science, Social Studies
            - Elective subjects vary by level and include: Arts, Music, PE, ICT, etc.
            """)
    


def marks_form():
    st.header("Enter Marks")
    
    # Get current user for filtering
    current_user = get_current_user()
    if not current_user:
        st.error("Please log in to enter marks.")
        return
    
    user_role = current_user.get('role', '')
    user_id = current_user.get('id', 0)
    
    # Ensure user_id is valid
    if not user_id or user_id == 0:
        st.error("Invalid user session. Please log in again.")
        return
    
    with get_session() as s:
        # Filter students based on user role and permissions
        if user_role == 'Teacher':
            # Get only students from teacher's assigned classes
            accessible_student_ids = get_user_accessible_students(user_id, user_role)
            
            if accessible_student_ids == [-1]:
                st.warning("No class assignments found. Please contact an administrator to assign you to classes.")
                return
            elif accessible_student_ids == [-2]:
                st.info("You are assigned to classes, but there are no students in your assigned classes yet.")
                return
            else:
                # Get students based on accessible IDs
                if accessible_student_ids:
                    students = []
                    for student_id in accessible_student_ids:
                        student = s.get(Student, student_id)
                        if student:
                            students.append(student)
                else:
                    students = []
        else:
            # Admin and Head can see all students
            students = s.exec(select(Student)).all()
        
        classes = s.exec(select(Class)).all()
    
    if not students:
        if user_role == 'Teacher':
            st.info("No students found in your assigned classes.")
        else:
            st.info("Create students first")
        return
    
    # Create a mapping of student to class for display
    class_map = {cls.id: cls for cls in classes}
    
    # Step 1: Select student (outside form for interactivity)
    def format_student(student):
        class_obj = class_map.get(student.class_id)
        class_name = class_obj.name if class_obj else 'Unknown Class'
        return f"{student.first_name} {student.last_name} ({class_name})"
    
    student = st.selectbox(
        "Select Student", 
        options=students, 
        format_func=format_student,
        key="student_selection"
    )
    
    if student:
        # Get the student's class category
        student_class = class_map.get(student.class_id)
        student_category = student_class.category if student_class else "Lower Primary"
        
        # Get subjects for the selected student's class category
        with get_session() as s:
            subjects = s.exec(
                select(Subject).where(Subject.category == student_category)
            ).all()
        
        if not subjects:
            st.warning(f"No subjects found for {student_category}. Please add subjects for this category first.")
            return
        
        # Step 2: Form for mark entry
        with st.form("marks_form"):
            st.write(f"**Student:** {student.first_name} {student.last_name}")
            class_obj = class_map.get(student.class_id)
            class_name = class_obj.name if class_obj else 'Unknown Class'
            st.write(f"**Class:** {class_name}")
            st.write(f"**Category:** {student_category}")
            
            subject = st.selectbox(
                "Subject", 
                options=subjects, 
                format_func=lambda x: f"{x.name} ({x.code})"
            )
            term = st.selectbox("Term", options=["Term 1", "Term 2", "Term 3"])
            exam_type = st.selectbox("Exam Type", options=["Mid-term", "External", "End of Term"])
            score = st.number_input("Score (%)", min_value=0.0, max_value=100.0, step=0.5, 
                                   help="Enter score as a percentage (0-100%). Values outside this range will be rejected.")
            
            # Enhanced validation with clear error messaging
            validation_error = None
            validated_score = None
            
            try:
                validated_score = validate_and_normalize_score(score)
            except ValueError as e:
                validation_error = str(e)
                st.error(f"⚠️ **Invalid Score**: {str(e)}")
            
            # Show grade preview only for valid scores
            if validated_score is not None and validated_score >= 0:
                if validated_score > 0:
                    grade = calculate_grade(validated_score)
                    grade_desc = get_grade_description(grade)
                    st.info(f"📊 **Grade: {grade} ({grade_desc})** for {validated_score:.1f}%")
                else:
                    st.info("📊 **Grade: 9 (LOWEST)** for 0.0%")
            
            submitted = st.form_submit_button("Save Mark")
        
        if submitted and subject and validated_score is not None and validation_error is None:
            with get_session() as s:
                # Check if mark already exists for this student, subject, term, and exam type
                existing_mark = s.exec(
                    select(Mark).where(
                        Mark.student_id == student.id,
                        Mark.subject_id == subject.id,
                        Mark.term == term,
                        Mark.exam_type == exam_type
                    )
                ).first()
                
                if existing_mark:
                    # Update existing mark with validated score and grade
                    existing_mark.score = validated_score
                    existing_mark.grade = calculate_grade(validated_score)
                    s.add(existing_mark)
                    s.commit()
                    grade_desc = get_grade_description(existing_mark.grade)
                    st.success(f"Updated {exam_type} mark for {subject.name} - {term}: {validated_score:.1f}% (Grade {existing_mark.grade}: {grade_desc})")
                    
                    # Auto-calculate aggregate for any exam type
                    if update_student_aggregate(student.id, term, exam_type):
                        st.info(f"📊 Student aggregate updated automatically for {exam_type}")
                        
                        # Show transparency - what subjects were selected
                        detailed_aggregate = calculate_student_aggregate_detailed(student.id, term, exam_type)
                        if detailed_aggregate and detailed_aggregate.get('aggregate') is not None:
                            with st.expander("🔍 View Aggregate Calculation Details", expanded=False):
                                st.write("**For transparency, here's how the aggregate was calculated:**")
                                
                                # Show selected electives
                                if detailed_aggregate.get('selected_electives'):
                                    st.write("**Selected Elective Subjects (best 2 by highest scores):**")
                                    for subject in detailed_aggregate['selected_electives']:
                                        st.write(f"• {subject['subject_name']}: {subject['score']:.1f}% (Grade {subject['grade']}) ✅")
                                
                                # Show calculation summary
                                if detailed_aggregate.get('calculation_details'):
                                    calc_details = detailed_aggregate['calculation_details']
                                    st.write(f"**Final Aggregate:** {calc_details['aggregate']} (Core: {calc_details['core_total']} + Electives: {calc_details['elective_total']})")
                                    
                                st.info("💡 The system automatically selected your best 2 elective subjects to give you the highest possible aggregate!")
                                    
                        else:
                            st.warning("Could not show calculation details (insufficient marks for complete aggregate)")
                else:
                    # Create new mark with validated score and grade
                    grade = calculate_grade(validated_score)
                    m = Mark(
                        student_id=student.id, 
                        subject_id=subject.id, 
                        term=term, 
                        exam_type=exam_type,
                        score=validated_score,
                        grade=grade
                    )
                    s.add(m)
                    s.commit()
                    grade_desc = get_grade_description(grade)
                    st.success(f"Saved {exam_type} mark for {subject.name} - {term}: {validated_score:.1f}% (Grade {grade}: {grade_desc})")
                    
                    # Auto-calculate aggregate for any exam type
                    if update_student_aggregate(student.id, term, exam_type):
                        st.info(f"📊 Student aggregate updated automatically for {exam_type}")
                        
                        # Show transparency - what subjects were selected
                        detailed_aggregate = calculate_student_aggregate_detailed(student.id, term, exam_type)
                        if detailed_aggregate and detailed_aggregate.get('aggregate') is not None:
                            with st.expander("🔍 View Aggregate Calculation Details", expanded=False):
                                st.write("**For transparency, here's how the aggregate was calculated:**")
                                
                                # Show selected electives
                                if detailed_aggregate.get('selected_electives'):
                                    st.write("**Selected Elective Subjects (best 2 by highest scores):**")
                                    for subject in detailed_aggregate['selected_electives']:
                                        st.write(f"• {subject['subject_name']}: {subject['score']:.1f}% (Grade {subject['grade']}) ✅")
                                
                                # Show calculation summary
                                if detailed_aggregate.get('calculation_details'):
                                    calc_details = detailed_aggregate['calculation_details']
                                    st.write(f"**Final Aggregate:** {calc_details['aggregate']} (Core: {calc_details['core_total']} + Electives: {calc_details['elective_total']})")
                                    
                                st.info("💡 The system automatically selected your best 2 elective subjects to give you the highest possible aggregate!")
                                    
                        else:
                            st.warning("Could not show calculation details (insufficient marks for complete aggregate)")
        elif submitted and validation_error is not None:
            # Handle validation errors - show specific error messages
            st.error(f"❌ **Mark not saved!** {validation_error}")
            st.warning("Please correct the score and try again. Valid scores must be between 0 and 100 (inclusive).")
        elif submitted and not subject:
            st.error("❌ **Mark not saved!** Please select a subject.")
    
    # Display existing marks
    st.subheader("Recent Marks")
    with get_session() as s:
        marks = s.exec(select(Mark).order_by(Mark.id.desc()).limit(10)).all()
        
    if marks:
        for mark in marks:
            with get_session() as s:
                student = s.get(Student, mark.student_id)
                subject = s.get(Subject, mark.subject_id)
                
            if student and subject:
                col1, col2, col3, col4, col5 = st.columns([2, 2, 1, 1, 1])
                with col1:
                    st.write(f"{student.first_name} {student.last_name}")
                with col2:
                    st.write(f"{subject.name} ({subject.code})")
                with col3:
                    st.write(f"{mark.term}: {mark.score}%")
                with col4:
                    if mark.grade:
                        grade_desc = get_grade_description(mark.grade)
                        st.write(f"Grade {mark.grade}")
                        st.caption(grade_desc)
                    else:
                        # Calculate grade for old marks that don't have grades
                        grade = calculate_grade(mark.score)
                        st.write(f"Grade {grade}")
                        st.caption(get_grade_description(grade))
                with col5:
                    if st.button("Delete", key=f"del_mark_{mark.id}"):
                        with get_session() as s:
                            s.delete(s.get(Mark, mark.id))
                            s.commit()
                            st.rerun()
    else:
        st.info("No marks entered yet.")

    # Admin-only section for deleting all marks
    current_user = get_current_user()
    if current_user and has_permission(current_user.get('role', ''), "marks.delete_all"):
        st.markdown("---")
        st.subheader("🚨 Admin Actions")
        
        with st.expander("⚠️ Delete All Marks (Admin Only)"):
            st.error("**WARNING**: This action will permanently delete ALL marks from ALL students. This cannot be undone!")
            
            # Get total marks count for confirmation
            with get_session() as s:
                total_marks = len(s.exec(select(Mark)).all())
            
            if total_marks == 0:
                st.info("No marks in the database to delete.")
            else:
                st.write(f"**Total marks in database: {total_marks}**")
                
                # First confirmation
                confirm_delete = st.checkbox("I understand this will delete ALL marks from ALL students")
                
                # Second confirmation
                confirm_text = st.text_input(
                    "Type 'DELETE ALL MARKS' to confirm:",
                    placeholder="Type the exact phrase to confirm"
                )
                
                # Final confirmation button
                if confirm_delete and confirm_text == "DELETE ALL MARKS":
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        if st.button("❌ Cancel Operation", key="cancel_delete_all"):
                            st.info("Delete operation cancelled.")
                    
                    with col2:
                        if st.button("🗑️ PERMANENTLY DELETE ALL MARKS", type="primary", key="execute_delete_all"):
                            # Execute the deletion immediately
                            try:
                                with st.spinner("Deleting all marks..."):
                                    with get_session() as s:
                                        # Get all marks and delete them
                                        all_marks = s.exec(select(Mark)).all()
                                        deleted_count = len(all_marks)
                                        
                                        # Delete all marks one by one (more reliable)
                                        for mark in all_marks:
                                            s.delete(mark)
                                        
                                        s.commit()
                                        
                                        # Verify deletion
                                        remaining_marks = s.exec(select(Mark)).all()
                                        
                                        if len(remaining_marks) == 0:
                                            st.success(f"✅ Successfully deleted {deleted_count} marks from all students.")
                                            st.info("🔄 The page will refresh automatically in 3 seconds...")
                                            st.balloons()
                                            time.sleep(3)
                                            st.rerun()
                                        else:
                                            st.error(f"❌ Deletion incomplete. {len(remaining_marks)} marks remaining.")
                                            
                            except Exception as e:
                                st.error(f"❌ Error deleting marks: {str(e)}")
                                st.exception(e)
                elif confirm_text and confirm_text != "DELETE ALL MARKS":
                    st.warning("Please type the exact phrase 'DELETE ALL MARKS' to proceed.")
