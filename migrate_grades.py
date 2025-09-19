#!/usr/bin/env python3
"""
Migration script to add grade field to existing marks and calculate grades
"""

import sqlite3
from src.services.db import calculate_grade

def migrate_add_grades():
    """Add grade column and calculate grades for existing marks"""
    
    # Connect to the database
    conn = sqlite3.connect('students.db')
    cursor = conn.cursor()
    
    try:
        # Check if grade column already exists
        cursor.execute("PRAGMA table_info(mark)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'grade' not in columns:
            print("Adding grade column to mark table...")
            cursor.execute("ALTER TABLE mark ADD COLUMN grade INTEGER")
            print("✅ Grade column added successfully")
        else:
            print("Grade column already exists")
        
        # Calculate and update grades for all existing marks
        print("Calculating grades for existing marks...")
        cursor.execute("SELECT id, score FROM mark")
        marks = cursor.fetchall()
        
        updated_count = 0
        for mark_id, score in marks:
            try:
                grade = calculate_grade(float(score))
                cursor.execute("UPDATE mark SET grade = ? WHERE id = ?", (grade, mark_id))
                updated_count += 1
            except Exception as e:
                print(f"Error calculating grade for mark {mark_id} (score: {score}): {e}")
        
        conn.commit()
        print(f"✅ Updated grades for {updated_count} marks")
        
        # Show some statistics
        cursor.execute("""
            SELECT grade, COUNT(*) as count 
            FROM mark 
            WHERE grade IS NOT NULL 
            GROUP BY grade 
            ORDER BY grade
        """)
        
        grade_stats = cursor.fetchall()
        print("\nGrade Distribution:")
        print("==================")
        for grade, count in grade_stats:
            print(f"Grade {grade}: {count} marks")
        
    except Exception as e:
        print(f"❌ Error during migration: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_add_grades()