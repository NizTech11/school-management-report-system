#!/usr/bin/env python3
"""
School Logo Configuration Tool
Easily set up your school logo for reports
"""

import os
import json
from pathlib import Path

def configure_school_logo():
    """Interactive tool to configure school logo"""
    print("🎨 School Logo Configuration Tool")
    print("=" * 60)
    
    # Load current configuration
    config_file = Path("src/config/clean_school_settings.json")
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        print("✅ Current configuration loaded")
    except Exception as e:
        print(f"❌ Error loading config: {e}")
        return
    
    # Show current logo settings
    print(f"\n📊 CURRENT LOGO SETTINGS:")
    print(f"   Logo Path: {config.get('logo_path', 'Not set')}")
    print(f"   Show Logo: {config.get('show_logo', False)}")
    
    print(f"\n🎯 TO ENABLE SCHOOL LOGO:")
    print("1. Save your logo file (PNG, JPEG, or GIF)")
    print("2. Run this configuration")
    print("3. Access Template Editor to enable logo display")
    
    # Create assets/logos directory
    logos_dir = Path("assets/logos")
    logos_dir.mkdir(parents=True, exist_ok=True)
    print(f"\n📁 Logo directory created: {logos_dir.absolute()}")
    
    # Look for existing logo files
    logo_files = []
    for pattern in ['*.png', '*.jpg', '*.jpeg', '*.gif']:
        logo_files.extend(list(logos_dir.glob(pattern)))
    
    if logo_files:
        print(f"\n🔍 FOUND EXISTING LOGO FILES:")
        for i, logo_file in enumerate(logo_files, 1):
            print(f"   {i}. {logo_file.name}")
        
        # Create example configuration for the first logo found
        example_logo = logo_files[0]
        example_config = {
            "logo_path": str(example_logo.absolute()),
            "show_logo": True
        }
        
        print(f"\n📝 EXAMPLE CONFIGURATION FOR {example_logo.name}:")
        print(json.dumps(example_config, indent=2))
        
        # Create a sample config file
        sample_file = Path("sample_logo_config.json")
        with open(sample_file, 'w') as f:
            json.dump(example_config, f, indent=2)
        print(f"\n💾 Sample config saved to: {sample_file.absolute()}")
        
    else:
        print(f"\n📄 NO LOGO FILES FOUND")
        print(f"   Copy your school logo to: {logos_dir.absolute()}")
        print(f"   Supported formats: PNG, JPEG, GIF")
    
    print(f"\n🔧 HOW TO APPLY THE CONFIGURATION:")
    print("1. Navigate to Template Editor in your app")
    print("2. In the 'School Information' section:")
    print("   - Set 'Logo File Path' to your logo file location")
    print("   - Enable 'Show Logo in Reports'")
    print("3. Save the configuration")
    print("4. Generate a report to see your logo!")
    
    print(f"\n💡 LOGO SPECIFICATIONS:")
    print("   - Recommended size: 300x300 pixels")
    print("   - File formats: PNG (best), JPEG, GIF") 
    print("   - Keep file size under 1MB")
    print("   - Square or rectangular logos work best")
    
    # Show where logo will appear
    print(f"\n🎯 LOGO APPEARS IN:")
    print("   ✓ Student report cards (PDF)")
    print("   ✓ Class reports")
    print("   ✓ Mark sheets")
    print("   ✓ All generated documents")
    
    # Create a simple logo uploader instruction
    instructions_file = Path("logo_setup_instructions.txt")
    with open(instructions_file, 'w') as f:
        f.write(f"""SCHOOL LOGO SETUP INSTRUCTIONS
===============================

1. PREPARE YOUR LOGO:
   - Save as PNG, JPEG, or GIF format
   - Recommended size: 300x300 pixels
   - Keep file size under 1MB

2. SAVE LOGO FILE:
   - Copy your logo to: {logos_dir.absolute()}
   - Name it something like: school_logo.png

3. CONFIGURE IN TEMPLATE EDITOR:
   - Open Template Editor in your app
   - Find "School Information" section
   - Set "Logo File Path" to: {logos_dir.absolute()}/your_logo_name.png
   - Enable "Show Logo in Reports"
   - Click "Save Configuration"

4. TEST:
   - Generate any report (student marks, class report, etc.)
   - Your logo should appear at the top of the PDF

TROUBLESHOOTING:
- Logo not showing? Check the file path is correct
- Logo too big/small? Adjust size settings in Template Editor
- File format issues? Try PNG format for best compatibility

Current Template Editor URL: http://localhost:8501/10_Clean_Template_Editor
""")
    
    print(f"\n📋 Complete instructions saved to: {instructions_file.absolute()}")

def main():
    """Main function"""
    os.chdir("c:\\Users\\abeik\\OneDrive - Georgia Institute of Technology\\Desktop\\sytems students")
    configure_school_logo()

if __name__ == "__main__":
    main()