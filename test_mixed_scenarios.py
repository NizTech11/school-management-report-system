#!/usr/bin/env python3
"""
Test script to demonstrate how "best two subjects" works with mixed grades
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from services.db import calculate_grade, get_grade_description

def test_mixed_grade_scenarios():
    """Test how the best two subjects logic works with different grade combinations"""
    
    print("🧪 Testing Mixed Grade Scenarios - 'Best Two' Selection")
    print("=" * 60)
    
    # Test different scenarios
    scenarios = [
        {
            "name": "All Grade 9 (Worst Case)",
            "elective_scores": [10, 15, 20, 25, 30],  # All result in Grade 9
            "description": "When all elective subjects are Grade 9"
        },
        {
            "name": "Mixed Grades - Some Good, Some Bad", 
            "elective_scores": [85, 72, 45, 25, 60],  # Grades: 1, 2, 7, 9, 4
            "description": "Mix of high and low performing subjects"
        },
        {
            "name": "Two Excellent, Rest Poor",
            "elective_scores": [95, 88, 30, 25, 35],  # Grades: 1, 1, 9, 9, 8  
            "description": "Student excels in 2 subjects, struggles in others"
        },
        {
            "name": "Gradually Declining Performance",
            "elective_scores": [75, 68, 58, 48, 38],  # Grades: 2, 3, 5, 7, 8
            "description": "Performance gets progressively worse"
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n📊 Scenario {i}: {scenario['name']}")
        print(f"Description: {scenario['description']}")
        print("-" * 40)
        
        # Calculate grades for each elective subject
        elective_grades = []
        print("Elective subject breakdown:")
        for j, score in enumerate(scenario['elective_scores'], 1):
            grade = calculate_grade(score)
            grade_desc = get_grade_description(grade)
            elective_grades.append(grade)
            print(f"  Subject {j}: {score}% → Grade {grade} ({grade_desc})")
        
        # Apply the "best two" logic
        sorted_grades = sorted(elective_grades)  # Sort ascending (lower is better)
        best_two = sorted_grades[:2]
        
        print(f"\nAll elective grades: {elective_grades}")
        print(f"Sorted grades (ascending): {sorted_grades}")
        print(f"✅ Best two selected: {best_two} (sum: {sum(best_two)})")
        
        # Show which subjects were selected
        selected_indices = []
        remaining_grades = elective_grades.copy()
        for grade in best_two:
            idx = remaining_grades.index(grade)
            selected_indices.append(elective_grades.index(grade, sum(selected_indices)))
            remaining_grades[idx] = None  # Mark as used
        
        print(f"Selected subjects: {[f'Subject {i+1}' for i in selected_indices]}")

def demonstrate_aggregate_calculation():
    """Show complete aggregate calculation with different scenarios"""
    
    print("\n" + "=" * 60)
    print("🎯 Complete Aggregate Calculation Examples")
    print("=" * 60)
    
    # Assume core subjects are consistent
    core_scores = [75, 68, 72, 70]  # Math, English, Science, Social Studies
    core_grades = [calculate_grade(score) for score in core_scores]
    core_total = sum(core_grades)
    
    print(f"Core subjects (fixed for all examples):")
    for i, (score, grade) in enumerate(zip(core_scores, core_grades)):
        subject_names = ['Math', 'English', 'Science', 'Social Studies']
        grade_desc = get_grade_description(grade)
        print(f"  {subject_names[i]}: {score}% → Grade {grade} ({grade_desc})")
    print(f"Core total: {core_total}")
    
    # Different elective scenarios
    elective_scenarios = [
        {"name": "Excellent Student", "scores": [95, 90, 85, 80, 75]},
        {"name": "Average Student", "scores": [65, 60, 55, 52, 48]},
        {"name": "Struggling Student", "scores": [30, 25, 20, 15, 10]},
        {"name": "Mixed Performance", "scores": [85, 45, 70, 25, 55]}
    ]
    
    for scenario in elective_scenarios:
        print(f"\n📋 {scenario['name']} - Elective Performance:")
        
        elective_grades = [calculate_grade(score) for score in scenario['scores']]
        sorted_grades = sorted(elective_grades)
        best_two = sorted_grades[:2]
        elective_total = sum(best_two)
        
        print(f"  Elective scores: {scenario['scores']}")
        print(f"  Elective grades: {elective_grades}")
        print(f"  Best two grades: {best_two}")
        print(f"  Elective total: {elective_total}")
        
        total_aggregate = core_total + elective_total
        print(f"  🏆 Final Aggregate: {core_total} + {elective_total} = {total_aggregate}")
        
        # Show performance level
        if total_aggregate <= 12:
            performance = "EXCELLENT"
        elif total_aggregate <= 24:
            performance = "GOOD"  
        elif total_aggregate <= 36:
            performance = "AVERAGE"
        else:
            performance = "NEEDS IMPROVEMENT"
        
        print(f"  📊 Performance Level: {performance}")

if __name__ == "__main__":
    test_mixed_grade_scenarios()
    demonstrate_aggregate_calculation()