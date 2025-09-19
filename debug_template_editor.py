#!/usr/bin/env python3
"""
Debug Template Editor Issues
Help identify which file is causing the encoding problem
"""

import os
import json
import sys
from pathlib import Path

def debug_template_editor_access():
    """Debug which template editor files exist and their contents"""
    print("🔍 Template Editor Debug Analysis")
    print("=" * 60)
    
    base_path = Path("src/pages")
    template_files = list(base_path.glob("*Template_Editor*.py")) + list(base_path.glob("*template_editor*.py"))
    
    print(f"Found {len(template_files)} template editor files:")
    for file in template_files:
        print(f"  📄 {file}")
        # Check file size and modification time
        stat = file.stat()
        print(f"     Size: {stat.st_size} bytes")
        print(f"     Modified: {stat.st_mtime}")
        print()
    
    # Check if the correct one is being referenced in app.py
    app_py = Path("src/app.py")
    if app_py.exists():
        with open(app_py, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Find template editor references
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if 'Template_Editor' in line or 'template_editor' in line:
                print(f"app.py line {i+1}: {line.strip()}")
        print()
    
    # Check config files that might contain the problematic byte
    config_dir = Path("src/config")
    config_files = list(config_dir.glob("*.py")) + list(config_dir.glob("*.json"))
    
    print("Configuration files:")
    for file in config_files:
        print(f"  📄 {file}")
        
        try:
            with open(file, 'rb') as f:
                content_bytes = f.read()
            
            # Check for byte 0x90
            if b'\x90' in content_bytes:
                positions = []
                pos = 0
                while True:
                    pos = content_bytes.find(b'\x90', pos)
                    if pos == -1:
                        break
                    positions.append(pos)
                    pos += 1
                
                print(f"    ⚠️  Contains {len(positions)} instances of byte 0x90 at positions: {positions[:10]}...")
            else:
                print(f"    ✅ Clean (no problematic bytes)")
                
        except Exception as e:
            print(f"    ❌ Error reading file: {e}")
        
        print()

def test_json_config_save():
    """Test if JSON config saving works without errors"""
    print("🧪 Testing JSON Config Save Operation")
    print("=" * 60)
    
    config_file = Path("src/config/clean_school_settings.json")
    
    # Test data that might contain problematic characters
    test_configs = [
        {
            "school_name": "TEST ACADEMY",
            "school_subtitle": "Excellence in Education",
            "address": "123 Test Street",
            "email": "test@school.edu"
        },
        {
            "school_name": "TEST ACADEMY – DASH TEST",  # em dash
            "school_subtitle": "Excellence in Education",
            "address": "123 Test Street",
            "email": "test@school.edu"
        }
    ]
    
    for i, test_config in enumerate(test_configs):
        print(f"Test {i+1}: {test_config['school_name']}")
        
        try:
            # Test writing
            test_file = config_file.parent / f"test_config_{i+1}.json"
            with open(test_file, 'w', encoding='utf-8') as f:
                json.dump(test_config, f, indent=4, ensure_ascii=True)
            
            # Test reading back
            with open(test_file, 'r', encoding='utf-8') as f:
                loaded_config = json.load(f)
            
            print(f"  ✅ Save/Load successful")
            
            # Clean up
            test_file.unlink()
            
        except Exception as e:
            print(f"  ❌ Error: {e}")
        
        print()

def main():
    """Main debug function"""
    os.chdir("c:\\Users\\abeik\\OneDrive - Georgia Institute of Technology\\Desktop\\sytems students")
    
    debug_template_editor_access()
    test_json_config_save()
    
    print("💡 Recommendations:")
    print("1. Make sure you're accessing the correct template editor URL")
    print("2. Clear your browser cache and restart Streamlit")
    print("3. Check if any config files still contain problematic bytes")
    print("4. Verify you're logged in with sufficient permissions")

if __name__ == "__main__":
    main()