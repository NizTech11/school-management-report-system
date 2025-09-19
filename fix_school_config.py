#!/usr/bin/env python3
"""
Fix School Config Encoding Issues
"""

import os
from pathlib import Path

def fix_school_config_encoding():
    """Fix encoding issues in school_config.py"""
    print("🔧 Fixing School Config Encoding Issues")
    print("=" * 60)
    
    config_file = Path("src/config/school_config.py")
    
    # Read file and identify problematic bytes
    with open(config_file, 'rb') as f:
        content_bytes = f.read()
    
    print(f"Original file size: {len(content_bytes)} bytes")
    
    # Find position 2977
    if len(content_bytes) > 2977:
        print(f"Byte at position 2977: 0x{content_bytes[2977]:02x}")
        
        # Show context around the problematic byte
        start = max(0, 2977 - 50)
        end = min(len(content_bytes), 2977 + 50)
        context = content_bytes[start:end]
        
        print(f"Context around position 2977:")
        print(f"Bytes {start}-{end}:")
        print(context)
        
        # Try to decode and show text context
        try:
            text_context = context.decode('utf-8', errors='replace')
            print(f"\nText context:")
            print(repr(text_context))
        except Exception as e:
            print(f"Error decoding context: {e}")
    
    # Create backup
    backup_file = config_file.with_suffix('.py.backup')
    with open(backup_file, 'wb') as f:
        f.write(content_bytes)
    print(f"Created backup: {backup_file}")
    
    # Fix encoding by replacing problematic bytes
    # Common problematic bytes and their ASCII replacements
    replacements = {
        b'\x90': b'-',  # Replace with regular dash
        b'\x91': b"'",  # Left single quotation mark
        b'\x92': b"'",  # Right single quotation mark  
        b'\x93': b'"',  # Left double quotation mark
        b'\x94': b'"',  # Right double quotation mark
        b'\x96': b'-',  # En dash
        b'\x97': b'--', # Em dash
        b'\xa0': b' ',  # Non-breaking space
    }
    
    fixed_content = content_bytes
    replacements_made = 0
    
    for bad_byte, replacement in replacements.items():
        count = fixed_content.count(bad_byte)
        if count > 0:
            print(f"Replacing {count} instances of {bad_byte} with {replacement}")
            fixed_content = fixed_content.replace(bad_byte, replacement)
            replacements_made += count
    
    print(f"Total replacements made: {replacements_made}")
    
    # Write fixed content
    with open(config_file, 'wb') as f:
        f.write(fixed_content)
    
    # Verify the fix
    with open(config_file, 'r', encoding='utf-8') as f:
        try:
            text_content = f.read()
            print("✅ File successfully reads as UTF-8")
            print(f"Fixed file size: {len(fixed_content)} bytes")
        except Exception as e:
            print(f"❌ Error reading fixed file: {e}")
            # Restore backup
            with open(backup_file, 'rb') as bf:
                backup_content = bf.read()
            with open(config_file, 'wb') as cf:
                cf.write(backup_content)
            print("Restored from backup")

def main():
    """Main function"""
    os.chdir("c:\\Users\\abeik\\OneDrive - Georgia Institute of Technology\\Desktop\\sytems students")
    fix_school_config_encoding()

if __name__ == "__main__":
    main()