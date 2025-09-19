#!/usr/bin/env python3
"""Debug the calculate_student_aggregate function step by step"""

from src.services.db import get_session, Student, Subject, Mark
from sqlmodel import select

def debug_aggregate_calculation(student_id: int, term: str = "Term 2", exam_type: str = "End of Term"):
    """Debug the aggregate calculation step by step"""
    with get_session() as session:
        print(f"Calculating aggregate for student {student_id}, {term}, {exam_type}")
        
        # Step 1: Get all marks for this student in the specified term and exam type
        marks_query = select(Mark).where(
            Mark.student_id == student_id,
            Mark.term == term
        )
        
        marks = session.exec(marks_query).all()
        print(f"Found {len(marks)} marks for student in {term}")
        
        # Filter marks by exam_type if the Mark model has that field
        end_of_term_marks = []
        for mark in marks:
            exam_type_attr = getattr(mark, 'exam_type', None)
            print(f"Mark: subject_id={mark.subject_id}, score={mark.score}, exam_type={exam_type_attr}")
            if exam_type_attr == exam_type:
                end_of_term_marks.append(mark)
        
        print(f"Filtered to {len(end_of_term_marks)} End of Term marks")
        
        # Step 2: Group marks by subject type
        core_marks = []
        elective_marks = []
        
        for mark in end_of_term_marks:
            subject = session.exec(select(Subject).where(Subject.id == mark.subject_id)).first()
            if subject:
                print(f"Subject: {subject.name} ({subject.subject_type}) - Score: {mark.score}")
                if subject.subject_type == 'core':
                    core_marks.append(mark.score)
                elif subject.subject_type == 'elective':
                    elective_marks.append(mark.score)
        
        print(f"Core marks: {core_marks}")
        print(f"Elective marks: {elective_marks}")
        
        # Step 3: Calculate aggregate (4 core + 2 best elective)
        if len(core_marks) >= 4:
            # Take all core subject marks (should be exactly 4 for proper calculation)
            core_total = sum(core_marks)
            print(f"Core total: {core_total}")
            
            # Take 2 best elective marks
            elective_marks_sorted = sorted(elective_marks, reverse=True)
            best_electives = elective_marks_sorted[:2]
            elective_total = sum(best_electives)
            print(f"Best 2 electives: {best_electives}, total: {elective_total}")
            
            aggregate = core_total + elective_total
            print(f"Final aggregate: {aggregate}")
            return aggregate
        else:
            print(f"Not enough core marks ({len(core_marks)}/4)")
            return None

if __name__ == "__main__":
    debug_aggregate_calculation(5)  # David Wilson's ID