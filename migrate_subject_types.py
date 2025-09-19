#!/usr/bin/env python3
"""
Migration to add subject_type field to Subject table and implement aggregate calculation
"""

import sys
import os
sys.path.append('src')

from services.db import *
from sqlmodel import text

def migrate_subject_types():
    """Add subject_type field to Subject table"""
    print("Adding subject_type field to Subject table...")
    
    engine = get_engine()
    
    with Session(engine) as session:
        try:
            # Add subject_type column to Subject table
            session.execute(text("ALTER TABLE subject ADD COLUMN subject_type TEXT DEFAULT 'elective'"))
            session.commit()
            print("✅ Added subject_type column to Subject table")
        except Exception as e:
            if "duplicate column name" in str(e).lower() or "already exists" in str(e).lower():
                print("ℹ️  subject_type column already exists, skipping...")
            else:
                print(f"❌ Error adding subject_type column: {e}")
                return False
        
        # Update Subject model schema by recreating the table structure
        try:
            # Check if we need to set default core subjects
            subjects = session.exec(select(Subject)).all()
            
            # Define common core subjects by name patterns
            core_subject_patterns = [
                'english', 'mathematics', 'science', 'social', 'math', 
                'literacy', 'numeracy', 'integrated science', 'history',
                'geography', 'civic', 'biology', 'chemistry', 'physics',
                'language arts', 'reading', 'writing'
            ]
            
            updated_count = 0
            for subject in subjects:
                subject_name_lower = subject.name.lower()
                is_core = any(pattern in subject_name_lower for pattern in core_subject_patterns)
                
                if is_core:
                    # Update to core
                    session.execute(
                        text("UPDATE subject SET subject_type = 'core' WHERE id = :id"),
                        {"id": subject.id}
                    )
                    updated_count += 1
                    print(f"   Set '{subject.name}' as CORE subject")
            
            session.commit()
            print(f"✅ Updated {updated_count} subjects as core subjects")
            
            # Show summary
            core_subjects = session.execute(text("SELECT COUNT(*) FROM subject WHERE subject_type = 'core'")).scalar()
            elective_subjects = session.execute(text("SELECT COUNT(*) FROM subject WHERE subject_type = 'elective'")).scalar()
            
            print(f"📊 Subject Summary:")
            print(f"   Core subjects: {core_subjects}")
            print(f"   Elective subjects: {elective_subjects}")
            
        except Exception as e:
            print(f"❌ Error updating subject types: {e}")
            session.rollback()
            return False
    
    return True

def update_subject_model():
    """Update the Subject model in db.py to include subject_type field"""
    print("\n📝 Note: You may need to update the Subject model in src/services/db.py")
    print("Add this line to the Subject class:")
    print("    subject_type: str = Field(default='elective')  # 'core' or 'elective'")

if __name__ == "__main__":
    print("🔄 Starting Subject Type Migration...")
    
    if migrate_subject_types():
        update_subject_model()
        print("\n✅ Migration completed successfully!")
        print("🎯 You can now implement aggregate calculations using core vs elective subjects")
    else:
        print("\n❌ Migration failed!")