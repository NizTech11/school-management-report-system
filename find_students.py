#!/usr/bin/env python3
"""Find correct student IDs"""

from src.services.db import get_session, Student
from sqlmodel import select

def find_students():
    with get_session() as session:
        students = session.exec(select(Student)).all()
        
        print("Student IDs and Names:")
        print("=" * 40)
        
        for student in students:
            print(f"ID: {student.id}, Name: {student.first_name} {student.last_name}")

if __name__ == "__main__":
    find_students()