"""
Migration script to add curriculum and assessment tables
Run this after implementing the curriculum system
"""

import sqlite3
from pathlib import Path
import sys
import os

# Add the src directory to Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from services.db import get_engine
from sqlmodel import SQLModel

def migrate_curriculum_tables():
    """Create new curriculum and assessment tables"""
    print("🔄 Creating curriculum and assessment tables...")
    
    try:
        # This will create all tables that don't exist yet
        engine = get_engine()
        SQLModel.metadata.create_all(engine)
        
        print("✅ Curriculum and assessment tables created successfully!")
        
        # Verify the tables were created
        db_path = "students.db"
        if Path(db_path).exists():
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Check which new tables were created
            new_tables = [
                'curriculum', 'assignment', 'gradingrubric', 'studentassignment', 
                'continuousassessment', 'learningobjective'
            ]
            
            for table in new_tables:
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,))
                if cursor.fetchone():
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    count = cursor.fetchone()[0]
                    print(f"  📊 Table '{table}': {count} records")
                else:
                    print(f"  ⚠️ Table '{table}': Not found")
            
            conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        return False

def add_sample_curriculum_data():
    """Add sample curriculum data for testing"""
    print("🔄 Adding sample curriculum data...")
    
    try:
        from services.db import get_session, Curriculum, Subject, Class, AcademicYear, GradingRubric
        from sqlmodel import select
        from datetime import datetime
        import json
        
        with get_session() as session:
            # Get first subject and class for sample data
            subject = session.exec(select(Subject)).first()
            class_obj = session.exec(select(Class)).first()
            academic_year = session.exec(select(AcademicYear)).first()
            
            if not subject or not class_obj or not academic_year:
                print("⚠️ Need subjects, classes, and academic years to create sample data")
                return False
            
            # Check if sample curriculum already exists
            existing = session.exec(
                select(Curriculum).where(Curriculum.name == "Sample Mathematics Curriculum")
            ).first()
            
            if existing:
                print("ℹ️ Sample curriculum already exists")
                return True
            
            # Create sample curriculum
            sample_objectives = [
                {
                    "text": "Students will understand basic arithmetic operations",
                    "category": "knowledge",
                    "priority": "high"
                },
                {
                    "text": "Students will solve word problems involving fractions",
                    "category": "application",
                    "priority": "medium"
                },
                {
                    "text": "Students will analyze mathematical patterns",
                    "category": "analysis",
                    "priority": "medium"
                }
            ]
            
            curriculum = Curriculum(
                name="Sample Mathematics Curriculum",
                subject_id=subject.id,
                class_id=class_obj.id,
                academic_year_id=academic_year.id,
                description="A comprehensive mathematics curriculum for primary students",
                learning_objectives=json.dumps(sample_objectives),
                total_lessons=40,
                duration_weeks=20,
                created_by=1,  # Default admin user
                status="active"
            )
            session.add(curriculum)
            session.commit()
            
            # Create sample grading rubric
            sample_criteria = [
                {
                    "name": "Problem Solving",
                    "description": "Ability to solve mathematical problems correctly",
                    "weight": 40,
                    "levels": {
                        "excellent": 4,
                        "good": 3,
                        "satisfactory": 2,
                        "needs_improvement": 1
                    }
                },
                {
                    "name": "Mathematical Communication",
                    "description": "Clear explanation of mathematical thinking",
                    "weight": 30,
                    "levels": {
                        "excellent": 4,
                        "good": 3,
                        "satisfactory": 2,
                        "needs_improvement": 1
                    }
                },
                {
                    "name": "Accuracy",
                    "description": "Correctness of calculations and solutions",
                    "weight": 30,
                    "levels": {
                        "excellent": 4,
                        "good": 3,
                        "satisfactory": 2,
                        "needs_improvement": 1
                    }
                }
            ]
            
            rubric = GradingRubric(
                name="Mathematics Assessment Rubric",
                description="Standard rubric for mathematics assignments",
                subject_id=subject.id,
                criteria=json.dumps(sample_criteria),
                scale_type="points",
                max_score=100.0,
                created_by=1,
                is_template=True
            )
            session.add(rubric)
            session.commit()
            
            print("✅ Sample curriculum data created successfully!")
            print(f"  📚 Curriculum: {curriculum.name}")
            print(f"  📊 Rubric: {rubric.name}")
            
        return True
        
    except Exception as e:
        print(f"❌ Error creating sample data: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting Curriculum & Assessment Migration")
    print("=" * 50)
    
    # Create tables
    if migrate_curriculum_tables():
        # Add sample data
        add_sample_curriculum_data()
        
        print("\n" + "=" * 50)
        print("✅ Migration completed successfully!")
        print("\n📚 You can now access:")
        print("  • Curriculum Planning")
        print("  • Assignment Management") 
        print("  • Grading Rubrics")
        print("  • Continuous Assessment")
        print("  • Assessment Analytics")
        
    else:
        print("\n❌ Migration failed!")
        sys.exit(1)