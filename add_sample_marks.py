#!/usr/bin/env python3
"""
Script to add sample marks for testing the delete functionality
"""

import sys
sys.path.append('src')

from services.db import get_session, Mark, Student, Subject
from sqlmodel import select
import random

def add_sample_marks():
    """Add sample marks for testing"""
    print("📝 Adding sample marks for testing...")
    
    with get_session() as session:
        # Get all students and subjects
        students = session.exec(select(Student)).all()
        subjects = session.exec(select(Subject)).all()
        
        if not students or not subjects:
            print("❌ No students or subjects found!")
            return
        
        print(f"👥 Found {len(students)} students")
        print(f"📚 Found {len(subjects)} subjects")
        
        # Add marks for each student and subject
        marks_added = 0
        for student in students[:5]:  # First 5 students
            for subject in subjects[:3]:  # First 3 subjects
                for term in ["Term 1", "Term 2"]:
                    for exam_type in ["Mid-term", "End of Term"]:
                        mark = Mark(
                            student_id=student.id,
                            subject_id=subject.id,
                            term=term,
                            exam_type=exam_type,
                            score=random.randint(60, 95)
                        )
                        session.add(mark)
                        marks_added += 1
        
        session.commit()
        print(f"✅ Added {marks_added} sample marks")
        
        # Verify
        total_marks = len(session.exec(select(Mark)).all())
        print(f"📊 Total marks in database: {total_marks}")

if __name__ == "__main__":
    add_sample_marks()