#!/usr/bin/env python3
"""
Test script to demonstrate the improved "best two subjects" logic
that selects based on highest scores rather than just lowest grades
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from services.db import calculate_grade, get_grade_description

def demonstrate_improved_logic():
    """Demonstrate how the improved logic works better with Grade 9 scenarios"""
    
    print("🔄 Improved 'Best Two Subjects' Logic")
    print("=" * 50)
    
    print("📊 The Problem with the Old Logic:")
    print("When all elective subjects resulted in Grade 9, the system")
    print("would pick any 2 subjects randomly since all grades were the same.")
    print()
    
    # Example scenario: Student struggling but with some variation in scores
    print("🎯 Example: Student with all Grade 9 electives but different scores")
    print("-" * 60)
    
    elective_data = [
        {'subject': 'Art', 'score': 34, 'grade': calculate_grade(34)},           # 34% = Grade 9
        {'subject': 'Music', 'score': 28, 'grade': calculate_grade(28)},         # 28% = Grade 9  
        {'subject': 'PE', 'score': 31, 'grade': calculate_grade(31)},            # 31% = Grade 9
        {'subject': 'ICT', 'score': 25, 'grade': calculate_grade(25)},           # 25% = Grade 9
        {'subject': 'French', 'score': 30, 'grade': calculate_grade(30)}         # 30% = Grade 9
    ]
    
    print("All elective subjects and their performance:")
    for data in elective_data:
        grade_desc = get_grade_description(data['grade'])
        print(f"  {data['subject']:8} - {data['score']:2}% → Grade {data['grade']} ({grade_desc})")
    
    print(f"\n📈 OLD LOGIC (selecting by grade):")
    print("All grades are 9, so system would pick any 2 subjects")
    old_grades = [data['grade'] for data in elective_data]
    old_grades.sort()  # Sort by grade
    old_best_two = old_grades[:2]
    print(f"Selected grades: {old_best_two} (sum: {sum(old_best_two)})")
    print("❌ This doesn't consider which subjects the student performed better in!")
    
    print(f"\n🎯 NEW LOGIC (selecting by highest scores first):")
    # Sort by score in descending order (highest first)
    sorted_by_score = sorted(elective_data, key=lambda x: x['score'], reverse=True)
    
    print("Subjects ranked by actual performance (score):")
    for i, data in enumerate(sorted_by_score, 1):
        grade_desc = get_grade_description(data['grade'])
        marker = "✅" if i <= 2 else "  "
        print(f"  {marker} {i}. {data['subject']:8} - {data['score']:2}% → Grade {data['grade']} ({grade_desc})")
    
    # Get the best 2 by score
    best_two_by_score = sorted_by_score[:2]
    new_grades = [data['grade'] for data in best_two_by_score]
    
    print(f"\n✅ Selected subjects: {best_two_by_score[0]['subject']} ({best_two_by_score[0]['score']}%) and {best_two_by_score[1]['subject']} ({best_two_by_score[1]['score']}%)")
    print(f"Selected grades: {new_grades} (sum: {sum(new_grades)})")
    print("✅ This fairly rewards the subjects where student performed relatively better!")

def compare_different_scenarios():
    """Compare old vs new logic across different scenarios"""
    
    print("\n" + "=" * 60)
    print("🔍 Comparison Across Different Scenarios")
    print("=" * 60)
    
    scenarios = [
        {
            "name": "All Grade 9 with Score Variation",
            "scores": [34, 28, 31, 25, 30]  # All Grade 9, but different actual performance
        },
        {
            "name": "Mixed Performance", 
            "scores": [85, 72, 45, 25, 60]  # Mix of grades
        },
        {
            "name": "Close Grade Boundaries",
            "scores": [80, 79, 69, 68, 59]  # Scores near grade boundaries
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n📊 Scenario {i}: {scenario['name']}")
        print("-" * 40)
        
        # Calculate grades and create data
        elective_data = []
        for j, score in enumerate(scenario['scores']):
            elective_data.append({
                'subject': f'Elective {j+1}',
                'score': score,
                'grade': calculate_grade(score)
            })
        
        print("Subject performances:")
        for data in elective_data:
            grade_desc = get_grade_description(data['grade'])
            print(f"  {data['subject']}: {data['score']}% → Grade {data['grade']} ({grade_desc})")
        
        # OLD LOGIC: Sort by grade (ascending)
        old_logic_data = sorted(elective_data, key=lambda x: x['grade'])
        old_best_two = old_logic_data[:2]
        old_sum = sum(data['grade'] for data in old_best_two)
        
        # NEW LOGIC: Sort by score (descending)  
        new_logic_data = sorted(elective_data, key=lambda x: x['score'], reverse=True)
        new_best_two = new_logic_data[:2]
        new_sum = sum(data['grade'] for data in new_best_two)
        
        print(f"\n  🔹 OLD Logic (by grade): {old_best_two[0]['subject']} + {old_best_two[1]['subject']} = Grade sum {old_sum}")
        print(f"  🔹 NEW Logic (by score): {new_best_two[0]['subject']} + {new_best_two[1]['subject']} = Grade sum {new_sum}")
        
        # Show if there's a difference
        if old_sum != new_sum:
            if new_sum < old_sum:
                print(f"  ✅ NEW logic gives BETTER aggregate (lower sum = better)")
            else:
                print(f"  ⚠️  NEW logic gives WORSE aggregate (but more fair selection)")
        else:
            print(f"  ➡️  Both logics give same result")
        
        # Show actual scores selected
        old_scores = [data['score'] for data in old_best_two]
        new_scores = [data['score'] for data in new_best_two]
        print(f"  📈 OLD selects scores: {old_scores} (avg: {sum(old_scores)/2:.1f}%)")
        print(f"  📈 NEW selects scores: {new_scores} (avg: {sum(new_scores)/2:.1f}%)")

def show_aggregate_impact():
    """Show how this impacts the complete aggregate calculation"""
    
    print("\n" + "=" * 60) 
    print("🏆 Complete Aggregate Impact Example")
    print("=" * 60)
    
    # Example: Student with consistent core subjects but struggling electives
    core_scores = [75, 68, 72, 70]  # Math, English, Science, Social Studies
    elective_scores = [34, 28, 31, 25, 30]  # All Grade 9, but with variation
    
    core_grades = [calculate_grade(score) for score in core_scores]
    
    print("📚 Core Subjects (consistent performance):")
    subjects = ['Math', 'English', 'Science', 'Social Studies']
    for i, (score, grade) in enumerate(zip(core_scores, core_grades)):
        grade_desc = get_grade_description(grade)
        print(f"  {subjects[i]:12} - {score}% → Grade {grade} ({grade_desc})")
    
    core_total = sum(core_grades)
    print(f"Core total: {core_total}")
    
    print(f"\n📋 Elective Subjects (all Grade 9, but with score variation):")
    elective_data = []
    for i, score in enumerate(elective_scores):
        grade = calculate_grade(score)
        grade_desc = get_grade_description(grade)
        elective_data.append({'score': score, 'grade': grade})
        print(f"  Elective {i+1:2} - {score}% → Grade {grade} ({grade_desc})")
    
    # NEW LOGIC: Select by highest scores
    sorted_electives = sorted(elective_data, key=lambda x: x['score'], reverse=True)
    best_two_new = sorted_electives[:2]
    new_elective_total = sum(data['grade'] for data in best_two_new)
    
    print(f"\n✅ NEW Logic selects:")
    print(f"  Best elective: {best_two_new[0]['score']}% (Grade {best_two_new[0]['grade']})")
    print(f"  2nd best elective: {best_two_new[1]['score']}% (Grade {best_two_new[1]['grade']})")
    print(f"  Elective total: {new_elective_total}")
    
    new_aggregate = core_total + new_elective_total
    print(f"\n🏆 Final Aggregate: {core_total} + {new_elective_total} = {new_aggregate}")
    print(f"This fairly represents the student's best efforts in elective subjects!")

if __name__ == "__main__":
    demonstrate_improved_logic()
    compare_different_scenarios()
    show_aggregate_impact()