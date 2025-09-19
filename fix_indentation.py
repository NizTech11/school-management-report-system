#!/usr/bin/env python3
"""Fix the indentation issue in calculate_student_aggregate function"""

def fix_db_file():
    """Fix the indentation issue in db.py"""
    # Read the current file
    with open('src/services/db.py', 'r') as f:
        content = f.read()
    
    # Find the problematic section and fix it
    old_section = """        ).all()
        
            # If no subjects found for exact category, fall back to all subjects
            # This handles cases where class categories don't match subject categories
            if not subjects:
                subjects = session.exec(select(Subject)).all()
        
        # Separate core and elective subjects"""
    
    new_section = """        ).all()
        
        # If no subjects found for exact category, fall back to all subjects
        # This handles cases where class categories don't match subject categories
        if not subjects:
            subjects = session.exec(select(Subject)).all()
        
        # Separate core and elective subjects"""
    
    if old_section in content:
        content = content.replace(old_section, new_section)
        
        # Write back the fixed content
        with open('src/services/db.py', 'w') as f:
            f.write(content)
        
        print("Fixed indentation in db.py")
    else:
        print("Section not found - manual fix needed")

if __name__ == "__main__":
    fix_db_file()