import os
from app import models
from fastapi import HTTPException
from app.models import UserRole
from app.repository.base import BaseRepository

# Quota Limits
MAX_EVENTS_PER_CLASS = int(os.getenv("MAX_EVENTS_PER_CLASS", "1000"))
MAX_SUBJECTS_PER_USER = int(os.getenv("MAX_SUBJECTS_PER_USER", "50")) # Interpreted as per Class
MAX_CLASSES_PER_USER = int(os.getenv("MAX_CLASSES_PER_USER", "10")) # Interpreted as global limit for now
MAX_TOTAL_STORAGE_MB = int(os.getenv("MAX_TOTAL_STORAGE_MB", "100"))

def is_admin(user: models.User):
    # Owner or Admin are exempt
    return user.role in [UserRole.OWNER, UserRole.ADMIN]

def check_event_quota(repo: BaseRepository, user: models.User):
    if is_admin(user):
        return

    count = repo.count_events(user.class_id)
    if count >= MAX_EVENTS_PER_CLASS:
        raise HTTPException(status_code=403, detail=f"Event quota exceeded. Max {MAX_EVENTS_PER_CLASS} events allowed.")

def check_subject_quota(repo: BaseRepository, user: models.User):
    if is_admin(user):
        return

    count = repo.count_subjects(user.class_id)
    if count >= MAX_SUBJECTS_PER_USER:
        raise HTTPException(status_code=403, detail=f"Subject quota exceeded. Max {MAX_SUBJECTS_PER_USER} subjects allowed.")

def check_class_quota(repo: BaseRepository):
    # Global class limit check - Not strictly implemented in Repo yet
    # We skipped this in auth.py too for now.
    pass

def check_storage_quota():
    # Check SQLite DB size via generic OS check - valid for SQL mode.
    # For Appwrite, we rely on Appwrite quotas.
    if os.getenv("APPWRITE", "").lower() == "true":
        return

    db_path = "app.db" # Check database.py or env
    # Simplification: Assume app.db or check if exists
    if os.path.exists("classly.db"):
         # Default name in database.py is classly.db? No, database.py says "sqlite:///./classly.db"
         db_path = "classly.db"
    
    if os.path.exists(db_path):
        size_bytes = os.path.getsize(db_path)
        size_mb = size_bytes / (1024 * 1024)
        if size_mb >= MAX_TOTAL_STORAGE_MB:
             raise HTTPException(status_code=507, detail=f"Storage quota exceeded. Max {MAX_TOTAL_STORAGE_MB} MB allowed.")
