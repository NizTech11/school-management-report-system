#!/usr/bin/env python3
"""
Template Editor Logo Feature Verification
"""

import os
import json
from pathlib import Path

def verify_template_editor_logo_features():
    """Verify that logo features are properly integrated"""
    print("🔍 Template Editor Logo Feature Verification")
    print("=" * 60)
    
    # Check template editor file
    template_file = Path("src/pages/10_Clean_Template_Editor.py")
    
    if not template_file.exists():
        print("❌ Template editor file not found!")
        return
    
    # Read the template editor content
    with open(template_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for logo-related features
    logo_features = [
        ("Logo File Path input field", "Logo File Path"),
        ("Show Logo checkbox", "Show Logo in Reports"),
        ("Logo validation", "file_ext in ['.png', '.jpg', '.jpeg', '.gif']"),
        ("Logo directory creation", "Create Logo Directory"),
        ("Logo instructions", "Step-by-Step Logo Setup"),
        ("Logo preview in config summary", "Logo Path"),
        ("Logo display settings", "Logo Display Settings")
    ]
    
    print("📋 Logo Feature Checklist:")
    all_present = True
    
    for feature_name, search_text in logo_features:
        if search_text in content:
            print(f"   ✅ {feature_name}")
        else:
            print(f"   ❌ {feature_name} - MISSING")
            all_present = False
    
    # Check current configuration
    config_file = Path("src/config/clean_school_settings.json")
    
    if config_file.exists():
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            print(f"\n📊 Current Logo Configuration:")
            print(f"   Logo Path: {config.get('logo_path', 'Not set')}")
            print(f"   Show Logo: {config.get('show_logo', False)}")
            
        except Exception as e:
            print(f"\n❌ Error reading config: {e}")
    
    # Check if logo directory exists
    logo_dir = Path("assets/logos")
    
    if logo_dir.exists():
        logo_files = list(logo_dir.glob("*.png")) + list(logo_dir.glob("*.jpg")) + list(logo_dir.glob("*.jpeg")) + list(logo_dir.glob("*.gif"))
        print(f"\n📁 Logo Directory Status:")
        print(f"   Directory exists: ✅ {logo_dir.absolute()}")
        print(f"   Logo files found: {len(logo_files)}")
        
        if logo_files:
            print(f"   Available logos:")
            for logo_file in logo_files:
                print(f"     • {logo_file.name}")
        else:
            print(f"   💡 No logo files found. Copy your logo to: {logo_dir.absolute()}")
    else:
        print(f"\n📁 Logo Directory Status:")
        print(f"   Directory exists: ❌ {logo_dir.absolute()}")
        print(f"   💡 Use 'Create Logo Directory' button in Template Editor to create it")
    
    print(f"\n🎯 SUMMARY:")
    
    if all_present:
        print("✅ All logo features are properly integrated in Template Editor!")
        print("\n🚀 HOW TO USE:")
        print("1. Open Template Editor (📝 Report Template Editor)")
        print("2. Go to '🏫 School Info' tab")
        print("3. Scroll down to '🎨 School Logo Configuration' section")
        print("4. Set your logo file path and enable 'Show Logo in Reports'")
        print("5. Save configuration")
        print("6. Generate a report to see your logo!")
    else:
        print("❌ Some logo features are missing. Please check the implementation.")
    
    print(f"\n📖 Next Steps:")
    print("1. Start your Streamlit app: streamlit run src/app.py")
    print("2. Navigate to Template Editor")
    print("3. Look for the School Logo Configuration section")

def main():
    """Main function"""
    os.chdir("c:\\Users\\abeik\\OneDrive - Georgia Institute of Technology\\Desktop\\sytems students")
    verify_template_editor_logo_features()

if __name__ == "__main__":
    main()