#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script to validate score validation functionality
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from services.db import validate_and_normalize_score, validate_score

def test_validation():
    print("Testing score validation functionality...")
    print("=" * 50)
    
    # Test cases
    test_cases = [
        # Valid scores
        (0, True, "Minimum valid score"),
        (50.5, True, "Mid-range score"), 
        (100, True, "Maximum valid score"),
        (99.9, True, "Near maximum score"),
        (0.1, True, "Near minimum score"),
        
        # Invalid scores  
        (-1, False, "Negative score"),
        (-0.1, False, "Small negative score"),
        (100.1, False, "Score above 100"),
        (150, False, "High invalid score"),
        (200, False, "Very high invalid score")
    ]
    
    print("Testing validate_score function:")
    print("-" * 30)
    
    for score, expected, description in test_cases:
        result = validate_score(score)
        status = "PASS" if result == expected else "FAIL"
        print(f"{status} {description}: {score}% -> {result}")
    
    print("\nTesting validate_and_normalize_score function:")
    print("-" * 45)
    
    for score, expected, description in test_cases:
        try:
            result = validate_and_normalize_score(score)
            if expected:
                status = "PASS"
                print(f"{status} {description}: {score}% -> {result}%")
            else:
                status = "FAIL (Should have raised ValueError)"
                print(f"{status} {description}: {score}% -> {result}%")
        except ValueError as e:
            if not expected:
                status = "PASS"
                print(f"{status} {description}: {score}% -> Error: {str(e)}")
            else:
                status = "FAIL (Unexpected ValueError)"
                print(f"{status} {description}: {score}% -> Unexpected error: {str(e)}")
        except Exception as e:
            status = "FAIL (Unexpected exception)"
            print(f"{status} {description}: {score}% -> Unexpected exception: {str(e)}")
    
    print("\n" + "=" * 50)
    print("Validation test completed!")
    print("The enhanced validation should now:")
    print("• Accept scores between 0 and 100 (inclusive)")
    print("• Reject negative scores with clear error message")
    print("• Reject scores above 100 with clear error message")
    print("• Show specific error messages in the forms interface")

if __name__ == "__main__":
    test_validation()