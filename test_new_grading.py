#!/usr/bin/env python3
"""
Test script for the updated grading system
"""

import sys
import os

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from services.db import calculate_grade, get_grade_description

def test_grading_system():
    """Test the updated grading system with various score ranges"""
    
    print("🧪 Testing Updated Grading System")
    print("=" * 50)
    
    # Test cases based on the new grading system
    test_cases = [
        # (score, expected_grade, expected_description)
        (100, 1, "HIGHEST"),  # Grade 1: 80% - 100%
        (95, 1, "HIGHEST"),
        (80, 1, "HIGHEST"),
        
        (79, 2, "HIGHER"),    # Grade 2: 70% - 79%
        (75, 2, "HIGHER"),
        (70, 2, "HIGHER"),
        
        (69, 3, "HIGH"),      # Grade 3: 65% - 69%
        (67, 3, "HIGH"),
        (65, 3, "HIGH"),
        
        (64, 4, "HIGH AVERAGE"),  # Grade 4: 60% - 64%
        (62, 4, "HIGH AVERAGE"),
        (60, 4, "HIGH AVERAGE"),
        
        (59, 5, "AVERAGE"),   # Grade 5: 55% - 59%
        (57, 5, "AVERAGE"),
        (55, 5, "AVERAGE"),
        
        (54, 6, "LOW AVERAGE"),  # Grade 6: 50% - 54%
        (52, 6, "LOW AVERAGE"),
        (50, 6, "LOW AVERAGE"),
        
        (49, 7, "LOW"),       # Grade 7: 45% - 49%
        (47, 7, "LOW"),
        (45, 7, "LOW"),
        
        (44, 8, "LOWER"),     # Grade 8: 35% - 44%
        (40, 8, "LOWER"),
        (35, 8, "LOWER"),
        
        (34, 9, "LOWEST"),    # Grade 9: 0% - 34%
        (20, 9, "LOWEST"),
        (10, 9, "LOWEST"),
        (0, 9, "LOWEST"),
    ]
    
    print("Testing grade calculations...")
    print("Score -> Grade | Description | Expected")
    print("-" * 45)
    
    all_passed = True
    
    for score, expected_grade, expected_description in test_cases:
        actual_grade = calculate_grade(score)
        actual_description = get_grade_description(actual_grade)
        
        status = "✅ PASS" if (actual_grade == expected_grade and actual_description == expected_description) else "❌ FAIL"
        
        if status == "❌ FAIL":
            all_passed = False
        
        print(f"{score:3}% -> Grade {actual_grade} | {actual_description:12} | {status}")
    
    print("\n" + "=" * 50)
    
    if all_passed:
        print("🎉 All tests passed! The grading system is working correctly.")
    else:
        print("⚠️  Some tests failed. Please check the implementation.")
    
    # Print the grade scale summary
    print("\n📊 New Grading Scale Summary:")
    print("-" * 30)
    for grade in range(1, 10):
        desc = get_grade_description(grade)
        if grade == 1:
            range_text = "80% - 100%"
        elif grade == 2:
            range_text = "70% - 79%"
        elif grade == 3:
            range_text = "65% - 69%"
        elif grade == 4:
            range_text = "60% - 64%"
        elif grade == 5:
            range_text = "55% - 59%"
        elif grade == 6:
            range_text = "50% - 54%"
        elif grade == 7:
            range_text = "45% - 49%"
        elif grade == 8:
            range_text = "35% - 44%"
        elif grade == 9:
            range_text = "0% - 34%"
        
        print(f"Grade {grade}: {range_text:11} - {desc}")
    
    return all_passed

def main():
    try:
        test_grading_system()
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return False

if __name__ == "__main__":
    main()