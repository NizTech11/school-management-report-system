#!/usr/bin/env python3
"""
Configuration Diagnostic Tool
Helps identify and diagnose configuration file issues
"""

import os
import json
import sys

def diagnose_file(file_path):
    """Diagnose a single configuration file"""
    print(f"\n🔍 Diagnosing: {file_path}")
    print("-" * 50)
    
    if not os.path.exists(file_path):
        print("❌ File does not exist")
        return False
    
    # Check file size
    size = os.path.getsize(file_path)
    print(f"📁 File size: {size} bytes")
    
    # Try to read with different encodings
    encodings = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252']
    
    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                content = f.read()
            
            print(f"✅ Successfully read with {encoding} encoding ({len(content)} characters)")
            
            # Check for problematic characters
            problematic_chars = []
            for i, char in enumerate(content):
                char_code = ord(char)
                if char_code < 32 and char not in '\n\r\t':
                    problematic_chars.append((i, char, char_code))
            
            if problematic_chars:
                print(f"⚠️  Found {len(problematic_chars)} problematic characters:")
                for pos, char, code in problematic_chars[:10]:  # Show first 10
                    print(f"   Position {pos}: byte 0x{code:02X}")
            else:
                print("✅ No problematic control characters found")
            
            # Try to parse as JSON
            try:
                config_data = json.loads(content)
                print("✅ Valid JSON structure")
                print(f"📊 Contains {len(config_data)} top-level keys")
                
                # Show structure
                for key, value in config_data.items():
                    if isinstance(value, dict):
                        print(f"   {key}: dict with {len(value)} items")
                    elif isinstance(value, list):
                        print(f"   {key}: list with {len(value)} items")
                    else:
                        print(f"   {key}: {type(value).__name__}")
                
                return True
                
            except json.JSONDecodeError as e:
                print(f"❌ JSON parsing error: {e}")
                return False
                
        except (UnicodeDecodeError, UnicodeError) as e:
            print(f"❌ Cannot read with {encoding}: {e}")
        except Exception as e:
            print(f"❌ Unexpected error with {encoding}: {e}")
    
    return False

def main():
    """Main diagnostic function"""
    print("🏥 Configuration Diagnostic Tool")
    print("=" * 60)
    
    # Files to check
    config_files = [
        "src/config/clean_school_settings.json",
        "src/config/school_settings.json",
        "src/config/config_manager.py",
        "src/config/school_config.py"
    ]
    
    success_count = 0
    
    for file_path in config_files:
        if file_path.endswith('.json'):
            if diagnose_file(file_path):
                success_count += 1
        else:
            # For Python files, just check existence
            if os.path.exists(file_path):
                print(f"\n✅ {file_path} exists")
                success_count += 1
            else:
                print(f"\n❌ {file_path} not found")
    
    print("\n" + "=" * 60)
    print(f"📊 Summary: {success_count}/{len(config_files)} files OK")
    
    # Environment info
    print(f"\n🖥️  Python version: {sys.version}")
    print(f"🖥️  Platform: {sys.platform}")
    
    if success_count == len(config_files):
        print("\n✅ All configuration files appear to be healthy!")
        print("💡 The encoding issue should now be resolved.")
    else:
        print("\n⚠️  Some configuration files have issues.")
        print("💡 Run fix_encoding.py to attempt repairs.")

if __name__ == "__main__":
    main()