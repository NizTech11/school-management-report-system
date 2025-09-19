#!/usr/bin/env python3
"""Add marks for David Wilson to test complete aggregate calculation"""

import random
from src.services.db import get_session, Student, Subject, Mark
from sqlmodel import select

def add_david_marks():
    """Add elective marks for David Wilson"""
    with get_session() as session:
        # Find David Wilson
        david = next((st for st in session.exec(select(Student)).all() if st.first_name == 'David'), None)
        
        if not david:
            print("David Wilson not found")
            return
        
        # Find elective subjects he doesn't have marks for
        subjects = session.exec(select(Subject)).all()
        elective_subjects = [s for s in subjects if s.subject_type == 'elective']
        
        # Find which electives he already has
        existing_marks = session.exec(
            select(Mark).where(
                Mark.student_id == david.id,
                Mark.term == "Term 2"
            )
        ).all()
        
        existing_subject_ids = [m.subject_id for m in existing_marks]
        needed_electives = [s for s in elective_subjects if s.id not in existing_subject_ids]
        
        print(f"David needs marks for {len(needed_electives)} elective subjects")
        
        # Add marks for 2 elective subjects
        for subject in needed_electives[:2]:
            # Mid-term
            midterm_mark = Mark(
                student_id=david.id,
                subject_id=subject.id,
                term="Term 2",
                exam_type="Mid-term",
                score=random.randint(70, 85)
            )
            session.add(midterm_mark)
            
            # End of Term
            endterm_mark = Mark(
                student_id=david.id,
                subject_id=subject.id,
                term="Term 2",
                exam_type="End of Term",
                score=random.randint(75, 90)
            )
            session.add(endterm_mark)
            
            print(f"Added {subject.name}: {midterm_mark.score} (Mid-term), {endterm_mark.score} (End of Term)")
        
        session.commit()
        print("David's marks added successfully!")

if __name__ == "__main__":
    add_david_marks()