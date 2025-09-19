#!/usr/bin/env python3
"""
Logo Setup Guide for School Reports
"""

import os
from pathlib import Path

def setup_school_logo():
    """Guide for setting up school logo"""
    print("📖 School Logo Setup Guide")
    print("=" * 60)
    
    # Create logos directory if it doesn't exist
    logos_dir = Path("assets/logos")
    logos_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"✅ Created logos directory: {logos_dir.absolute()}")
    
    print("\n🎯 STEPS TO ADD YOUR SCHOOL LOGO:")
    print("\n1. **Prepare Your Logo File:**")
    print("   - Supported formats: PNG, JPEG, GIF")
    print("   - Recommended size: 300x300 pixels or similar")
    print("   - Square or rectangular logos work best")
    print("   - Keep file size under 1MB for best performance")
    
    print(f"\n2. **Save Logo to Assets Folder:**")
    print(f"   - Copy your logo file to: {logos_dir.absolute()}")
    print("   - Suggested names: 'school_logo.png', 'logo.jpg', etc.")
    
    print("\n3. **Update Configuration:**")
    print("   Edit src/config/school_config.py and change:")
    print(f"   LOGO_PATH = \"{logos_dir.absolute()}\\your_logo_file.png\"")
    print("   SHOW_LOGO = True")
    
    print("\n4. **Logo Display Settings:**")
    print("   - LOGO_WIDTH = 60   # Logo width in points")
    print("   - LOGO_HEIGHT = 60  # Logo height in points")
    print("   - Adjust these values to resize your logo")
    
    print("\n📝 EXAMPLE CONFIGURATION:")
    print(f"   LOGO_PATH = \"{logos_dir.absolute()}\\school_logo.png\"")
    print("   LOGO_WIDTH = 80")
    print("   LOGO_HEIGHT = 80") 
    print("   SHOW_LOGO = True")
    
    print("\n🔍 WHERE LOGO APPEARS:")
    print("   - PDF reports (at the top of each page)")
    print("   - Student mark sheets")
    print("   - Class reports")
    print("   - All generated documents")
    
    print("\n⚠️ TROUBLESHOOTING:")
    print("   - Logo not showing? Check file path is correct")
    print("   - Logo too big/small? Adjust LOGO_WIDTH/LOGO_HEIGHT")
    print("   - File format issues? Try PNG format")
    print("   - Path issues? Use full absolute path")
    
    # Create a sample logo configuration
    sample_config = f"""
# Example Logo Configuration (add to school_config.py)

LOGO_PATH = "{logos_dir.absolute()}\\school_logo.png"
LOGO_WIDTH = 70
LOGO_HEIGHT = 70
SHOW_LOGO = True
"""
    
    config_file = Path("logo_config_example.txt")
    with open(config_file, 'w') as f:
        f.write(sample_config.strip())
    
    print(f"\n📄 Sample configuration saved to: {config_file.absolute()}")

def main():
    """Main function"""
    os.chdir("c:\\Users\\abeik\\OneDrive - Georgia Institute of Technology\\Desktop\\sytems students")
    setup_school_logo()

if __name__ == "__main__":
    main()