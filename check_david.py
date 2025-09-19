#!/usr/bin/env python3
"""Check David Wilson's class and category"""

from src.services.db import get_session, Student, Class, Subject
from sqlmodel import select

def check_david_details():
    """Check David Wilson's class and available subjects"""
    with get_session() as session:
        # Get David Wilson
        david = session.exec(select(Student).where(Student.first_name == "David")).first()
        
        if not david:
            print("David not found")
            return
        
        print(f"David Wilson (ID: {david.id})")
        
        # Get his class
        david_class = session.get(Class, david.class_id)
        print(f"Class: {david_class.name if david_class else 'None'}")
        print(f"Category: {david_class.category if david_class else 'None'}")
        
        # Get subjects for his class category
        if david_class:
            subjects = session.exec(
                select(Subject).where(Subject.category == david_class.category)
            ).all()
            
            core_subjects = [s for s in subjects if s.subject_type == 'core']
            elective_subjects = [s for s in subjects if s.subject_type == 'elective']
            
            print(f"\nSubjects for category '{david_class.category}':")
            print(f"Core subjects ({len(core_subjects)}): {[s.name for s in core_subjects]}")
            print(f"Elective subjects ({len(elective_subjects)}): {[s.name for s in elective_subjects]}")
        
        # Check all subjects in database
        all_subjects = session.exec(select(Subject)).all()
        print(f"\nAll subjects in database ({len(all_subjects)}):")
        for subject in all_subjects:
            print(f"  {subject.name} - Category: {subject.category}, Type: {subject.subject_type}")

if __name__ == "__main__":
    check_david_details()