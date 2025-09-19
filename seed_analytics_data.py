#!/usr/bin/env python3
"""
Seed Enhanced Analytics Sample Data
Creates comprehensive sample data for testing the Enhanced Analytics features
"""

import sqlite3
import random
from datetime import datetime, timedelta
from pathlib import Path

def seed_enhanced_analytics_data():
    """Create sample data for enhanced analytics testing"""
    db_path = Path("students.db")
    
    if not db_path.exists():
        print("❌ Database file not found. Please run the application first.")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🌱 Seeding Enhanced Analytics Sample Data...")
        
        # Get existing students, subjects, and classes
        cursor.execute("SELECT id, first_name, last_name FROM student LIMIT 10")
        students = cursor.fetchall()
        
        cursor.execute("SELECT id, name FROM subject")
        subjects = cursor.fetchall()
        
        if not students or not subjects:
            print("❌ No students or subjects found. Please add some basic data first.")
            return False
        
        print(f"Found {len(students)} students and {len(subjects)} subjects")
        
        # Generate marks with temporal progression and trends
        marks_data = []
        base_date = datetime.now() - timedelta(days=120)  # Start 4 months ago
        
        for student in students:
            student_id = student[0]
            student_name = f"{student[1]} {student[2]}"
            
            # Determine student's performance profile
            performance_profiles = [
                {'base_score': 85, 'trend': 0.1, 'volatility': 5},   # High performer, improving
                {'base_score': 75, 'trend': -0.05, 'volatility': 8}, # Good performer, declining
                {'base_score': 65, 'trend': 0.15, 'volatility': 10}, # Average, improving
                {'base_score': 55, 'trend': -0.1, 'volatility': 12}, # Below average, declining
                {'base_score': 45, 'trend': 0.2, 'volatility': 15},  # Poor performer, improving
            ]
            
            profile = random.choice(performance_profiles)
            
            # Generate marks over time for each subject
            for subject in subjects:
                subject_id = subject[0]
                subject_name = subject[1]
                
                # Subject difficulty adjustment
                subject_adjustments = {
                    'Mathematics': -3,
                    'English': 0,
                    'Science': -2,
                    'History': 2,
                    'Geography': 1
                }
                
                subject_adj = subject_adjustments.get(subject_name, 0)
                
                # Generate 8-12 marks over 4 months
                num_marks = random.randint(8, 12)
                
                for i in range(num_marks):
                    # Calculate date
                    days_offset = (120 / num_marks) * i + random.randint(-3, 3)
                    mark_date = base_date + timedelta(days=days_offset)
                    
                    # Calculate score with trend and noise
                    trend_effect = profile['trend'] * i
                    base_score = profile['base_score'] + subject_adj
                    noise = random.gauss(0, profile['volatility'])
                    
                    score = base_score + trend_effect + noise
                    score = max(0, min(100, score))  # Clamp between 0-100
                    
                    # Assign term based on date
                    if mark_date < base_date + timedelta(days=40):
                        term = "Term 1"
                    elif mark_date < base_date + timedelta(days=80):
                        term = "Term 2"
                    else:
                        term = "Term 3"
                    
                    marks_data.append((
                        student_id,
                        subject_id,
                        round(score, 1),
                        term
                    ))
        
        # Insert marks data
        print(f"Inserting {len(marks_data)} sample marks...")
        cursor.executemany("""
            INSERT INTO mark (student_id, subject_id, score, term)
            VALUES (?, ?, ?, ?)
        """, marks_data)
        
        # Update student aggregates based on their marks
        print("Updating student aggregates...")
        for student in students:
            student_id = student[0]
            
            # Calculate aggregate score
            cursor.execute("""
                SELECT AVG(score) 
                FROM mark 
                WHERE student_id = ?
            """, (student_id,))
            
            avg_score = cursor.fetchone()[0]
            if avg_score:
                cursor.execute("""
                    UPDATE student 
                    SET aggregate = ? 
                    WHERE id = ?
                """, (round(avg_score, 2), student_id))
        
        conn.commit()
        
        print("✅ Sample data seeded successfully!")
        
        # Show summary statistics
        cursor.execute("SELECT COUNT(*) FROM mark")
        total_marks = cursor.fetchone()[0]
        
        cursor.execute("SELECT AVG(score) FROM mark")
        avg_score = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(DISTINCT student_id) FROM mark")
        students_with_marks = cursor.fetchone()[0]
        
        print(f"📊 Summary:")
        print(f"   - Total marks: {total_marks}")
        print(f"   - Average score: {avg_score:.1f}%")
        print(f"   - Students with marks: {students_with_marks}")
        
        conn.close()
        return True
        
    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Enhanced Analytics Data Seeder")
    print("=" * 50)
    
    success = seed_enhanced_analytics_data()
    
    if success:
        print("\n✅ Data seeding completed successfully!")
        print("You can now access the Enhanced Analytics with meaningful sample data.")
        print("Navigate to the '🔬 Enhanced Analytics' page in the application.")
    else:
        print("\n❌ Data seeding failed!")
        exit(1)