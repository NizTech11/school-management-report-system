#!/usr/bin/env python3
"""Test the grading system"""

from src.services.db import calculate_grade, get_grade_description

def test_grading_system():
    """Test grade calculations for different score ranges"""
    
    test_scores = [
        (95, 1, "Excellent"),
        (85, 2, "Very Good"), 
        (75, 3, "Good"),
        (65, 4, "Satisfactory"),
        (55, 5, "Fair"),
        (45, 6, "Poor"),
        (35, 7, "Very Poor"),
        (25, 8, "Weak"),
        (15, 9, "Very Weak/Failed"),
        (5, 9, "Very Weak/Failed"),
        (0, 9, "Very Weak/Failed"),
        (100, 1, "Excellent"),
        (90, 1, "Excellent"),
        (89.9, 2, "Very Good"),
        (80, 2, "Very Good"),
        (79.9, 3, "Good")
    ]
    
    print("Testing Primary School Grading System")
    print("=" * 50)
    print("Score Range | Grade | Description")
    print("-" * 35)
    
    all_passed = True
    
    for score, expected_grade, expected_desc in test_scores:
        try:
            grade = calculate_grade(score)
            desc = get_grade_description(grade)
            
            status = "✅" if grade == expected_grade and expected_desc in desc else "❌"
            if grade != expected_grade or expected_desc not in desc:
                all_passed = False
            
            print(f"{score:5.1f}%     | {grade}     | {desc} {status}")
            
        except Exception as e:
            print(f"{score:5.1f}%     | ERROR: {e} ❌")
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 All grading tests passed!")
    else:
        print("⚠️ Some grading tests failed!")
    
    # Test edge cases
    print("\nTesting Edge Cases:")
    print("-" * 20)
    
    try:
        calculate_grade(-1)
        print("❌ Should reject negative scores")
        all_passed = False
    except ValueError:
        print("✅ Correctly rejects negative scores")
    
    try:
        calculate_grade(101)
        print("❌ Should reject scores > 100")
        all_passed = False
    except ValueError:
        print("✅ Correctly rejects scores > 100")
    
    print("\n" + "=" * 50)
    final_status = "🎉 All tests passed!" if all_passed else "⚠️ Some tests failed!"
    print(final_status)

if __name__ == "__main__":
    test_grading_system()