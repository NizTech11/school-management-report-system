#!/usr/bin/env python3
"""
Test Enhanced Analytics Import
"""

import sys
import os

# Add src to path
sys.path.insert(0, 'src')

def test_enhanced_analytics_import():
    """Test if enhanced analytics can be imported"""
    print("🧪 Testing Enhanced Analytics Import")
    print("=" * 50)
    
    try:
        print("1. Testing basic imports...")
        import pandas as pd
        import numpy as np
        import plotly.express as px
        print("   ✅ Basic packages imported successfully")
        
        print("2. Testing sklearn imports...")
        try:
            from sklearn.linear_model import LinearRegression
            print("   ✅ Sklearn is available")
            sklearn_available = True
        except ImportError:
            print("   ⚠️  Sklearn not available (this is OK)")
            sklearn_available = False
        
        print("3. Testing database imports...")
        from services.db import get_session, Student, Subject, Mark, Class
        print("   ✅ Database modules imported successfully")
        
        print("4. Testing enhanced analytics import...")
        from components.enhanced_analytics import render_enhanced_analytics
        print("   ✅ Enhanced analytics imported successfully")
        
        print(f"\n🎯 RESULT: Enhanced Analytics is ready!")
        print(f"   Sklearn status: {'Available' if sklearn_available else 'Not available (limited features)'}")
        print(f"   The app should now run without import errors.")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Import failed: {e}")
        return False

def main():
    """Main function"""
    os.chdir("c:\\Users\\abeik\\OneDrive - Georgia Institute of Technology\\Desktop\\sytems students")
    success = test_enhanced_analytics_import()
    
    if success:
        print(f"\n🚀 NEXT STEPS:")
        print("1. Run: streamlit run src/app.py")
        print("2. Navigate to Enhanced Analytics page")
        print("3. The sklearn features will show appropriate warnings if not available")
    else:
        print(f"\n❌ ISSUES FOUND:")
        print("Please check the error messages above and fix any import issues.")

if __name__ == "__main__":
    main()