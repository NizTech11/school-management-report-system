#!/usr/bin/env python3
"""Check that existing marks have grades"""

from src.services.db import get_session, Mark, calculate_grade, get_grade_description
from sqlmodel import select

def check_mark_grades():
    """Check that existing marks have grades calculated"""
    with get_session() as session:
        marks = session.exec(select(Mark).limit(10)).all()
        
        print("Sample marks with grades:")
        print("=" * 40)
        
        for i, mark in enumerate(marks[:10]):
            grade = mark.grade if mark.grade else calculate_grade(mark.score)
            grade_desc = get_grade_description(grade)
            print(f"{i+1}. Score: {mark.score}%, Grade: {grade} ({grade_desc})")
        
        # Check grade distribution
        all_marks = session.exec(select(Mark)).all()
        grades_with_data = [m for m in all_marks if m.grade is not None]
        grades_without_data = [m for m in all_marks if m.grade is None]
        
        print(f"\nTotal marks: {len(all_marks)}")
        print(f"Marks with grades: {len(grades_with_data)}")
        print(f"Marks without grades: {len(grades_without_data)}")

if __name__ == "__main__":
    check_mark_grades()