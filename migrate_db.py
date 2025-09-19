#!/usr/bin/env python3
"""
Database migration script to add Teacher table and teacher_id to Class table
"""

import sqlite3
import os
from pathlib import Path

def migrate_database():
    """Migrate the database to add Teacher table and teacher_id column"""
    
    # Database path
    db_path = "students.db"
    
    print(f"Migrating database: {db_path}")
    
    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if Teacher table exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='teacher';
        """)
        teacher_table_exists = cursor.fetchone() is not None
        
        if not teacher_table_exists:
            print("Creating Teacher table...")
            cursor.execute("""
                CREATE TABLE teacher (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    first_name VARCHAR NOT NULL,
                    last_name VARCHAR NOT NULL,
                    email VARCHAR NOT NULL,
                    phone VARCHAR,
                    subject_specialization VARCHAR
                )
            """)
            print("✓ Teacher table created")
        else:
            print("✓ Teacher table already exists")
        
        # Check if teacher_id column exists in Class table
        cursor.execute("PRAGMA table_info(class)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'teacher_id' not in columns:
            print("Adding teacher_id column to Class table...")
            cursor.execute("""
                ALTER TABLE class 
                ADD COLUMN teacher_id INTEGER
            """)
            print("✓ teacher_id column added to Class table")
        else:
            print("✓ teacher_id column already exists in Class table")
        
        # Check if class_id column exists in Student table
        cursor.execute("PRAGMA table_info(student)")
        student_columns = [column[1] for column in cursor.fetchall()]
        
        print(f"Current student table columns: {student_columns}")
        
        if 'class_id' not in student_columns:
            print("Adding class_id column to Student table...")
            cursor.execute("""
                ALTER TABLE student 
                ADD COLUMN class_id INTEGER
            """)
            print("✓ class_id column added to Student table")
        else:
            print("✓ class_id column already exists in Student table")
        
        # Check if old class_name column exists and remove NOT NULL constraint if needed
        if 'class_name' in student_columns:
            print("Found old class_name column. Updating table structure...")
            
            # Create a new table with correct structure
            cursor.execute("""
                CREATE TABLE student_new (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    first_name VARCHAR NOT NULL,
                    last_name VARCHAR NOT NULL,
                    class_id INTEGER,
                    aggregate REAL
                )
            """)
            
            # Copy data from old table to new table (excluding admission_no and email)
            cursor.execute("""
                INSERT INTO student_new (id, first_name, last_name, class_id)
                SELECT id, first_name, last_name, class_id FROM student
            """)
            
            # Drop old table and rename new table
            cursor.execute("DROP TABLE student")
            cursor.execute("ALTER TABLE student_new RENAME TO student")
            
            print("✓ Student table structure updated (removed class_name, admission_no, email; added aggregate)")
        else:
            # Check if we need to add aggregate column and remove old columns
            if 'admission_no' in student_columns or 'email' in student_columns:
                print("Updating student table to remove admission_no and email, add aggregate...")
                
                # Create a new table with correct structure
                cursor.execute("""
                    CREATE TABLE student_new (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        first_name VARCHAR NOT NULL,
                        last_name VARCHAR NOT NULL,
                        class_id INTEGER,
                        aggregate REAL
                    )
                """)
                
                # Copy data from old table to new table
                cursor.execute("""
                    INSERT INTO student_new (id, first_name, last_name, class_id)
                    SELECT id, first_name, last_name, class_id FROM student
                """)
                
                # Drop old table and rename new table
                cursor.execute("DROP TABLE student")
                cursor.execute("ALTER TABLE student_new RENAME TO student")
                
                print("✓ Student table updated (removed admission_no, email; added aggregate)")
            elif 'aggregate' not in student_columns:
                print("Adding aggregate column to Student table...")
                cursor.execute("""
                    ALTER TABLE student 
                    ADD COLUMN aggregate REAL
                """)
                print("✓ aggregate column added to Student table")
            else:
                print("✓ Student table structure is up to date")
        
        # Commit changes
        conn.commit()
        print("✅ Database migration completed successfully!")
        
    except sqlite3.Error as e:
        print(f"❌ Error during migration: {e}")
        conn.rollback()
        raise
    
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_database()
