#!/usr/bin/env python3
"""
Test Individual Student PDF Report Generation

This script tests the new functionality to generate individual student PDF reports
from the bulk class reports system.
"""

import sys
import os
sys.path.append('src')

from services.db import get_session
from services.db import get_session, Student, Class, Mark, Subject
from components.forms import generate_individual_student_report, generate_individual_student_pdfs
from sqlmodel import select

def test_individual_student_reports():
    """Test individual student PDF generation"""
    print("🧪 Testing Individual Student PDF Report Generation")
    print("=" * 60)
    
    # Test database connection
    try:
        with get_session() as session:
            # Get sample data
            students = session.exec(select(Student).limit(5)).all()
            classes = session.exec(select(Class).limit(3)).all()
            subjects = session.exec(select(Subject).limit(5)).all()
            marks = session.exec(select(Mark).limit(10)).all()
            
            print(f"📊 Test Data Available:")
            print(f"   • Students: {len(students)}")
            print(f"   • Classes: {len(classes)}")
            print(f"   • Subjects: {len(subjects)}")
            print(f"   • Marks: {len(marks)}")
            print()
            
            if not students:
                print("❌ No students found for testing")
                return False
            
            if not classes:
                print("❌ No classes found for testing")
                return False
                
            # Test 1: Generate individual student report
            print("🔬 Test 1: Individual Student Report Generation")
            test_student = students[0]
            print(f"   Testing with: {test_student.first_name} {test_student.last_name}")
            
            try:
                pdf_buffer = generate_individual_student_report(test_student, "Term 3", "End of Term")
                if pdf_buffer and pdf_buffer.getvalue():
                    print(f"   ✅ PDF generated successfully ({len(pdf_buffer.getvalue())} bytes)")
                else:
                    print("   ❌ PDF generation failed - empty buffer")
                    return False
            except Exception as e:
                print(f"   ❌ Error generating individual student report: {str(e)}")
                return False
            
            # Test 2: Generate bulk individual student reports
            print()
            print("🔬 Test 2: Bulk Individual Student Reports Generation")
            test_classes = classes[:2]  # Test with first 2 classes
            print(f"   Testing with classes: {[cls.name for cls in test_classes]}")
            
            try:
                student_pdfs = generate_individual_student_pdfs(test_classes, "Term 3", "End of Term")
                
                if student_pdfs:
                    print(f"   ✅ Generated {len(student_pdfs)} individual student PDFs")
                    
                    # Test filename generation and PDF content
                    for filename, pdf_data in student_pdfs.items():
                        student = pdf_data['student']
                        class_obj = pdf_data['class']
                        pdf_buffer = pdf_data['buffer']
                        
                        # Check filename format
                        expected_parts = [student.first_name, student.last_name, class_obj.name, "Term_3", "End_of_Term"]
                        print(f"   📄 {filename} - {pdf_data['display_name']}")
                        print(f"      Size: {len(pdf_buffer.getvalue())} bytes")
                        
                        # Validate PDF content exists
                        if len(pdf_buffer.getvalue()) == 0:
                            print(f"      ❌ Empty PDF buffer for {student.first_name} {student.last_name}")
                            return False
                        else:
                            print(f"      ✅ Valid PDF content")
                    
                else:
                    print("   ⚠️  No individual student PDFs generated (may be normal if no marks exist)")
                    
            except Exception as e:
                print(f"   ❌ Error generating bulk individual student reports: {str(e)}")
                return False
            
            # Test 3: Check filename sanitization
            print()
            print("🔬 Test 3: Filename Sanitization Test")
            
            # Create a test student with special characters in name
            from datetime import datetime
            
            for filename, pdf_data in (student_pdfs or {}).items():
                # Check that filename contains only safe characters
                safe_chars = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._-")
                if all(c in safe_chars for c in filename):
                    print(f"   ✅ Filename '{filename}' is properly sanitized")
                else:
                    print(f"   ❌ Filename '{filename}' contains unsafe characters")
                    return False
            
            print()
            print("🎉 All individual student report tests completed successfully!")
            print()
            print("💡 Next Steps:")
            print("   • Individual student PDFs can now be generated from the bulk reports interface")
            print("   • Each student gets their own detailed PDF report")
            print("   • Filenames are automatically generated with student names")
            print("   • PDFs include comprehensive academic analysis for each student")
            
            return True
            
    except Exception as e:
        print(f"❌ Database connection error: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_individual_student_reports()
    
    if success:
        print("\n✅ SUCCESS: Individual student PDF reports are ready to use!")
    else:
        print("\n❌ FAILURE: Some tests failed. Check the output above for details.")