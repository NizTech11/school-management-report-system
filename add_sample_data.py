#!/usr/bin/env python3
"""
Add Sample Students and Classes for Analytics Testing
"""

import sqlite3
from pathlib import Path

def add_sample_data():
    """Add sample students and classes"""
    db_path = Path("students.db")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🏫 Adding sample classes...")
        
        # Add sample classes
        classes = [
            ("Class 6A", "Primary", "Morning shift class for 6th grade"),
            ("Class 7B", "Primary", "Regular class for 7th grade"),
            ("Class 8A", "Secondary", "Advanced class for 8th grade"),
            ("Class 9B", "Secondary", "Regular class for 9th grade"),
            ("Class 10A", "Secondary", "Senior class for 10th grade"),
        ]
        
        for class_name, category, description in classes:
            cursor.execute("""
                INSERT OR IGNORE INTO class (name, category, description)
                VALUES (?, ?, ?)
            """, (class_name, category, description))
        
        # Get class IDs
        cursor.execute("SELECT id, name FROM class")
        class_data = cursor.fetchall()
        class_ids = [cls[0] for cls in class_data]
        
        print(f"✅ Added {len(class_data)} classes")
        
        print("👥 Adding sample students...")
        
        # Add sample students
        sample_students = [
            ("Alice", "Johnson"),
            ("Bob", "Smith"),
            ("Carol", "Davis"),
            ("David", "Wilson"),
            ("Emma", "Brown"),
            ("Frank", "Jones"),
            ("Grace", "Miller"),
            ("Henry", "Garcia"),
            ("Ivy", "Rodriguez"),
            ("Jack", "Martinez"),
            ("Kate", "Lopez"),
            ("Liam", "Gonzalez"),
            ("Maya", "Anderson"),
            ("Noah", "Taylor"),
            ("Olivia", "Thomas"),
        ]
        
        for first_name, last_name in sample_students:
            class_id = class_ids[hash(first_name) % len(class_ids)]  # Distribute across classes
            
            cursor.execute("""
                INSERT OR IGNORE INTO student 
                (first_name, last_name, class_id, aggregate)
                VALUES (?, ?, ?, ?)
            """, (first_name, last_name, class_id, 0.0))
        
        conn.commit()
        
        # Check results
        cursor.execute("SELECT COUNT(*) FROM student")
        student_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM class")
        class_count = cursor.fetchone()[0]
        
        print(f"✅ Added {student_count} students")
        print(f"✅ Total {class_count} classes")
        
        conn.close()
        return True
        
    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Adding Sample Data for Analytics")
    print("=" * 40)
    
    success = add_sample_data()
    
    if success:
        print("\n✅ Sample data added successfully!")
        print("Now you can run the analytics seeding script.")
    else:
        print("\n❌ Failed to add sample data!")
        exit(1)