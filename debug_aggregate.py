#!/usr/bin/env python3
"""Debug the aggregate calculation system"""

from src.services.db import get_session, Student, Subject, Mark
from sqlmodel import select

def debug_student_marks():
    """Debug student marks and subject types"""
    with get_session() as session:
        # Get first student
        student = session.exec(select(Student)).first()
        print(f"Student: {student.first_name} {student.last_name} (ID: {student.id})")
        
        # Get all marks for this student
        marks = session.exec(select(Mark).where(Mark.student_id == student.id)).all()
        print(f"\nStudent has {len(marks)} marks:")
        
        for mark in marks:
            subject = session.exec(select(Subject).where(Subject.id == mark.subject_id)).first()
            print(f"  {subject.name} ({subject.subject_type}): {mark.score} - Term: {mark.term}, Type: {getattr(mark, 'exam_type', 'N/A')}")
        
        # Check subject types distribution
        subjects = session.exec(select(Subject)).all()
        core_subjects = [s for s in subjects if s.subject_type == 'core']
        elective_subjects = [s for s in subjects if s.subject_type == 'elective']
        
        print(f"\nCore subjects ({len(core_subjects)}):")
        for s in core_subjects:
            print(f"  - {s.name}")
        
        print(f"\nElective subjects ({len(elective_subjects)}):")
        for s in elective_subjects:
            print(f"  - {s.name}")

if __name__ == "__main__":
    debug_student_marks()