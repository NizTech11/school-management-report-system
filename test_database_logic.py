#!/usr/bin/env python3
"""
Test the improved aggregate calculation logic with actual database scenarios
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_with_mock_data():
    """Test the improved logic with mock student data"""
    
    print("🧪 Testing Improved Logic with Mock Student Data")
    print("=" * 55)
    
    # Mock elective subjects data (subject_id: score)
    test_cases = [
        {
            "name": "Student A - All Grade 9 Electives",
            "elective_scores": {1: 34, 2: 28, 3: 31, 4: 25, 5: 30},  # All Grade 9
            "description": "Student struggling in all electives but with score variation"
        },
        {
            "name": "Student B - Mixed Elective Performance", 
            "elective_scores": {1: 85, 2: 72, 3: 45, 4: 25, 5: 60},
            "description": "Student with good and poor elective performance"
        },
        {
            "name": "Student C - Near Grade Boundaries",
            "elective_scores": {1: 80, 2: 79, 3: 69, 4: 68, 5: 59},
            "description": "Student with scores near grade boundaries"
        },
        {
            "name": "Student D - Only 2 Electives (Edge Case)",
            "elective_scores": {1: 32, 2: 29},  # Exactly 2 electives, both Grade 9
            "description": "Student with exactly 2 elective subjects"
        }
    ]
    
    # Import the functions we need
    from services.db import calculate_grade, get_grade_description
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n📊 Test Case {i}: {case['name']}")
        print(f"Description: {case['description']}")
        print("-" * 50)
        
        # Simulate the improved logic
        elective_score_data = []
        for subject_id, score in case['elective_scores'].items():
            elective_score_data.append({
                'subject_id': subject_id,
                'score': score,
                'grade': calculate_grade(score)
            })
        
        # Show all elective performance
        print("All elective subjects:")
        for data in elective_score_data:
            grade_desc = get_grade_description(data['grade'])
            print(f"  Subject {data['subject_id']}: {data['score']:2}% → Grade {data['grade']} ({grade_desc})")
        
        # Apply the NEW improved logic
        elective_score_data.sort(key=lambda x: x['score'], reverse=True)
        
        if len(elective_score_data) >= 2:
            best_two = elective_score_data[:2]
            best_elective_grades = [data['grade'] for data in best_two]
            
            print(f"\n✅ Best two subjects selected (by highest scores):")
            print(f"  1st: Subject {best_two[0]['subject_id']} - {best_two[0]['score']}% (Grade {best_two[0]['grade']})")
            print(f"  2nd: Subject {best_two[1]['subject_id']} - {best_two[1]['score']}% (Grade {best_two[1]['grade']})")
            print(f"  Grade sum: {sum(best_elective_grades)}")
            print(f"  Average score: {(best_two[0]['score'] + best_two[1]['score']) / 2:.1f}%")
        else:
            print("❌ Insufficient elective subjects (need at least 2)")
        
        # Show what OLD logic would have done
        old_logic_grades = [data['grade'] for data in elective_score_data]
        old_logic_grades.sort()  # Sort by grade (ascending)
        if len(old_logic_grades) >= 2:
            old_best_two = old_logic_grades[:2]
            print(f"\n🔹 For comparison, OLD logic would select grades: {old_best_two} (sum: {sum(old_best_two)})")
            
            # Find which subjects these grades correspond to
            old_subjects = []
            used_indices = []
            for grade in old_best_two:
                for j, data in enumerate(elective_score_data):
                    if data['grade'] == grade and j not in used_indices:
                        old_subjects.append(f"Subject {data['subject_id']} ({data['score']}%)")
                        used_indices.append(j)
                        break
            print(f"    Corresponding to: {', '.join(old_subjects)}")

def demonstrate_fairness():
    """Demonstrate why the new logic is more fair"""
    
    print("\n" + "=" * 55)
    print("⚖️ Why the Improved Logic is More Fair")
    print("=" * 55)
    
    from services.db import calculate_grade, get_grade_description
    
    print("🎯 Fairness Principle:")
    print("Students should be rewarded for their BEST ACTUAL PERFORMANCE,")
    print("not just the subjects that happen to fall into certain grade brackets.")
    print()
    
    # Extreme example to show the difference
    print("📋 Extreme Example - Student with Very Different Elective Performance:")
    elective_data = [
        {'subject': 'Art', 'score': 34.9, 'grade': calculate_grade(34.9)},      # 34.9% = Grade 9
        {'subject': 'Music', 'score': 10.0, 'grade': calculate_grade(10.0)},    # 10.0% = Grade 9
        {'subject': 'PE', 'score': 5.0, 'grade': calculate_grade(5.0)},         # 5.0% = Grade 9
        {'subject': 'ICT', 'score': 1.0, 'grade': calculate_grade(1.0)},        # 1.0% = Grade 9
    ]
    
    for data in elective_data:
        grade_desc = get_grade_description(data['grade'])
        print(f"  {data['subject']:5} - {data['score']:4.1f}% → Grade {data['grade']} ({grade_desc})")
    
    print(f"\n❌ OLD LOGIC Problems:")
    print(f"  • All subjects have Grade 9, so system picks any 2")
    print(f"  • Could pick Art (34.9%) and Music (10.0%) - average 22.45%")
    print(f"  • Could pick ICT (1.0%) and PE (5.0%) - average 3.0%")
    print(f"  • This creates unfair randomness in aggregate calculation!")
    
    # Apply new logic
    sorted_data = sorted(elective_data, key=lambda x: x['score'], reverse=True)
    best_two = sorted_data[:2]
    
    print(f"\n✅ NEW LOGIC Benefits:")
    print(f"  • Always selects the subjects with highest actual scores")
    print(f"  • Selects {best_two[0]['subject']} ({best_two[0]['score']}%) and {best_two[1]['subject']} ({best_two[1]['score']}%)")
    print(f"  • Average score: {(best_two[0]['score'] + best_two[1]['score']) / 2:.1f}%")
    print(f"  • Fair and consistent reward for best performance")
    print(f"  • Students benefit from their stronger elective subjects")
    
    print(f"\n🏆 Impact on Student Motivation:")
    print(f"  • Students know their best efforts in electives will count")
    print(f"  • Encourages students to focus on their strongest elective areas")
    print(f"  • More accurate representation of student abilities")
    print(f"  • Removes unfair randomness from aggregate calculation")

if __name__ == "__main__":
    test_with_mock_data()
    demonstrate_fairness()