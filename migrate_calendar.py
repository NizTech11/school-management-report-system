#!/usr/bin/env python3
"""
Migration script to add Academic Calendar & Scheduling tables
"""

import sqlite3
import sys
from pathlib import Path
from datetime import datetime

def migrate_calendar_tables():
    """Add calendar and scheduling tables"""
    db_path = Path("students.db")
    
    if not db_path.exists():
        print("❌ Database file not found. Please run the application first to create the database.")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔄 Starting Academic Calendar tables migration...")
        
        # Create AcademicYear table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS academicyear (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                year VARCHAR UNIQUE NOT NULL,
                start_date TIMESTAMP NOT NULL,
                end_date TIMESTAMP NOT NULL,
                is_current BOOLEAN DEFAULT 0 NOT NULL,
                description TEXT
            )
        """)
        print("✅ AcademicYear table created")
        
        # Create Term table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS term (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                academic_year_id INTEGER NOT NULL,
                name VARCHAR NOT NULL,
                start_date TIMESTAMP NOT NULL,
                end_date TIMESTAMP NOT NULL,
                is_current BOOLEAN DEFAULT 0 NOT NULL,
                FOREIGN KEY (academic_year_id) REFERENCES academicyear (id)
            )
        """)
        print("✅ Term table created")
        
        # Create CalendarEvent table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS calendarevent (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title VARCHAR NOT NULL,
                description TEXT,
                event_type VARCHAR NOT NULL,
                start_date TIMESTAMP NOT NULL,
                end_date TIMESTAMP,
                is_all_day BOOLEAN DEFAULT 1 NOT NULL,
                academic_year_id INTEGER,
                term_id INTEGER,
                class_id INTEGER,
                created_by INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (academic_year_id) REFERENCES academicyear (id),
                FOREIGN KEY (term_id) REFERENCES term (id),
                FOREIGN KEY (class_id) REFERENCES class (id),
                FOREIGN KEY (created_by) REFERENCES user (id)
            )
        """)
        print("✅ CalendarEvent table created")
        
        # Create Timetable table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS timetable (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                class_id INTEGER NOT NULL,
                subject_id INTEGER NOT NULL,
                teacher_id INTEGER,
                day_of_week INTEGER NOT NULL,
                start_time VARCHAR NOT NULL,
                end_time VARCHAR NOT NULL,
                room VARCHAR,
                academic_year_id INTEGER NOT NULL,
                term_id INTEGER,
                FOREIGN KEY (class_id) REFERENCES class (id),
                FOREIGN KEY (subject_id) REFERENCES subject (id),
                FOREIGN KEY (teacher_id) REFERENCES teacher (id),
                FOREIGN KEY (academic_year_id) REFERENCES academicyear (id),
                FOREIGN KEY (term_id) REFERENCES term (id)
            )
        """)
        print("✅ Timetable table created")
        
        # Create ExamSchedule table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS examschedule (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title VARCHAR NOT NULL,
                subject_id INTEGER NOT NULL,
                class_id INTEGER NOT NULL,
                exam_date TIMESTAMP NOT NULL,
                start_time VARCHAR NOT NULL,
                end_time VARCHAR NOT NULL,
                room VARCHAR,
                duration_minutes INTEGER,
                instructions TEXT,
                term_id INTEGER NOT NULL,
                created_by INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (subject_id) REFERENCES subject (id),
                FOREIGN KEY (class_id) REFERENCES class (id),
                FOREIGN KEY (term_id) REFERENCES term (id),
                FOREIGN KEY (created_by) REFERENCES user (id)
            )
        """)
        print("✅ ExamSchedule table created")
        
        # Create default academic year if none exists
        cursor.execute("SELECT COUNT(*) FROM academicyear")
        year_count = cursor.fetchone()[0]
        
        if year_count == 0:
            print("Creating default academic year...")
            current_year = datetime.now().year
            next_year = current_year + 1
            year_str = f"{current_year}-{next_year}"
            
            start_date = datetime(current_year, 9, 1)  # September 1st
            end_date = datetime(next_year, 6, 30)      # June 30th next year
            
            cursor.execute("""
                INSERT INTO academicyear (year, start_date, end_date, is_current, description)
                VALUES (?, ?, ?, ?, ?)
            """, (
                year_str,
                start_date.isoformat(),
                end_date.isoformat(),
                1,  # Set as current
                f"Academic Year {year_str}"
            ))
            
            # Get the ID of the created academic year
            academic_year_id = cursor.lastrowid
            
            # Create default terms
            terms = [
                ("Term 1", datetime(current_year, 9, 1), datetime(current_year, 12, 15)),
                ("Term 2", datetime(current_year + 1, 1, 8), datetime(current_year + 1, 4, 15)),
                ("Term 3", datetime(current_year + 1, 4, 22), datetime(current_year + 1, 6, 30))
            ]
            
            for i, (term_name, start, end) in enumerate(terms):
                cursor.execute("""
                    INSERT INTO term (academic_year_id, name, start_date, end_date, is_current)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    academic_year_id,
                    term_name,
                    start.isoformat(),
                    end.isoformat(),
                    1 if i == 0 else 0  # Set first term as current
                ))
            
            print(f"✅ Default academic year {year_str} created with 3 terms")
        else:
            print("✅ Academic years already exist, skipping default creation")
        
        # Commit changes
        conn.commit()
        print("✅ Academic Calendar migration completed successfully!")
        
        # Show summary
        cursor.execute("SELECT COUNT(*) FROM academicyear")
        year_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM term")
        term_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM calendarevent")
        event_count = cursor.fetchone()[0]
        
        print(f"📊 Migration Summary:")
        print(f"   - Academic Years: {year_count}")
        print(f"   - Terms: {term_count}")
        print(f"   - Calendar Events: {event_count}")
        
        conn.close()
        return True
        
    except sqlite3.Error as e:
        print(f"❌ Database error during migration: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error during migration: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Academic Calendar Migration Script")
    print("=" * 50)
    
    success = migrate_calendar_tables()
    
    if success:
        print("\n✅ Migration completed successfully!")
        print("The Academic Calendar & Scheduling system is now ready.")
        print("You can now restart the application and access the Calendar page.")
    else:
        print("\n❌ Migration failed!")
        sys.exit(1)