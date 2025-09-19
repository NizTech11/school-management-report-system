#!/usr/bin/env python3
"""
Migration script to add exam_type column to marks table
"""

import sqlite3
import os

def migrate_exam_types():
    """Add exam_type column to marks table"""
    
    db_path = "students.db"
    if not os.path.exists(db_path):
        print("Database file not found!")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if exam_type column already exists
        cursor.execute("PRAGMA table_info(mark)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'exam_type' not in columns:
            print("Adding exam_type column to mark table...")
            
            # Add exam_type column with default value
            cursor.execute("""
                ALTER TABLE mark 
                ADD COLUMN exam_type TEXT DEFAULT 'Mid-term'
            """)
            
            # Update existing records to have varied exam types
            # This distributes existing marks across different exam types
            cursor.execute("""
                UPDATE mark 
                SET exam_type = CASE 
                    WHEN id % 3 = 0 THEN 'Mid-term'
                    WHEN id % 3 = 1 THEN 'External'
                    ELSE 'End of Term'
                END
            """)
            
            conn.commit()
            print("✅ Successfully added exam_type column and populated with sample data")
            
            # Show distribution
            cursor.execute("SELECT exam_type, COUNT(*) FROM mark GROUP BY exam_type")
            distribution = cursor.fetchall()
            print("\nExam Type Distribution:")
            for exam_type, count in distribution:
                print(f"  {exam_type}: {count} marks")
                
        else:
            print("exam_type column already exists in mark table")
            
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        conn.rollback()
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_exam_types()