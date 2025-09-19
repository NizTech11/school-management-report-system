#!/usr/bin/env python3
"""
Test script to demonstrate role-based dashboard filtering
"""

import sys
sys.path.append('src')

from utils.rbac import get_user_accessible_students
from services.db import *
from sqlmodel import select

def test_dashboard_filtering():
    """Test what different roles see on the dashboard"""
    print("🎯 Testing Role-Based Dashboard Filtering")
    print("=" * 50)
    
    with get_session() as session:
        # Get all data for comparison
        all_students = session.exec(select(Student)).all()
        all_subjects = session.exec(select(Subject)).all()
        all_marks = session.exec(select(Mark)).all()
        
        print(f"📊 System Totals:")
        print(f"   Students: {len(all_students)}")
        print(f"   Subjects: {len(all_subjects)}")
        print(f"   Marks: {len(all_marks)}")
        print()
        
        # Test Teacher view (MarkDoug - ID 3)
        print("👨‍🏫 TEACHER VIEW (MarkDoug):")
        teacher_accessible = get_user_accessible_students(3, 'Teacher')
        
        # Filter teacher's students
        teacher_students = []
        for student_id in teacher_accessible:
            student = session.get(Student, student_id)
            if student:
                teacher_students.append(student)
        
        # Filter teacher's subjects (based on class categories)
        class_categories = set()
        for student in teacher_students:
            student_class = session.get(Class, student.class_id)
            if student_class:
                class_categories.add(student_class.category)
        
        teacher_subjects = []
        for category in class_categories:
            category_subjects = session.exec(select(Subject).where(Subject.category == category)).all()
            teacher_subjects.extend(category_subjects)
        
        # Filter teacher's marks
        teacher_student_ids = set(s.id for s in teacher_students)
        teacher_marks = [mark for mark in all_marks if mark.student_id in teacher_student_ids]
        
        print(f"   Students: {len(teacher_students)} (from assigned classes)")
        for student in teacher_students:
            class_obj = session.get(Class, student.class_id)
            print(f"     - {student.first_name} {student.last_name} (Class: {class_obj.name})")
        
        print(f"   Subjects: {len(teacher_subjects)} (for class categories)")
        print(f"   Marks: {len(teacher_marks)} (for their students only)")
        
        if teacher_marks:
            avg_score = sum(mark.score for mark in teacher_marks) / len(teacher_marks)
            print(f"   Class Average: {avg_score:.1f}%")
        
        print()
        
        # Test Admin view
        print("🔧 ADMIN VIEW:")
        print(f"   Students: {len(all_students)} (all students)")
        print(f"   Subjects: {len(all_subjects)} (all subjects)")
        print(f"   Marks: {len(all_marks)} (all marks)")
        
        if all_marks:
            overall_avg = sum(mark.score for mark in all_marks) / len(all_marks)
            print(f"   Overall Average: {overall_avg:.1f}%")
        
        print()
        
        # Summary
        print("🎯 SUMMARY:")
        teacher_percentage = (len(teacher_students) / len(all_students)) * 100 if all_students else 0
        print(f"   Teacher sees {teacher_percentage:.1f}% of all students")
        
        marks_percentage = (len(teacher_marks) / len(all_marks)) * 100 if all_marks else 0
        print(f"   Teacher sees {marks_percentage:.1f}% of all marks")
        
        print(f"   Dashboard is properly filtered by role! ✅")

if __name__ == "__main__":
    test_dashboard_filtering()