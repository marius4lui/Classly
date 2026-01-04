from sqlalchemy.orm import Session
from app import models
import datetime

# --- Class CRUD ---
def create_class(db: Session, name: str, join_token: str):
    db_class = models.Class(name=name, join_token=join_token)
    db.add(db_class)
    db.commit()
    db.refresh(db_class)
    return db_class

def get_class_by_token(db: Session, join_token: str):
    return db.query(models.Class).filter(models.Class.join_token == join_token).first()

def get_class(db: Session, class_id: str):
    return db.query(models.Class).filter(models.Class.id == class_id).first()

# --- User CRUD ---
def create_user(db: Session, name: str, class_id: str, role: models.UserRole = models.UserRole.MEMBER):
    db_user = models.User(name=name, class_id=class_id, role=role)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user(db: Session, user_id: str):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_session(db: Session, session_token: str):
    return db.query(models.User).filter(models.User.session_token == session_token).first()

def get_class_members(db: Session, class_id: str):
    return db.query(models.User).filter(models.User.class_id == class_id).all()

def delete_user(db: Session, user_id: str):
    user = get_user(db, user_id)
    if user:
        db.delete(user)
        db.commit()
        return True
    return False

# --- Subject CRUD ---
def create_subject(db: Session, class_id: str, name: str, color: str = "#666666"):
    db_subject = models.Subject(class_id=class_id, name=name, color=color)
    db.add(db_subject)
    db.commit()
    db.refresh(db_subject)
    return db_subject

def get_subjects_for_class(db: Session, class_id: str):
    return db.query(models.Subject).filter(models.Subject.class_id == class_id).order_by(models.Subject.name).all()

def delete_subject(db: Session, subject_id: str):
    subject = db.query(models.Subject).filter(models.Subject.id == subject_id).first()
    if subject:
        db.delete(subject)
        db.commit()
        return True
    return False

def get_subject(db: Session, subject_id: str):
    return db.query(models.Subject).filter(models.Subject.id == subject_id).first()

# --- Event CRUD ---
def create_event(db: Session, class_id: str, author_id: str, type: models.EventType, date: datetime.datetime, subject_id: str = None, subject_name: str = None, title: str = None):
    db_event = models.Event(
        class_id=class_id,
        author_id=author_id,
        type=type,
        subject_id=subject_id,
        subject_name=subject_name,
        date=date,
        title=title
    )
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event

def get_events_for_class(db: Session, class_id: str):
    return db.query(models.Event).filter(models.Event.class_id == class_id).order_by(models.Event.date).all()

def delete_event(db: Session, event_id: str):
    event = db.query(models.Event).filter(models.Event.id == event_id).first()
    if event:
        db.delete(event)
        db.commit()
        return True
    return False
