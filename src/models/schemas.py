from __future__ import annotations
from typing import Optional, List
from pydantic import BaseModel, Field

class Student(BaseModel):
    id: Optional[int] = Field(default=None)
    first_name: str
    last_name: str
    class_id: int
    aggregate: Optional[float] = None

class Subject(BaseModel):
    id: Optional[int] = None
    name: str
    code: str
    category: str

class Mark(BaseModel):
    id: Optional[int] = None
    student_id: int
    subject_id: int
    term: str
    score: float = Field(ge=0, le=100)

class ReportRequest(BaseModel):
    student_id: int
    term: str
