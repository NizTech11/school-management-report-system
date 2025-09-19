#!/usr/bin/env python3
"""Check class and student categories"""

from src.services.db import get_session, Student, Class, Subject
from sqlmodel import select

def check_categories():
    """Check categories across classes, students, and subjects"""
    with get_session() as session:
        # Check classes
        classes = session.exec(select(Class)).all()
        print("Classes and their categories:")
        print("=" * 40)
        for cls in classes:
            print(f"{cls.name}: {cls.category}")
        
        # Check students and their class categories
        students = session.exec(select(Student)).all()[:5]
        print("\nStudents and their class categories:")
        print("=" * 40)
        
        for student in students:
            if student.class_id:
                student_class = session.get(Class, student.class_id)
                category = student_class.category if student_class else "None"
            else:
                category = "No Class"
            print(f"{student.first_name} {student.last_name}: {category}")
        
        # Check subject categories
        subjects = session.exec(select(Subject)).all()
        categories = set(subject.category for subject in subjects)
        print(f"\nSubject categories: {sorted(categories)}")

if __name__ == "__main__":
    check_categories()