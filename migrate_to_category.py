#!/usr/bin/env python3
"""
Migration script to convert Subject table from class_id to category
This allows subjects to be associated with class categories instead of individual classes
"""

import sqlite3
import sys
from pathlib import Path

def migrate_to_category():
    """Convert Subject table from class_id to category"""
    db_path = Path("students.db")
    
    if not db_path.exists():
        print("❌ Database file not found. Please run the application first to create the database.")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check current table structure
        cursor.execute("PRAGMA table_info(subject)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'category' in columns and 'class_id' not in columns:
            print("✅ Subject table already uses category. No migration needed.")
            conn.close()
            return True
        
        print("🔄 Starting Subject table migration from class_id to category...")
        
        # Get class categories to map class_id to category
        cursor.execute("SELECT id, category FROM class")
        class_categories = {class_id: category for class_id, category in cursor.fetchall()}
        
        # Add category column if it doesn't exist
        if 'category' not in columns:
            cursor.execute("ALTER TABLE subject ADD COLUMN category TEXT")
            print("✅ Added category column to Subject table")
        
        # Update subjects with their class categories
        if 'class_id' in columns:
            cursor.execute("SELECT id, class_id FROM subject WHERE class_id IS NOT NULL")
            subjects_to_update = cursor.fetchall()
            
            for subject_id, class_id in subjects_to_update:
                category = class_categories.get(class_id, "Lower Primary")  # Default fallback
                cursor.execute("UPDATE subject SET category = ? WHERE id = ?", (category, subject_id))
            
            print(f"✅ Updated {len(subjects_to_update)} subjects with categories")
            
            # Create new table without class_id
            cursor.execute("""
                CREATE TABLE subject_new (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    code TEXT NOT NULL,
                    category TEXT NOT NULL
                )
            """)
            
            # Copy data to new table
            cursor.execute("""
                INSERT INTO subject_new (id, name, code, category)
                SELECT id, name, code, category FROM subject
            """)
            
            # Drop old table and rename new table
            cursor.execute("DROP TABLE subject")
            cursor.execute("ALTER TABLE subject_new RENAME TO subject")
            
            print("✅ Removed class_id column and restructured table")
        
        # Commit changes
        conn.commit()
        print("✅ Subject table migration to category completed successfully!")
        
        # Show summary
        cursor.execute("SELECT category, COUNT(*) FROM subject GROUP BY category")
        category_counts = cursor.fetchall()
        print("📊 Subjects by category:")
        for category, count in category_counts:
            print(f"   - {category}: {count} subjects")
        
        conn.close()
        return True
        
    except sqlite3.Error as e:
        print(f"❌ Database error during migration: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error during migration: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Subject Category Migration Script")
    print("=" * 50)
    
    success = migrate_to_category()
    
    if success:
        print("\n✅ Migration completed successfully!")
        print("Subjects are now organized by category (Lower Primary, Upper Primary, JHS)")
        print("You can now restart the application.")
    else:
        print("\n❌ Migration failed!")
        sys.exit(1)
