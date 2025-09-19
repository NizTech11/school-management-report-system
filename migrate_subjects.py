#!/usr/bin/env python3
"""
Migration script to add class_id to Subject table
This allows subjects to be associated with specific classes
"""

import sqlite3
import sys
from pathlib import Path

def migrate_subject_table():
    """Add class_id column to Subject table"""
    db_path = Path("students.db")
    
    if not db_path.exists():
        print("❌ Database file not found. Please run the application first to create the database.")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if class_id column already exists
        cursor.execute("PRAGMA table_info(subject)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'class_id' in columns:
            print("✅ Subject table already has class_id column. No migration needed.")
            conn.close()
            return True
        
        print("🔄 Starting Subject table migration...")
        
        # Add class_id column to Subject table
        cursor.execute("ALTER TABLE subject ADD COLUMN class_id INTEGER")
        print("✅ Added class_id column to Subject table")
        
        # Get the first class ID to use as default for existing subjects
        cursor.execute("SELECT id FROM class ORDER BY id LIMIT 1")
        first_class = cursor.fetchone()
        
        if first_class:
            default_class_id = first_class[0]
            # Update existing subjects to have the first class as default
            cursor.execute("UPDATE subject SET class_id = ? WHERE class_id IS NULL", (default_class_id,))
            print(f"✅ Updated existing subjects to use class ID {default_class_id} as default")
        else:
            print("⚠️  No classes found. Existing subjects will have NULL class_id")
        
        # Commit changes
        conn.commit()
        print("✅ Subject table migration completed successfully!")
        
        # Show summary
        cursor.execute("SELECT COUNT(*) FROM subject")
        subject_count = cursor.fetchone()[0]
        print(f"📊 Total subjects in database: {subject_count}")
        
        conn.close()
        return True
        
    except sqlite3.Error as e:
        print(f"❌ Database error during migration: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error during migration: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Subject Table Migration Script")
    print("=" * 50)
    
    success = migrate_subject_table()
    
    if success:
        print("\n✅ Migration completed successfully!")
        print("You can now restart the application.")
    else:
        print("\n❌ Migration failed!")
        sys.exit(1)
