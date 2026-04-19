from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
import models
from database import engine, SessionLocal
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
from typing import List

# Create tables in the DB automatically
models.Base.metadata.create_all(bind=engine)

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

def get_db():
    db = SessionLocal()
    try: yield db
    finally: db.close()

# --- SCHEMAS (Matches the Frontend Payloads) ---
class TeacherRegister(BaseModel):
    name: str
    emp_id: str
    pin: str

class TeacherLogin(BaseModel):
    emp_id: str
    pin: str

class StudentReg(BaseModel):
    student_name: str
    student_email: str

class MarksCreate(BaseModel):
    student_name: str
    student_email: str
    score: int
    total_marks: int
    month_index: int
    remarks: str
    target_score: int

class SyllabusCreate(BaseModel):
    topic_name: str
    month: str

# --- TEACHER AUTH ROUTES ---
@app.post("/auth/teacher-register")
def register_teacher(data: TeacherRegister, db: Session = Depends(get_db)):
    existing = db.query(models.Teacher).filter(models.Teacher.emp_id == data.emp_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Employee ID already registered")
    new_teacher = models.Teacher(name=data.name, emp_id=data.emp_id, pin=data.pin)
    db.add(new_teacher)
    db.commit()
    return {"message": "Success"}

@app.post("/auth/teacher-login")
def login_teacher(data: TeacherLogin, db: Session = Depends(get_db)):
    teacher = db.query(models.Teacher).filter(
        models.Teacher.emp_id == data.emp_id, 
        models.Teacher.pin == data.pin
    ).first()
    if not teacher:
        raise HTTPException(status_code=401, detail="Invalid ID or PIN")
    return {"status": "success", "teacher_name": teacher.name}

# --- STUDENT & MARKS ROUTES ---
@app.post("/student/register")
def register_student(item: StudentReg, db: Session = Depends(get_db)):
    email_clean = item.student_email.lower().strip()
    existing = db.query(models.StudentMark).filter(models.StudentMark.student_email == email_clean).first()
    if existing:
        return {"message": "Student already exists!"}
    
    new_student = models.StudentMark(
        student_name=item.student_name,
        student_email=email_clean,
        score=0, total_marks=100, month_index=0, 
        remarks="New Registration", target_score=75
    )
    db.add(new_student)
    db.commit()
    return {"message": f"Successfully Registered {item.student_name}!"}

@app.get("/student/auth/{email}")
def student_auth(email: str, db: Session = Depends(get_db)):
    email_clean = email.lower().strip()
    records = db.query(models.StudentMark).filter(
        models.StudentMark.student_email == email_clean
    ).order_by(models.StudentMark.month_index).all()

    if not records:
        raise HTTPException(status_code=404, detail="Student not registered")

    latest_record = records[-1]
    
    # --- AI Trend Logic with Safety Check ---
    prediction = 70.0 
    try:
        trend = db.execute(
            text("SELECT * FROM student_trends WHERE student_name = :n"), 
            {"n": latest_record.student_name}
        ).mappings().first()

        if trend and trend["improvement_rate"] is not None:
            avg = float(trend["average_score"])
            slope = float(trend["improvement_rate"])
            months_left = 12 - latest_record.month_index
            prediction = avg + (slope * months_left)
        elif trend and trend["average_score"]:
            prediction = float(trend["average_score"])
    except Exception:
        # Fallback if the database view 'student_trends' doesn't exist yet
        prediction = (latest_record.score / latest_record.total_marks) * 100 if latest_record.total_marks > 0 else 70.0

    return {
        "profile": latest_record, 
        "prediction": round(float(max(0, min(100, prediction))), 2)
    }
@app.get("/student/marks/all/{email}")
def get_student_marks(email: str, db: Session = Depends(get_db)):
    email_clean = email.lower().strip()
    
    # This fetches ALL marks for the history table
    records = db.query(models.StudentMark).filter(
        models.StudentMark.student_email == email_clean
    ).order_by(models.StudentMark.month_index).all()
    
    if not records:
        # Instead of 404, return an empty list so the table just shows "No data"
        return []
        
    return records

@app.post("/marks/add")
def add_marks(item: MarksCreate, db: Session = Depends(get_db)):
    item_dict = item.dict()
    item_dict['student_email'] = item_dict['student_email'].lower().strip()
    new_mark = models.StudentMark(**item_dict)
    db.add(new_mark)
    db.commit()
    return {"message": "Success"}

@app.get("/student/marks/all/{email}")
def list_marks(email: str, db: Session = Depends(get_db)):
    email_clean = email.lower().strip()
    return db.query(models.StudentMark).filter(models.StudentMark.student_email == email_clean).all()

# --- CURRICULUM ROUTES ---
@app.post("/curriculum/add")
def add_topic(item: SyllabusCreate, db: Session = Depends(get_db)):
    new_topic = models.Syllabus(topic_name=item.topic_name, month=item.month, is_completed=False)
    db.add(new_topic)
    db.commit()
    return {"message": "Topic Added"}

@app.get("/curriculum/list")
def list_curriculum(db: Session = Depends(get_db)):
    return db.query(models.Syllabus).all()

@app.put("/curriculum/complete/{topic_id}")
def mark_topic_done(topic_id: int, db: Session = Depends(get_db)):
    topic = db.query(models.Syllabus).filter(models.Syllabus.id == topic_id).first()
    if topic:
        topic.is_completed = True
        db.commit()
    return {"message": "Updated"}
@app.get("/curriculum/progress")
def get_progress(db: Session = Depends(get_db)):
    all_topics = db.query(models.Syllabus).all()
    if not all_topics:
        return {"progress_percent": 0, "topics_left": 0}
    
    total = len(all_topics)
    completed = db.query(models.Syllabus).filter(models.Syllabus.is_completed == True).count()
    percent = int((completed / total) * 100)
    return {"progress_percent": percent, "topics_left": total - completed}