#!/usr/bin/env python3
"""Test aggregate calculation with different exam types"""

from src.services.db import calculate_student_aggregate, get_session, Student, Mark, Subject
from sqlmodel import select

def test_exam_type_aggregates():
    """Test aggregate calculation for different exam types"""
    with get_session() as session:
        student = session.exec(select(Student)).first()
        
        if not student:
            print("No students found")
            return
        
        print(f"Testing aggregates for: {student.first_name} {student.last_name}")
        print("=" * 50)
        
        # Test different exam types and terms
        test_combinations = [
            ("Term 1", "Mid-term"),
            ("Term 1", "End of Term"),
            ("Term 2", "Mid-term"),
            ("Term 2", "End of Term")
        ]
        
        for term, exam_type in test_combinations:
            print(f"\n📊 {term} - {exam_type}:")
            
            # Get marks for this combination
            marks = session.exec(
                select(Mark).where(
                    Mark.student_id == student.id,
                    Mark.term == term
                )
            ).all()
            
            # Filter by exam type
            filtered_marks = [m for m in marks if getattr(m, 'exam_type', None) == exam_type]
            
            print(f"   Found {len(filtered_marks)} marks for {exam_type}")
            
            # Show subject breakdown
            core_count = 0
            elective_count = 0
            
            for mark in filtered_marks:
                subject = session.exec(select(Subject).where(Subject.id == mark.subject_id)).first()
                if subject:
                    if subject.subject_type == 'core':
                        core_count += 1
                    elif subject.subject_type == 'elective':
                        elective_count += 1
            
            print(f"   Core subjects: {core_count}, Elective subjects: {elective_count}")
            
            # Calculate aggregate
            aggregate = calculate_student_aggregate(student.id, term, exam_type)
            
            if aggregate is not None:
                print(f"   ✅ Aggregate: {aggregate:.1f}/600")
            else:
                print(f"   ❌ Cannot calculate (need 4 core + 2 elective)")

if __name__ == "__main__":
    test_exam_type_aggregates()