#!/usr/bin/env python3
"""
Professional School Report Template
Clean, modern design with proper spacing and alignment
"""

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Frame
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from datetime import datetime
from io import BytesIO


def create_professional_report_template(student_data, marks_data, aggregate_details, term="Term 3", exam_type="End of Term"):
    """
    Create a professional, clean school report template
    
    Features:
    - Proper spacing and alignment
    - Professional color scheme
    - Clean typography
    - Well-organized sections
    - Consistent formatting
    """
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, 
        pagesize=A4, 
        topMargin=60,
        bottomMargin=60, 
        leftMargin=60, 
        rightMargin=60
    )
    story = []
    
    # Define professional color palette
    SCHOOL_BLUE = colors.Color(0.1, 0.2, 0.5)      # Dark blue
    LIGHT_BLUE = colors.Color(0.85, 0.9, 1.0)      # Light blue
    ACCENT_GOLD = colors.Color(1.0, 0.8, 0.0)      # Gold/Yellow
    SUCCESS_GREEN = colors.Color(0.2, 0.7, 0.3)    # Green
    TEXT_GRAY = colors.Color(0.3, 0.3, 0.3)        # Dark gray
    LIGHT_GRAY = colors.Color(0.95, 0.95, 0.95)    # Light gray
    
    # Enhanced typography styles
    styles = getSampleStyleSheet()
    
    # School header styles
    school_title_style = ParagraphStyle(
        'SchoolTitle',
        parent=styles['Title'],
        fontSize=18,
        fontName='Helvetica-Bold',
        textColor=SCHOOL_BLUE,
        alignment=TA_CENTER,
        spaceAfter=8
    )
    
    school_subtitle_style = ParagraphStyle(
        'SchoolSubtitle',
        parent=styles['Normal'],
        fontSize=12,
        fontName='Helvetica',
        textColor=TEXT_GRAY,
        alignment=TA_CENTER,
        spaceAfter=6
    )
    
    contact_style = ParagraphStyle(
        'Contact',
        parent=styles['Normal'],
        fontSize=10,
        fontName='Helvetica',
        textColor=TEXT_GRAY,
        alignment=TA_CENTER,
        spaceAfter=20
    )
    
    report_title_style = ParagraphStyle(
        'ReportTitle',
        parent=styles['Normal'],
        fontSize=14,
        fontName='Helvetica-Bold',
        textColor=colors.white,
        alignment=TA_CENTER,
        backColor=SCHOOL_BLUE,
        borderPadding=12,
        spaceAfter=25
    )
    
    section_header_style = ParagraphStyle(
        'SectionHeader',
        parent=styles['Normal'],
        fontSize=11,
        fontName='Helvetica-Bold',
        textColor=SCHOOL_BLUE,
        spaceAfter=8,
        spaceBefore=15
    )
    
    # === HEADER SECTION ===
    story.append(Paragraph("BRIGHT KIDS INTERNATIONAL SCHOOL", school_title_style))
    story.append(Paragraph("Excellence in Education", school_subtitle_style))
    story.append(Paragraph("P.O. Box SC 344, Sekondi", contact_style))
    story.append(Paragraph("📧 brightkidsint@gmail.com  |  📞 0533150076 / 0551215664", contact_style))
    
    # Decorative line
    line_table = Table([["_" * 80]], colWidths=[450])
    line_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('TEXTCOLOR', (0, 0), (-1, -1), LIGHT_BLUE),
        ('FONTSIZE', (0, 0), (-1, -1), 8)
    ]))
    story.append(line_table)
    story.append(Spacer(1, 15))
    
    # === REPORT TITLE ===
    current_year = datetime.now().year
    exam_titles = {
        "Mid-term": f"MID-TERM EXAMINATION REPORT (3RD TERM {current_year})",
        "End of Term": f"END OF TERM EXAMINATION REPORT (3RD TERM {current_year})",
        "External": f"EXTERNAL EXAMINATION REPORT (3RD TERM {current_year})"
    }
    report_title = exam_titles.get(exam_type, f"EXAMINATION REPORT (3RD TERM {current_year})")
    
    story.append(Paragraph(report_title, report_title_style))
    
    # === STUDENT INFORMATION SECTION ===
    story.append(Paragraph("STUDENT INFORMATION", section_header_style))
    
    # Format current date professionally
    current_date = datetime.now()
    formatted_date = current_date.strftime("%B %d, %Y")
    
    # Student info with clean layout
    student_info_data = [
        ["Student ID:", student_data.get('student_id', 'N/A'), "", "Academic Year:", student_data.get('year', 'YEAR 1B')],
        ["", "", "", "", ""],
        ["Full Name:", student_data.get('name', ''), "", "Report Date:", formatted_date],
        ["", "", "", "", ""],
        ["Roll Number:", student_data.get('roll_number', '23'), "", "Term:", term.upper()]
    ]
    
    student_table = Table(student_info_data, colWidths=[80, 140, 20, 80, 130])
    student_table.setStyle(TableStyle([
        # Labels styling
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (3, 0), (3, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TEXTCOLOR', (0, 0), (0, -1), SCHOOL_BLUE),
        ('TEXTCOLOR', (3, 0), (3, -1), SCHOOL_BLUE),
        
        # Data styling
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTNAME', (4, 0), (4, -1), 'Helvetica'),
        
        # Borders for data fields
        ('BOX', (1, 0), (1, 0), 1.5, SCHOOL_BLUE),  # Student ID
        ('BOX', (4, 0), (4, 0), 1.5, SCHOOL_BLUE),  # Year
        ('BOX', (1, 2), (1, 2), 1.5, SCHOOL_BLUE),  # Name
        ('BOX', (4, 2), (4, 2), 1.5, SCHOOL_BLUE),  # Date
        ('BOX', (1, 4), (1, 4), 1.5, SCHOOL_BLUE),  # Roll Number
        ('BOX', (4, 4), (4, 4), 1.5, SCHOOL_BLUE),  # Term
        
        # Padding and alignment
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
    ]))
    story.append(student_table)
    story.append(Spacer(1, 25))
    
    # === ACADEMIC PERFORMANCE SECTION ===
    story.append(Paragraph("ACADEMIC PERFORMANCE", section_header_style))
    
    # Performance table with enhanced design
    performance_header = ["SUBJECT", "SCORE (%)", "GRADE", "PERFORMANCE LEVEL"]
    performance_data = [performance_header]
    
    # Grade to performance mapping
    performance_levels = {
        1: "OUTSTANDING", 2: "EXCELLENT", 3: "VERY GOOD", 4: "GOOD", 
        5: "SATISFACTORY", 6: "FAIR", 7: "NEEDS IMPROVEMENT", 
        8: "POOR", 9: "VERY POOR"
    }
    
    # Add subject rows
    for mark in marks_data:
        grade = mark.get('grade', '')
        score = mark.get('score', 0)
        subject_name = mark.get('subject_name', '').title()
        
        # Format score
        score_display = f"{score:.1f}" if isinstance(score, float) else str(score)
        
        performance_data.append([
            subject_name,
            score_display,
            str(grade),
            performance_levels.get(grade, "N/A")
        ])
    
    # Add aggregate row
    if aggregate_details:
        performance_data.append([
            "AGGREGATE TOTAL",
            "—",
            str(aggregate_details.get('aggregate', '')),
            "FINAL GRADE"
        ])
    
    # Create performance table
    performance_table = Table(performance_data, colWidths=[150, 80, 60, 120])
    
    # Enhanced table styling
    perf_style = [
        # Header styling
        ('BACKGROUND', (0, 0), (-1, 0), SCHOOL_BLUE),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        
        # General styling
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        
        # Grid and borders
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('LINEBELOW', (0, 0), (-1, 0), 2, SCHOOL_BLUE),
        
        # Padding
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10)
    ]
    
    # Alternate row colors for better readability
    row_count = len(performance_data) - 1
    for i in range(1, row_count):  # Skip header and aggregate
        if i % 2 == 0:
            perf_style.append(('BACKGROUND', (0, i), (-1, i), LIGHT_GRAY))
        else:
            perf_style.append(('BACKGROUND', (0, i), (-1, i), colors.white))
    
    # Special styling for aggregate row
    if aggregate_details:
        aggregate_row = len(performance_data) - 1
        perf_style.extend([
            ('BACKGROUND', (0, aggregate_row), (-1, aggregate_row), SUCCESS_GREEN),
            ('TEXTCOLOR', (0, aggregate_row), (-1, aggregate_row), colors.white),
            ('FONTNAME', (0, aggregate_row), (-1, aggregate_row), 'Helvetica-Bold'),
            ('LINEABOVE', (0, aggregate_row), (-1, aggregate_row), 2, SUCCESS_GREEN)
        ])
    
    performance_table.setStyle(TableStyle(perf_style))
    story.append(performance_table)
    story.append(Spacer(1, 25))
    
    # === SELECTED ELECTIVES SECTION ===
    if aggregate_details and aggregate_details.get('selected_electives'):
        story.append(Paragraph("SELECTED ELECTIVE SUBJECTS", section_header_style))
        
        elective_note = ParagraphStyle(
            'ElectiveNote',
            parent=styles['Normal'],
            fontSize=9,
            fontName='Helvetica-Oblique',
            textColor=TEXT_GRAY,
            spaceAfter=10
        )
        
        story.append(Paragraph("The following two elective subjects with the highest scores were selected for aggregate calculation:", elective_note))
        
        # Electives table
        elective_data = [["SUBJECT", "SCORE (%)", "GRADE", "STATUS"]]
        
        for elective in aggregate_details['selected_electives']:
            score = elective.get('score', 0)
            subject_name = elective.get('subject_name', '').title()
            score_display = f"{score:.1f}" if isinstance(score, float) else str(score)
            
            elective_data.append([
                subject_name,
                score_display,
                str(elective.get('grade', '')),
                "✓ SELECTED"
            ])
        
        elective_table = Table(elective_data, colWidths=[150, 80, 60, 120])
        elective_table.setStyle(TableStyle([
            # Header
            ('BACKGROUND', (0, 0), (-1, 0), ACCENT_GOLD),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            
            # Content
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            
            # Borders and grid
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('LINEBELOW', (0, 0), (-1, 0), 2, ACCENT_GOLD),
            
            # Padding
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            
            # Status column highlighting
            ('TEXTCOLOR', (3, 1), (3, -1), SUCCESS_GREEN),
            ('FONTNAME', (3, 1), (3, -1), 'Helvetica-Bold')
        ]))
        story.append(elective_table)
    
    # === FOOTER ===
    story.append(Spacer(1, 40))
    
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=8,
        fontName='Helvetica-Oblique',
        textColor=TEXT_GRAY,
        alignment=TA_CENTER
    )
    
    story.append(Paragraph(f"Report generated on {formatted_date} | Bright Kids International School", footer_style))
    
    # Build the PDF
    doc.build(story)
    buffer.seek(0)
    return buffer


# Test function
if __name__ == "__main__":
    # Test data
    test_student = {
        'student_id': 'BKIS0030',
        'name': 'AHKURST KYRIE THEODORE',
        'year': 'YEAR 1B',
        'roll_number': '23'
    }
    
    test_marks = [
        {'subject_name': 'English Language', 'score': 100.0, 'grade': 1},
        {'subject_name': 'Mathematics', 'score': 98.0, 'grade': 1},
        {'subject_name': 'Science', 'score': 90.0, 'grade': 1},
        {'subject_name': 'History', 'score': 76.0, 'grade': 3},
        {'subject_name': 'Religious & Moral Education', 'score': 78.0, 'grade': 3},
        {'subject_name': 'Computing', 'score': 86.0, 'grade': 2},
        {'subject_name': 'Creative Arts', 'score': 84.0, 'grade': 2},
        {'subject_name': 'Fante', 'score': 91.0, 'grade': 1},
        {'subject_name': 'French', 'score': 60.0, 'grade': 4},
    ]
    
    test_aggregate = {
        'aggregate': 9,
        'selected_electives': [
            {'subject_name': 'Fante', 'score': 91.0, 'grade': 1},
            {'subject_name': 'Computing', 'score': 86.0, 'grade': 2}
        ]
    }
    
    # Generate test report
    pdf_buffer = create_professional_report_template(test_student, test_marks, test_aggregate)
    
    with open("professional_school_report.pdf", "wb") as f:
        f.write(pdf_buffer.getvalue())
    
    print("✅ Professional report template generated: professional_school_report.pdf")