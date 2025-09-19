"""
Migration to add Teacher-Class Assignment System
Adds TeacherClass table for many-to-many relationships and updates User table
"""

import sqlite3
from pathlib import Path

def migrate_teacher_class_assignment():
    """Add TeacherClass table and update User table"""
    db_path = Path("students.db")
    
    if not db_path.exists():
        print("Database file not found. Please run the application first to create the database.")
        return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if TeacherClass table already exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='teacherclass'")
        if cursor.fetchone():
            print("TeacherClass table already exists. Skipping creation.")
        else:
            # Create TeacherClass table for many-to-many relationship
            cursor.execute("""
                CREATE TABLE teacherclass (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    class_id INTEGER NOT NULL,
                    assigned_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT 1,
                    FOREIGN KEY (user_id) REFERENCES user (id) ON DELETE CASCADE,
                    FOREIGN KEY (class_id) REFERENCES class (id) ON DELETE CASCADE,
                    UNIQUE(user_id, class_id)
                )
            """)
            print("✅ Created TeacherClass table")
        
        # Check if teacher_id column exists in User table
        cursor.execute("PRAGMA table_info(user)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'teacher_id' not in columns:
            # Add teacher_id column to User table to link to Teacher records
            cursor.execute("ALTER TABLE user ADD COLUMN teacher_id INTEGER")
            cursor.execute("CREATE INDEX idx_user_teacher_id ON user(teacher_id)")
            print("✅ Added teacher_id column to User table")
        else:
            print("teacher_id column already exists in User table")
        
        # Create indexes for better performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_teacherclass_user_id ON teacherclass(user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_teacherclass_class_id ON teacherclass(class_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_teacherclass_active ON teacherclass(is_active)")
        
        conn.commit()
        print("✅ Migration completed successfully!")
        
        # Display current table counts
        cursor.execute("SELECT COUNT(*) FROM user")
        user_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM teacher")
        teacher_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM class")
        class_count = cursor.fetchone()[0]
        
        print(f"\n📊 Current data counts:")
        print(f"Users: {user_count}")
        print(f"Teachers: {teacher_count}")
        print(f"Classes: {class_count}")
        
        return True
        
    except sqlite3.Error as e:
        print(f"❌ Error during migration: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    print("🚀 Starting Teacher-Class Assignment Migration...")
    success = migrate_teacher_class_assignment()
    if success:
        print("🎉 Migration completed successfully!")
    else:
        print("💥 Migration failed!")