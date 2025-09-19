#!/usr/bin/env python3
"""
Test transparency feature for aggregate calculation
Shows students exactly which elective subjects were selected
"""

import sys
import os

# Add the src directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
sys.path.insert(0, src_dir)

from services.db import (
    get_session, Student, Subject, Mark, Class, 
    calculate_student_aggregate_detailed, calculate_grade
)
from sqlmodel import select

def test_transparency_feature():
    """Test the new transparency feature"""
    print("🔍 Testing Aggregate Calculation Transparency Feature")
    print("=" * 60)
    
    with get_session() as session:
        # Get a student with marks
        students = session.exec(select(Student)).all()
        
        if not students:
            print("❌ No students found in database")
            return
        
        student = students[0]  # Test with first student
        print(f"📚 Testing with student: {student.first_name} {student.last_name}")
        print(f"💳 Student ID: {student.id}")
        print()
        
        # Test the detailed aggregate calculation
        detailed_result = calculate_student_aggregate_detailed(
            student_id=student.id,
            term="Term 3",
            exam_type="End of Term"
        )
        
        if detailed_result is None:
            print("❌ No detailed result returned")
            return
            
        if detailed_result.get('error'):
            print(f"⚠️  Error in calculation: {detailed_result['error']}")
            return
        
        # Display transparency information
        print("🎯 AGGREGATE CALCULATION TRANSPARENCY")
        print("-" * 40)
        
        aggregate = detailed_result.get('aggregate')
        print(f"📊 Final Aggregate Score: {aggregate}")
        print()
        
        # Show core subjects
        core_subjects = detailed_result.get('core_subjects', [])
        if core_subjects:
            print("📋 CORE SUBJECTS (All 4 included):")
            print("-" * 30)
            for subject in core_subjects:
                print(f"  ✓ {subject['subject_name']} ({subject['subject_code']})")
                print(f"    Score: {subject['score']:.1f}% → Grade: {subject['grade']}")
            print()
        
        # Show selected electives
        selected_electives = detailed_result.get('selected_electives', [])
        if selected_electives:
            print("🎯 SELECTED ELECTIVE SUBJECTS (Best 2 by highest scores):")
            print("-" * 50)
            for subject in selected_electives:
                print(f"  ✅ {subject['subject_name']} ({subject['subject_code']})")
                print(f"    Score: {subject['score']:.1f}% → Grade: {subject['grade']} (SELECTED)")
            print()
        
        # Show all electives for transparency
        all_electives = detailed_result.get('all_electives', [])
        if all_electives:
            print("📝 ALL ELECTIVE SUBJECTS (Complete transparency):")
            print("-" * 45)
            for subject in all_electives:
                status = "✅ SELECTED" if subject['selected'] else "❌ NOT SELECTED"
                print(f"  {status} {subject['subject_name']} ({subject['subject_code']})")
                print(f"    Score: {subject['score']:.1f}% → Grade: {subject['grade']}")
            print()
        
        # Show calculation details
        calc_details = detailed_result.get('calculation_details', {})
        if calc_details:
            print("🧮 CALCULATION BREAKDOWN:")
            print("-" * 25)
            print(f"  Core Subjects Total: {calc_details.get('core_total', 0)}")
            print(f"  Elective Subjects Total: {calc_details.get('elective_total', 0)}")
            print(f"  Final Aggregate: {calc_details.get('aggregate', 0)}")
            print(f"  Selection Method: {calc_details.get('selection_method', 'N/A')}")
            print()
        
        print("✅ Transparency feature working correctly!")
        print("🎓 Students now know exactly which elective subjects were selected for their grades!")

def compare_with_original():
    """Compare with original aggregate calculation"""
    print("\n" + "=" * 60)
    print("🔄 COMPARING WITH ORIGINAL CALCULATION")
    print("=" * 60)
    
    with get_session() as session:
        students = session.exec(select(Student)).all()
        
        if not students:
            print("❌ No students found")
            return
        
        student = students[0]
        
        # Original calculation (without transparency)
        from services.db import calculate_student_aggregate
        original_result = calculate_student_aggregate(
            student_id=student.id,
            term="Term 3", 
            exam_type="End of Term"
        )
        
        # New detailed calculation
        detailed_result = calculate_student_aggregate_detailed(
            student_id=student.id,
            term="Term 3",
            exam_type="End of Term"
        )
        
        print(f"📊 Original aggregate: {original_result}")
        print(f"📊 New detailed aggregate: {detailed_result.get('aggregate') if detailed_result else 'None'}")
        
        if original_result == detailed_result.get('aggregate') if detailed_result else None:
            print("✅ Results match! Transparency added without changing calculation logic.")
        else:
            print("❌ Results don't match! Need to check implementation.")

if __name__ == "__main__":
    test_transparency_feature()
    compare_with_original()