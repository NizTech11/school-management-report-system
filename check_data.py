#!/usr/bin/env python3
"""Check available data in database"""

from src.services.db import get_session, Mark, Subject, Student
from sqlmodel import select
from collections import Counter

def check_database():
    """Check what data is available in the database"""
    with get_session() as session:
        # Check marks
        marks = session.exec(select(Mark)).all()
        print(f"Total marks: {len(marks)}")
        
        terms = [m.term for m in marks]
        print(f"Available terms: {Counter(terms)}")
        
        exam_types = [getattr(m, 'exam_type', 'N/A') for m in marks]
        print(f"Available exam types: {Counter(exam_types)}")
        
        # Check subjects
        subjects = session.exec(select(Subject)).all()
        print(f"\nTotal subjects: {len(subjects)}")
        
        subject_names = [s.name for s in subjects]
        print(f"Subject name counts: {Counter(subject_names)}")
        
        # Check students
        students = session.exec(select(Student)).all()
        print(f"\nTotal students: {len(students)}")
        
        # Check a sample student's marks for Term 2 End of Term
        student = students[0]
        term2_marks = session.exec(
            select(Mark).where(
                Mark.student_id == student.id,
                Mark.term == "Term 2"
            )
        ).all()
        
        print(f"\nSample student ({student.first_name} {student.last_name}) Term 2 marks:")
        for mark in term2_marks:
            subject = session.exec(select(Subject).where(Subject.id == mark.subject_id)).first()
            exam_type = getattr(mark, 'exam_type', 'N/A')
            print(f"  {subject.name} ({subject.subject_type}): {mark.score} - {exam_type}")

if __name__ == "__main__":
    check_database()