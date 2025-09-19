#!/usr/bin/env python3
"""
Encoding Fix Utility
This script fixes encoding issues in configuration files that might contain problematic bytes like 0x90
"""

import os
import json
import shutil
from pathlib import Path

def clean_file_content(content):
    """Clean content of problematic characters"""
    if not isinstance(content, str):
        return content
    
    # Remove the specific problematic byte 0x90 and other control characters
    cleaned = content.replace('\x90', '')  # Main culprit
    
    # Remove other potentially problematic control characters
    problem_chars = [
        '\x80', '\x81', '\x82', '\x83', '\x84', '\x85', '\x86', '\x87',
        '\x88', '\x89', '\x8a', '\x8b', '\x8c', '\x8d', '\x8e', '\x8f',
        '\x90', '\x91', '\x92', '\x93', '\x94', '\x95', '\x96', '\x97',
        '\x98', '\x99', '\x9a', '\x9b', '\x9c', '\x9d', '\x9e', '\x9f'
    ]
    
    for char in problem_chars:
        cleaned = cleaned.replace(char, '')
    
    # Keep only printable characters plus essential whitespace
    cleaned = ''.join(char for char in cleaned if ord(char) >= 32 or char in '\n\r\t')
    
    return cleaned

def fix_json_file(file_path):
    """Fix encoding issues in a JSON file"""
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return False
    
    print(f"Processing: {file_path}")
    
    # Try multiple encodings
    encodings = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252', 'ascii']
    
    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                content = f.read()
            
            print(f"  Successfully read with {encoding} encoding")
            
            # Clean the content
            cleaned_content = clean_file_content(content)
            
            # Try to parse as JSON
            try:
                config_data = json.loads(cleaned_content)
                print(f"  JSON is valid after cleaning")
                
                # Create backup
                backup_path = file_path + '.backup'
                shutil.copy2(file_path, backup_path)
                print(f"  Created backup: {backup_path}")
                
                # Write cleaned version
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(config_data, f, indent=4, ensure_ascii=True)
                
                print(f"  ✅ Successfully fixed {file_path}")
                return True
                
            except json.JSONDecodeError as e:
                print(f"  JSON parsing failed with {encoding}: {e}")
                continue
                
        except (UnicodeDecodeError, UnicodeError) as e:
            print(f"  Failed to read with {encoding}: {e}")
            continue
        except Exception as e:
            print(f"  Unexpected error with {encoding}: {e}")
            continue
    
    print(f"  ❌ Could not fix {file_path}")
    return False

def main():
    """Main function to fix encoding issues"""
    print("🔧 Encoding Fix Utility")
    print("=" * 50)
    
    # Define paths to check
    config_dir = Path("src/config")
    files_to_check = [
        config_dir / "clean_school_settings.json",
        config_dir / "school_settings.json",
    ]
    
    # Add any other JSON files in config directory
    if config_dir.exists():
        for json_file in config_dir.glob("*.json"):
            if json_file not in files_to_check:
                files_to_check.append(json_file)
    
    print(f"Found {len(files_to_check)} files to check")
    print()
    
    fixed_count = 0
    for file_path in files_to_check:
        if file_path.exists():
            if fix_json_file(str(file_path)):
                fixed_count += 1
            print()
    
    print("=" * 50)
    print(f"✅ Fixed {fixed_count} files")
    print("🔄 Please restart your application and try again")

if __name__ == "__main__":
    main()