#!/usr/bin/env python3
"""Add sample marks for testing aggregate calculation"""

import random
from src.services.db import get_session, Student, Subject, Mark
from sqlmodel import select

def add_sample_marks():
    """Add sample marks to complete the aggregate calculation test"""
    with get_session() as session:
        students = session.exec(select(Student)).all()
        subjects = session.exec(select(Subject)).all()
        
        # Find unique subjects (remove duplicates)
        unique_subjects = {}
        for subject in subjects:
            if subject.name not in unique_subjects:
                unique_subjects[subject.name] = subject
        
        core_subjects = [s for s in unique_subjects.values() if s.subject_type == 'core']
        elective_subjects = [s for s in unique_subjects.values() if s.subject_type == 'elective']
        
        print(f"Found {len(core_subjects)} unique core subjects")
        print(f"Found {len(elective_subjects)} unique elective subjects")
        
        # Add marks for each student
        for student in students[:3]:  # First 3 students for testing
            print(f"\nAdding marks for {student.first_name} {student.last_name}")
            
            # Add History marks (4th core subject) if missing
            history_subject = next((s for s in core_subjects if s.name == 'History'), None)
            if history_subject:
                # Check if student already has History marks
                existing_mark = session.exec(
                    select(Mark).where(
                        Mark.student_id == student.id,
                        Mark.subject_id == history_subject.id,
                        Mark.term == "Term 2"
                    )
                ).first()
                
                if not existing_mark:
                    # Add Mid-term mark
                    midterm_mark = Mark(
                        student_id=student.id,
                        subject_id=history_subject.id,
                        term="Term 2",
                        score=random.randint(60, 95),
                        exam_type="Mid-term"
                    )
                    session.add(midterm_mark)
                    
                    # Add End of Term mark
                    endterm_mark = Mark(
                        student_id=student.id,
                        subject_id=history_subject.id,
                        term="Term 2",
                        score=random.randint(60, 95),
                        exam_type="End of Term"
                    )
                    session.add(endterm_mark)
                    print(f"  Added History marks: {midterm_mark.score} (Mid-term), {endterm_mark.score} (End of Term)")
            
            # Add 3 elective subject marks (we need only 2 for aggregate, but 3 gives choice)
            sample_electives = random.sample(elective_subjects, min(3, len(elective_subjects)))
            
            for elective in sample_electives:
                # Check if student already has marks for this elective
                existing_mark = session.exec(
                    select(Mark).where(
                        Mark.student_id == student.id,
                        Mark.subject_id == elective.id,
                        Mark.term == "Term 2"
                    )
                ).first()
                
                if not existing_mark:
                    # Add Mid-term mark
                    midterm_mark = Mark(
                        student_id=student.id,
                        subject_id=elective.id,
                        term="Term 2",
                        score=random.randint(55, 90),
                        exam_type="Mid-term"
                    )
                    session.add(midterm_mark)
                    
                    # Add End of Term mark
                    endterm_mark = Mark(
                        student_id=student.id,
                        subject_id=elective.id,
                        term="Term 2",
                        score=random.randint(55, 90),
                        exam_type="End of Term"
                    )
                    session.add(endterm_mark)
                    print(f"  Added {elective.name} marks: {midterm_mark.score} (Mid-term), {endterm_mark.score} (End of Term)")
        
        session.commit()
        print("\nSample marks added successfully!")

if __name__ == "__main__":
    add_sample_marks()