import os
from sqlalchemy.orm import Session
from app import models, crud
from fastapi import HTTPException
from app.models import UserRole

# Quota Limits
MAX_EVENTS_PER_CLASS = int(os.getenv("MAX_EVENTS_PER_CLASS", "1000"))
MAX_SUBJECTS_PER_USER = int(os.getenv("MAX_SUBJECTS_PER_USER", "50")) # Interpreted as per Class
MAX_CLASSES_PER_USER = int(os.getenv("MAX_CLASSES_PER_USER", "10")) # Interpreted as global limit for now
MAX_TOTAL_STORAGE_MB = int(os.getenv("MAX_TOTAL_STORAGE_MB", "100"))

def is_admin(user: models.User):
    # Owner or Admin are exempt
    return user.role in [UserRole.OWNER, UserRole.ADMIN]

def check_event_quota(db: Session, user: models.User):
    if is_admin(user):
        return

    count = db.query(models.Event).filter(models.Event.class_id == user.class_id).count()
    if count >= MAX_EVENTS_PER_CLASS:
        raise HTTPException(status_code=403, detail=f"Event quota exceeded. Max {MAX_EVENTS_PER_CLASS} events allowed.")

def check_subject_quota(db: Session, user: models.User):
    if is_admin(user):
        return

    count = db.query(models.Subject).filter(models.Subject.class_id == user.class_id).count()
    if count >= MAX_SUBJECTS_PER_USER:
        raise HTTPException(status_code=403, detail=f"Subject quota exceeded. Max {MAX_SUBJECTS_PER_USER} subjects allowed.")

def check_class_quota(db: Session):
    # Global class limit check
    count = db.query(models.Class).count()
    if count >= MAX_CLASSES_PER_USER: # Reusing this env var for global limit as discussed
        raise HTTPException(status_code=403, detail=f"Class quota exceeded. Max {MAX_CLASSES_PER_USER} classes allowed on this server.")

def check_storage_quota():
    # Check SQLite DB size
    # Assuming SQLite
    db_path = "app.db" # Standard path usually, check main/db config
    # In app/database.py it's SQLALCHEMY_DATABASE_URL = "sqlite:///./app.db"

    if os.path.exists("app.db"):
        size_bytes = os.path.getsize("app.db")
        size_mb = size_bytes / (1024 * 1024)
        if size_mb >= MAX_TOTAL_STORAGE_MB:
             raise HTTPException(status_code=507, detail=f"Storage quota exceeded. Max {MAX_TOTAL_STORAGE_MB} MB allowed.")
