from sqlalchemy import Column, Integer, String, Boolean
from database import Base

class Syllabus(Base):
    __tablename__ = "syllabus"
    id = Column(Integer, primary_key=True, index=True)
    topic_name = Column(String)
    month = Column(String)
    is_completed = Column(Boolean, default=False)

class StudentMark(Base):
    __tablename__ = "student_marks"
    id = Column(Integer, primary_key=True, index=True)
    student_name = Column(String)
    student_email = Column(String, index=True)
    score = Column(Integer)
    total_marks = Column(Integer)
    month_index = Column(Integer)
    remarks = Column(String, default="No remarks yet.")
    target_score = Column(Integer, default=75)

class Teacher(Base):
    __tablename__ = "teachers"
    # id is the only primary key, and it auto-increments
    id = Column(Integer, primary_key=True, index=True, autoincrement=True) 
    # emp_id is unique so no two teachers have the same ID
    emp_id = Column(String, unique=True, index=True) 
    name = Column(String)
    # pin is NOT unique, allowing different teachers to have the same PIN
    pin = Column(String)