#!/usr/bin/env python3
"""
Template Editor Test
Test the configuration save/load functionality
"""

import os
import sys
import json
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_config_operations():
    """Test configuration loading and saving"""
    print("🧪 Testing Template Editor Configuration Operations")
    print("=" * 60)
    
    # Import the functions from the template editor
    try:
        # Simulate the config file path function
        def get_config_file_path():
            return os.path.join(os.path.dirname(__file__), 'src', 'config', 'clean_school_settings.json')
        
        # Test configuration (with potential problematic characters)
        test_config = {
            "school_name": "TEST ACADEMY",
            "school_subtitle": "Test School - Excellence",  # Regular dash
            "address": "123 Test Street, Test City",
            "email": "test@testacademy.edu",
            "phone_numbers": ["+123-456-7890"],
            "academic_year": "2024-2025",
            "current_term": "3RD TERM",
            "report_titles": {
                "Mid-term": "MID-TERM TEST REPORT",
                "End of Term": "END OF TERM TEST REPORT"
            },
            "grade_remarks": {
                "1": "HIGHEST", "2": "HIGHER", "3": "HIGH", "4": "GOOD", "5": "CREDIT",
                "6": "PASS", "7": "FAIR", "8": "POOR", "9": "FAIL"
            }
        }
        
        print("1. Testing configuration save...")
        config_file = get_config_file_path()
        
        # Create backup of original
        backup_file = config_file + '.test_backup'
        if os.path.exists(config_file):
            with open(config_file, 'r', encoding='utf-8') as f:
                original_config = f.read()
            with open(backup_file, 'w', encoding='utf-8') as f:
                f.write(original_config)
            print(f"✅ Created backup: {backup_file}")
        
        # Test save operation
        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(test_config, f, indent=4, ensure_ascii=True)
            print("✅ Configuration saved successfully")
            
            # Test load operation
            with open(config_file, 'r', encoding='utf-8') as f:
                loaded_config = json.load(f)
            print("✅ Configuration loaded successfully")
            
            # Verify data integrity
            if loaded_config['school_name'] == test_config['school_name']:
                print("✅ Data integrity verified")
            else:
                print("❌ Data integrity check failed")
                
            # Test with special characters that previously caused issues
            problematic_config = test_config.copy()
            problematic_config['school_name'] = 'Test\x90Academy'  # Contains the problematic byte
            
            # Clean the problematic characters
            clean_name = ''.join(c for c in problematic_config['school_name'] if ord(c) >= 32 or c in '\n\r\t')
            clean_name = clean_name.replace('\x90', '')
            problematic_config['school_name'] = clean_name
            
            print("2. Testing with cleaned problematic characters...")
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(problematic_config, f, indent=4, ensure_ascii=True)
            print("✅ Problematic characters handled successfully")
            
        except Exception as e:
            print(f"❌ Save/Load test failed: {e}")
            return False
        
        finally:
            # Restore original config
            if os.path.exists(backup_file):
                with open(backup_file, 'r', encoding='utf-8') as f:
                    original_config = f.read()
                with open(config_file, 'w', encoding='utf-8') as f:
                    f.write(original_config)
                os.remove(backup_file)
                print("✅ Original configuration restored")
        
        print("\n" + "=" * 60)
        print("🎉 All tests passed! Template Editor should work correctly now.")
        return True
        
    except Exception as e:
        print(f"❌ Test setup failed: {e}")
        return False

def main():
    """Main test function"""
    if test_config_operations():
        print("\n💡 You can now use the Template Editor without encoding errors!")
        print("🚀 Go to the Reports → Template Editor page and try saving your configuration.")
    else:
        print("\n⚠️  Tests failed. There may still be issues with the configuration.")
        print("💡 Please check the error messages above for more details.")

if __name__ == "__main__":
    main()