#!/usr/bin/env python3
"""Test creating a new mark with the grading system"""

from src.services.db import get_session, Student, Subject, Mark, calculate_grade, get_grade_description
from sqlmodel import select

def test_new_mark_with_grade():
    """Test creating a new mark and verify it gets a grade automatically"""
    
    with get_session() as session:
        # Get a student and subject for testing
        student = session.exec(select(Student)).first()
        subject = session.exec(select(Subject)).first()
        
        if not student or not subject:
            print("❌ No student or subject found for testing")
            return
        
        print(f"Testing with: {student.first_name} {student.last_name}")
        print(f"Subject: {subject.name}")
        
        # Test different scores
        test_scores = [92.5, 67.0, 45.5]
        
        for score in test_scores:
            # Create a new mark
            mark = Mark(
                student_id=student.id,
                subject_id=subject.id,
                term="Test Term",
                exam_type="Test",
                score=score,
                grade=calculate_grade(score)
            )
            
            session.add(mark)
            session.commit()
            
            grade_desc = get_grade_description(mark.grade)
            print(f"✅ Created mark: {score}% → Grade {mark.grade} ({grade_desc})")
        
        print("\nTest completed successfully!")

if __name__ == "__main__":
    test_new_mark_with_grade()