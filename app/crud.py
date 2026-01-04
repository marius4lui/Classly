from sqlalchemy.orm import Session
from passlib.context import CryptContext
from app import models
import datetime
import secrets

# Use argon2 instead of bcrypt (bcrypt has compatibility issues on some systems)
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

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
def create_user(db: Session, name: str, class_id: str, role: models.UserRole = models.UserRole.MEMBER, email: str = None, password: str = None):
    db_user = models.User(name=name, class_id=class_id, role=role)
    # Handle empty strings from HTML forms
    email = email.strip() if email else None
    password = password.strip() if password else None
    if email and password and len(password) >= 8:
        db_user.email = email
        db_user.password_hash = hash_password(password)
        db_user.is_registered = True
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_user(db: Session, user_id: str):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_user_by_session(db: Session, session_token: str):
    return db.query(models.User).filter(models.User.session_token == session_token).first()

def get_user_by_caldav_token(db: Session, caldav_token: str):
    return db.query(models.User).filter(
        models.User.caldav_token == caldav_token,
        models.User.caldav_enabled == True
    ).first()

def get_class_members(db: Session, class_id: str):
    return db.query(models.User).filter(models.User.class_id == class_id).all()

def delete_user(db: Session, user_id: str):
    user = get_user(db, user_id)
    if user:
        db.delete(user)
        db.commit()
        return True
    return False

def update_user_role(db: Session, user_id: str, role: models.UserRole):
    user = get_user(db, user_id)
    if user:
        user.role = role
        db.commit()
        return user
    return None

def register_user(db: Session, user_id: str, email: str, password: str):
    user = get_user(db, user_id)
    if user:
        email = email.strip() if email else None
        password = password.strip() if password else None
        if not email or not password or len(password) < 8:
            return None
        user.email = email
        user.password_hash = hash_password(password)
        user.is_registered = True
        db.commit()
        return user
    return None

def regenerate_session_token(db: Session, user_id: str):
    user = get_user(db, user_id)
    if user:
        user.session_token = secrets.token_urlsafe(32)
        db.commit()
        return user
    return None

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

# --- Login Token CRUD ---
def create_login_token(db: Session, class_id: str, created_by: str, user_id: str = None, user_name: str = None, max_uses: int = None, expires_at: datetime.datetime = None):
    """Create a login token for a specific user (existing or new by name)"""
    db_token = models.LoginToken(
        class_id=class_id,
        created_by=created_by,
        user_id=user_id,
        user_name=user_name,
        max_uses=max_uses,
        expires_at=expires_at
    )
    db.add(db_token)
    db.commit()
    db.refresh(db_token)
    return db_token

def get_login_token(db: Session, token: str):
    return db.query(models.LoginToken).filter(models.LoginToken.token == token).first()

def get_login_tokens_for_class(db: Session, class_id: str):
    return db.query(models.LoginToken).filter(models.LoginToken.class_id == class_id).order_by(models.LoginToken.created_at.desc()).all()

def use_login_token(db: Session, token: str):
    """Returns the token if valid, increments uses, returns None if invalid/expired"""
    login_token = get_login_token(db, token)
    if not login_token:
        return None
    
    # Check expiration
    if login_token.expires_at and login_token.expires_at < datetime.datetime.utcnow():
        return None
    
    # Check max uses
    if login_token.max_uses is not None and login_token.uses >= login_token.max_uses:
        return None
    
    # Increment uses
    login_token.uses += 1
    db.commit()
    return login_token

def delete_login_token(db: Session, token_id: str):
    token = db.query(models.LoginToken).filter(models.LoginToken.id == token_id).first()
    if token:
        db.delete(token)
        db.commit()
        return True
    return False

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

# --- CalDAV ---
def enable_caldav(db: Session, user_id: str, write: bool = False):
    user = get_user(db, user_id)
    if user:
        user.caldav_enabled = True
        user.caldav_write = write
        user.caldav_token = secrets.token_urlsafe(32)  # Regenerate for security
        db.commit()
        return user
    return None

def disable_caldav(db: Session, user_id: str):
    user = get_user(db, user_id)
    if user:
        user.caldav_enabled = False
        db.commit()
        return user
    return None

# --- Event Extended ---
def get_event(db: Session, event_id: str):
    return db.query(models.Event).filter(models.Event.id == event_id).first()

def update_event(db: Session, event_id: str, type: models.EventType = None, subject_name: str = None, 
                 title: str = None, date: datetime.datetime = None):
    event = get_event(db, event_id)
    if event:
        if type: event.type = type
        if subject_name is not None: event.subject_name = subject_name
        if title is not None: event.title = title
        if date: event.date = date
        db.commit()
        db.refresh(event)
        return event
    return None

# --- Event Topics ---
def create_event_topic(db: Session, event_id: str, topic_type: str, content: str = None, count: int = None, order: int = 0):
    db_topic = models.EventTopic(
        event_id=event_id,
        topic_type=topic_type,
        content=content,
        count=count,
        order=order
    )
    db.add(db_topic)
    db.commit()
    db.refresh(db_topic)
    return db_topic

def get_topics_for_event(db: Session, event_id: str):
    return db.query(models.EventTopic).filter(models.EventTopic.event_id == event_id).order_by(models.EventTopic.order).all()

def delete_topic(db: Session, topic_id: str):
    topic = db.query(models.EventTopic).filter(models.EventTopic.id == topic_id).first()
    if topic:
        db.delete(topic)
        db.commit()
        return True
    return False

# --- Audit Logs ---
def create_audit_log(db: Session, class_id: str, user_id: str, action: models.AuditAction, 
                     target_id: str = None, data: str = None, permanent: bool = False):
    db_log = models.AuditLog(
        class_id=class_id,
        user_id=user_id,
        action=action,
        target_id=target_id,
        data=data,
        permanent=permanent
    )
    db.add(db_log)
    db.commit()
    return db_log

def cleanup_old_audit_logs(db: Session):
    """Delete non-permanent audit logs older than 90 days"""
    cutoff = datetime.datetime.utcnow() - datetime.timedelta(days=90)
    deleted = db.query(models.AuditLog).filter(
        models.AuditLog.permanent == False,
        models.AuditLog.created_at < cutoff
    ).delete()
    db.commit()
    return deleted

def get_audit_logs_for_class(db: Session, class_id: str, limit: int = 50):
    return db.query(models.AuditLog).filter(
        models.AuditLog.class_id == class_id
    ).order_by(models.AuditLog.created_at.desc()).limit(limit).all()
