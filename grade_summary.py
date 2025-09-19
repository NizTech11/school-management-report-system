#!/usr/bin/env python3
"""Show grade distribution summary"""

from src.services.db import get_session, Mark, get_grade_description
from sqlmodel import select
from collections import Counter

def show_grade_distribution():
    """Display grade distribution across all marks"""
    
    with get_session() as session:
        marks = session.exec(select(Mark)).all()
        
        if not marks:
            print("No marks found in database")
            return
        
        # Count grades
        grades = [mark.grade for mark in marks if mark.grade is not None]
        grade_counts = Counter(grades)
        
        print("Grade Distribution Summary")
        print("=" * 50)
        print(f"Total Marks: {len(marks)}")
        print(f"Marks with Grades: {len(grades)}")
        print()
        
        print("Grade | Count | Percentage | Description")
        print("-" * 45)
        
        for grade in sorted(grade_counts.keys()):
            count = grade_counts[grade]
            percentage = (count / len(grades)) * 100
            desc = get_grade_description(grade)
            print(f"  {grade}   |  {count:3d}  |   {percentage:5.1f}%   | {desc}")
        
        print()
        
        # Show score ranges for reference
        print("Grade Scale Reference:")
        print("=" * 25)
        score_ranges = [
            (1, "90-100%", "Excellent"),
            (2, "80-89%", "Very Good"), 
            (3, "70-79%", "Good"),
            (4, "60-69%", "Satisfactory"),
            (5, "50-59%", "Fair"),
            (6, "40-49%", "Poor"),
            (7, "30-39%", "Very Poor"),
            (8, "20-29%", "Weak"),
            (9, "10-19%", "Very Weak/Failed")
        ]
        
        for grade, range_str, desc in score_ranges:
            print(f"Grade {grade}: {range_str:8} - {desc}")

if __name__ == "__main__":
    show_grade_distribution()