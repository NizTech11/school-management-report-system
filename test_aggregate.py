#!/usr/bin/env python3
"""Test the aggregate calculation system"""

from src.services.db import get_session, Student, Subject, Mark, calculate_student_aggregate, update_all_student_aggregates
from sqlmodel import select

def test_aggregate_system():
    """Test the aggregate calculation system"""
    with get_session() as session:
        # Get all students
        students = session.exec(select(Student)).all()
        print(f"Found {len(students)} students")
        
        # Get all subjects and their types
        subjects = session.exec(select(Subject)).all()
        print(f"\nFound {len(subjects)} subjects:")
        core_subjects = [s for s in subjects if s.subject_type == 'core']
        elective_subjects = [s for s in subjects if s.subject_type == 'elective']
        print(f"- Core subjects: {len(core_subjects)}")
        print(f"- Elective subjects: {len(elective_subjects)}")
        
        # Test with first student if available
        if students:
            student = students[0]
            print(f"\nTesting with student: {student.first_name} {student.last_name}")
            
            # Get student's marks
            marks = session.exec(select(Mark).where(Mark.student_id == student.id)).all()
            print(f"Student has {len(marks)} marks")
            
            # Calculate aggregate
            aggregate = calculate_student_aggregate(student.id)
            print(f"Calculated aggregate: {aggregate}")
            
            # Show current aggregate in database
            updated_student = session.exec(select(Student).where(Student.id == student.id)).first()
            print(f"Current aggregate in database: {updated_student.aggregate}")
        
        # Test bulk update
        print("\nTesting bulk aggregate update...")
        results = update_all_student_aggregates()
        print(f"Updated aggregates for {results['updated']} students")
        print(f"Errors: {results['errors']}")

if __name__ == "__main__":
    test_aggregate_system()