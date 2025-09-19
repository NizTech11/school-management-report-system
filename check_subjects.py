#!/usr/bin/env python3
"""Check which subjects students have marks for"""

from src.services.db import get_session, Student, Subject, Mark
from sqlmodel import select

def check_student_subjects():
    """Check which subjects each student has marks for"""
    with get_session() as session:
        students = session.exec(select(Student)).all()
        
        for student in students[:3]:  # Check first 3 students
            print(f"\nStudent: {student.first_name} {student.last_name}")
            
            # Get Term 2 End of Term marks
            marks = session.exec(
                select(Mark).where(
                    Mark.student_id == student.id,
                    Mark.term == "Term 2"
                )
            ).all()
            
            # Filter for End of Term marks
            end_term_marks = [m for m in marks if getattr(m, 'exam_type', None) == 'End of Term']
            
            print(f"  End of Term marks in Term 2: {len(end_term_marks)}")
            
            # Group by subject type
            core_subjects = []
            elective_subjects = []
            
            for mark in end_term_marks:
                subject = session.exec(select(Subject).where(Subject.id == mark.subject_id)).first()
                if subject:
                    if subject.subject_type == 'core':
                        core_subjects.append((subject.name, mark.score))
                    elif subject.subject_type == 'elective':
                        elective_subjects.append((subject.name, mark.score))
            
            print(f"  Core subjects ({len(core_subjects)}): {[f'{name}:{score}' for name, score in core_subjects]}")
            print(f"  Elective subjects ({len(elective_subjects)}): {[f'{name}:{score}' for name, score in elective_subjects]}")
        
        # Also check which subjects are available
        print(f"\n=== Available Subjects ===")
        subjects = session.exec(select(Subject)).all()
        core_subjects = [s for s in subjects if s.subject_type == 'core']
        elective_subjects = [s for s in subjects if s.subject_type == 'elective']
        
        print(f"Core subjects ({len(core_subjects)}): {[s.name for s in core_subjects]}")
        print(f"Elective subjects ({len(elective_subjects)}): {[s.name for s in elective_subjects]}")

if __name__ == "__main__":
    check_student_subjects()