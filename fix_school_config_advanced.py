#!/usr/bin/env python3
"""
Advanced School Config Encoding Fix
Handle UTF-8 emojis and special characters properly
"""

import os
from pathlib import Path
import codecs

def fix_school_config_advanced():
    """Fix encoding issues in school_config.py with proper UTF-8 handling"""
    print("🔧 Advanced School Config Encoding Fix")
    print("=" * 60)
    
    config_file = Path("src/config/school_config.py")
    
    # Try different encodings to read the file
    encodings_to_try = ['utf-8', 'utf-8-sig', 'cp1252', 'latin1', 'ascii']
    content = None
    used_encoding = None
    
    for encoding in encodings_to_try:
        try:
            with open(config_file, 'r', encoding=encoding) as f:
                content = f.read()
            used_encoding = encoding
            print(f"✅ Successfully read file using encoding: {encoding}")
            break
        except Exception as e:
            print(f"❌ Failed to read with {encoding}: {e}")
    
    if content is None:
        print("Failed to read file with any encoding. Trying binary approach...")
        
        # Read as binary and try to fix byte by byte
        with open(config_file, 'rb') as f:
            content_bytes = f.read()
        
        # Create backup
        backup_file = config_file.with_suffix('.py.backup_advanced')
        with open(backup_file, 'wb') as f:
            f.write(content_bytes)
        print(f"Created backup: {backup_file}")
        
        # Try to decode with error handling
        try:
            content = content_bytes.decode('utf-8', errors='replace')
            print("✅ Decoded with error replacement")
        except Exception as e:
            print(f"❌ Even error replacement failed: {e}")
            return
    
    # Clean the content
    print("\n🧹 Cleaning content...")
    
    # Replace problematic Unicode characters with safe alternatives
    replacements = {
        '🌐': '[WEBSITE]',  # Globe emoji
        '📱': '[PHONE]',    # Phone emoji
        '✉️': '[EMAIL]',    # Email emoji
        '📍': '[ADDRESS]',  # Pin emoji
        '🏫': '[SCHOOL]',   # School emoji
        '\x90': '-',        # Problematic byte
        '\x91': "'",        # Left single quote
        '\x92': "'",        # Right single quote
        '\x93': '"',        # Left double quote
        '\x94': '"',        # Right double quote
        '\x96': '-',        # En dash
        '\x97': '--',       # Em dash
        '\xa0': ' ',        # Non-breaking space
    }
    
    cleaned_content = content
    total_replacements = 0
    
    for old_char, new_char in replacements.items():
        count = cleaned_content.count(old_char)
        if count > 0:
            print(f"  Replacing {count} instances of '{old_char}' with '{new_char}'")
            cleaned_content = cleaned_content.replace(old_char, new_char)
            total_replacements += count
    
    print(f"Total replacements made: {total_replacements}")
    
    # Additional cleanup for any remaining problematic characters
    # Replace any non-ASCII characters with ASCII equivalents
    ascii_content = ""
    non_ascii_replaced = 0
    
    for char in cleaned_content:
        if ord(char) > 127:  # Non-ASCII character
            if char in '""''':  # Smart quotes
                ascii_content += '"' if char in '""' else "'"
            elif char in '–—':  # Dashes
                ascii_content += '-'
            else:
                ascii_content += '?'  # Replace with question mark
            non_ascii_replaced += 1
        else:
            ascii_content += char
    
    if non_ascii_replaced > 0:
        print(f"Replaced {non_ascii_replaced} additional non-ASCII characters")
    
    # Write the cleaned content
    try:
        with open(config_file, 'w', encoding='utf-8') as f:
            f.write(ascii_content)
        print("✅ Successfully wrote cleaned file")
        
        # Verify the file can be read back
        with open(config_file, 'r', encoding='utf-8') as f:
            test_content = f.read()
        print("✅ File verification successful - can be read as UTF-8")
        
        # Try to import it to make sure Python can parse it
        import tempfile
        import sys
        
        # Create a test script to import the config
        test_script = f'''
import sys
sys.path.insert(0, r"{os.getcwd()}")
try:
    from src.config.school_config import SchoolConfig
    print("✅ Successfully imported SchoolConfig")
    print(f"School name: {{SchoolConfig.SCHOOL_NAME}}")
except Exception as e:
    print(f"❌ Import failed: {{e}}")
'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as tmp:
            tmp.write(test_script)
            tmp_path = tmp.name
        
        # Run the test
        import subprocess
        result = subprocess.run([sys.executable, tmp_path], 
                              capture_output=True, text=True, cwd=os.getcwd())
        
        print("\nImport test result:")
        print(result.stdout)
        if result.stderr:
            print("Errors:")
            print(result.stderr)
        
        # Clean up temp file
        os.unlink(tmp_path)
        
    except Exception as e:
        print(f"❌ Error writing cleaned file: {e}")
        # Restore backup if we created one
        backup_file = config_file.with_suffix('.py.backup_advanced')
        if backup_file.exists():
            with open(backup_file, 'rb') as bf:
                backup_content = bf.read()
            with open(config_file, 'wb') as cf:
                cf.write(backup_content)
            print("Restored from backup")

def main():
    """Main function"""
    os.chdir("c:\\Users\\abeik\\OneDrive - Georgia Institute of Technology\\Desktop\\sytems students")
    fix_school_config_advanced()

if __name__ == "__main__":
    main()