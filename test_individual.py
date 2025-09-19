#!/usr/bin/env python3
"""Test individual student aggregates"""

from src.services.db import calculate_student_aggregate, get_session, Student
from sqlmodel import select

def test_individual_students():
    """Test aggregate calculation for different individual students"""
    with get_session() as session:
        students = session.exec(select(Student)).all()[:5]  # First 5 students
        
        print("Individual Student Aggregates (Term 2, End of Term):")
        print("=" * 60)
        
        for student in students:
            if student.id:
                aggregate = calculate_student_aggregate(student.id, "Term 2", "End of Term")
                if aggregate is not None:
                    print(f"✅ {student.first_name} {student.last_name}: {aggregate:.1f}/600")
                else:
                    print(f"❌ {student.first_name} {student.last_name}: Insufficient marks")
            else:
                print(f"⚠️ {student.first_name} {student.last_name}: No ID found")
        
        print("\n" + "=" * 60)
        print("Individual Student Aggregates (Term 2, Mid-term):")
        print("=" * 60)
        
        for student in students:
            if student.id:
                aggregate = calculate_student_aggregate(student.id, "Term 2", "Mid-term")
                if aggregate is not None:
                    print(f"✅ {student.first_name} {student.last_name}: {aggregate:.1f}/600")
                else:
                    print(f"❌ {student.first_name} {student.last_name}: Insufficient marks")

if __name__ == "__main__":
    test_individual_students()