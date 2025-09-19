#!/usr/bin/env python3
"""
Migration script to update attendance table schema from status-based to visit-count based.

This script:
1. Adds new columns: visit_count, session_type
2. Converts existing status data to visit counts
3. Removes old status column
"""

import sqlite3
from datetime import datetime
import sys
import os

# Add the src directory to the path so we can import our modules
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def migrate_attendance_schema():
    """Migrate attendance table from status-based to visit-count based schema."""
    
    db_path = "students.db"
    
    if not os.path.exists(db_path):
        print(f"Database file {db_path} not found!")
        return False
    
    # Create backup
    backup_path = f"students_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
    import shutil
    shutil.copy2(db_path, backup_path)
    print(f"✅ Created backup: {backup_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if migration is needed
        cursor.execute("PRAGMA table_info(attendance)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'visit_count' in columns and 'session_type' in columns:
            print("✅ Migration already completed - attendance table has new schema")
            conn.close()
            return True
            
        if 'status' not in columns:
            print("⚠️  Unexpected table schema - no 'status' column found")
            conn.close()
            return False
        
        print("🔄 Starting attendance schema migration...")
        
        # Step 1: Add new columns
        print("  Adding new columns...")
        cursor.execute("ALTER TABLE attendance ADD COLUMN visit_count INTEGER DEFAULT 1")
        cursor.execute("ALTER TABLE attendance ADD COLUMN session_type VARCHAR DEFAULT 'Regular'")
        
        # Step 2: Convert existing status data to visit counts
        print("  Converting existing status data...")
        
        # For existing records, we'll set visit_count based on status:
        # - Present/Late -> 1 visit
        # - Absent/Excused -> 0 visits (but we'll keep the record for historical purposes)
        
        cursor.execute("""
            UPDATE attendance 
            SET visit_count = CASE 
                WHEN status IN ('Present', 'Late') THEN 1
                WHEN status IN ('Absent', 'Excused') THEN 0
                ELSE 1
            END,
            session_type = 'Regular'
            WHERE visit_count IS NULL OR visit_count = 1
        """)
        
        converted_records = cursor.rowcount
        print(f"  ✅ Converted {converted_records} existing records")
        
        # Step 3: Remove old status column
        # SQLite doesn't support DROP COLUMN directly, so we need to recreate the table
        print("  Recreating table without status column...")
        
        # Get current table structure (excluding status column)
        cursor.execute("""
            CREATE TABLE attendance_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER NOT NULL,
                date DATETIME NOT NULL,
                visit_count INTEGER NOT NULL DEFAULT 1,
                session_type VARCHAR NOT NULL DEFAULT 'Regular',
                teacher_id INTEGER,
                notes TEXT,
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (student_id) REFERENCES student (id),
                FOREIGN KEY (teacher_id) REFERENCES user (id)
            )
        """)
        
        # Copy data from old table to new table
        cursor.execute("""
            INSERT INTO attendance_new (id, student_id, date, visit_count, session_type, teacher_id, notes, created_at)
            SELECT id, student_id, date, visit_count, session_type, teacher_id, notes, created_at
            FROM attendance
        """)
        
        # Drop old table and rename new table
        cursor.execute("DROP TABLE attendance")
        cursor.execute("ALTER TABLE attendance_new RENAME TO attendance")
        
        # Step 4: Create indexes for performance
        print("  Creating indexes...")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_attendance_student_date ON attendance (student_id, date)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_attendance_teacher ON attendance (teacher_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_attendance_session_type ON attendance (session_type)")
        
        # Commit changes
        conn.commit()
        
        # Verify migration
        cursor.execute("SELECT COUNT(*) FROM attendance")
        total_records = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM attendance WHERE visit_count > 0")
        visit_records = cursor.fetchone()[0]
        
        print(f"  ✅ Migration completed successfully!")
        print(f"  📊 Total attendance records: {total_records}")
        print(f"  📊 Records with visits: {visit_records}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        
        # Restore backup
        if os.path.exists(backup_path):
            shutil.copy2(backup_path, db_path)
            print(f"🔄 Restored from backup: {backup_path}")
        
        return False

def main():
    print("🚀 Attendance Schema Migration")
    print("=" * 40)
    
    success = migrate_attendance_schema()
    
    if success:
        print("\n✅ Migration completed successfully!")
        print("📝 The attendance system now uses visit counting instead of status.")
        print("🔗 You can now run the application with the new schema.")
    else:
        print("\n❌ Migration failed!")
        print("📝 Please check the error messages above.")
        sys.exit(1)

if __name__ == "__main__":
    main()