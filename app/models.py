import enum
import datetime
import uuid
import secrets
from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Boolean, Enum, Float, Time
from sqlalchemy.orm import relationship
from app.database import Base

def generate_uuid():
    return str(uuid.uuid4())

def generate_token():
    return secrets.token_urlsafe(32)

class UserRole(str, enum.Enum):
    OWNER = "owner"
    ADMIN = "admin"
    CLASS_ADMIN = "class_admin"
    MEMBER = "member"
    GUEST = "guest"

class EventType(str, enum.Enum):
    KA = "KA"
    TEST = "TEST"
    HA = "HA"
    INFO = "INFO"

class Priority(str, enum.Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"

class Class(Base):
    __tablename__ = "classes"

    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String, nullable=False)
    join_token = Column(String, unique=True, index=True, nullable=False)
    owner_id = Column(String, nullable=True)
    join_enabled = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    users = relationship("User", back_populates="clazz")
    events = relationship("Event", back_populates="clazz")
    subjects = relationship("Subject", back_populates="clazz")
    login_tokens = relationship("LoginToken", back_populates="clazz")
    audit_logs = relationship("AuditLog", back_populates="clazz")
    integration_tokens = relationship("IntegrationToken", back_populates="clazz")

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String, nullable=False)
    class_id = Column(String, ForeignKey("classes.id"), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.MEMBER)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Session token for cookie auth
    session_token = Column(String, default=generate_token)
    
    # Admin auth fields (optional - only for registered admins)
    email = Column(String, unique=True, nullable=True, index=True)
    password_hash = Column(String, nullable=True)
    is_registered = Column(Boolean, default=False)
    
    # CalDAV fields
    caldav_token = Column(String, default=generate_token)
    caldav_enabled = Column(Boolean, default=False)
    caldav_write = Column(Boolean, default=False)

    clazz = relationship("Class", back_populates="users")
    events = relationship("Event", back_populates="author")
    integration_tokens = relationship("IntegrationToken", back_populates="user")

class Subject(Base):
    __tablename__ = "subjects"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    class_id = Column(String, ForeignKey("classes.id"), nullable=False)
    name = Column(String, nullable=False)
    color = Column(String, default="#666666")
    
    clazz = relationship("Class", back_populates="subjects")

class LoginToken(Base):
    """Login tokens for specific users - existing or new"""
    __tablename__ = "login_tokens"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    class_id = Column(String, ForeignKey("classes.id"), nullable=False)
    token = Column(String, unique=True, index=True, default=generate_token)
    
    # Link to existing user OR name for new user
    user_id = Column(String, ForeignKey("users.id"), nullable=True)  # Existing user
    user_name = Column(String, nullable=True)  # Name for new user if user_id is None
    
    # Usage limits
    max_uses = Column(Integer, nullable=True)  # None = unlimited
    uses = Column(Integer, default=0)
    
    # Role for new users
    role = Column(Enum(UserRole), default=UserRole.MEMBER)
    
    # Expiration
    expires_at = Column(DateTime, nullable=True)
    
    # Metadata
    created_by = Column(String, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    clazz = relationship("Class", back_populates="login_tokens")
    user = relationship("User", foreign_keys=[user_id])
    creator = relationship("User", foreign_keys=[created_by])


class IntegrationToken(Base):
    """Personal Access Tokens for API integrations (read-only for now)"""
    __tablename__ = "integration_tokens"

    id = Column(String, primary_key=True, default=generate_uuid)
    token = Column(String, unique=True, index=True, default=generate_token)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    class_id = Column(String, ForeignKey("classes.id"), nullable=False)
    scopes = Column(String, default="read:events")  # Comma-separated scopes
    expires_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    last_used_at = Column(DateTime, nullable=True)
    revoked = Column(Boolean, default=False)

    user = relationship("User", back_populates="integration_tokens")
    clazz = relationship("Class", back_populates="integration_tokens")

class Event(Base):
    __tablename__ = "events"

    id = Column(String, primary_key=True, default=generate_uuid)
    class_id = Column(String, ForeignKey("classes.id"), nullable=False)
    type = Column(Enum(EventType), nullable=False)
    priority = Column(Enum(Priority), default=Priority.MEDIUM)
    subject_id = Column(String, ForeignKey("subjects.id"), nullable=True)
    subject_name = Column(String, nullable=True)
    title = Column(String, nullable=True)
    date = Column(DateTime, nullable=True)
    author_id = Column(String, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    clazz = relationship("Class", back_populates="events")
    author = relationship("User", back_populates="events")
    topics = relationship("EventTopic", back_populates="event", cascade="all, delete-orphan")
    links = relationship("EventLink", back_populates="event", cascade="all, delete-orphan")

class EventTopic(Base):
    """Topics for KA/TEST events - supports hierarchical structure"""
    __tablename__ = "event_topics"

    id = Column(String, primary_key=True, default=generate_uuid)
    event_id = Column(String, ForeignKey("events.id"), nullable=False)
    topic_type = Column(String, nullable=False)  # e.g. "Vokabeln", "Grammatik"
    content = Column(String, nullable=True)  # e.g. "Page 20" (legacy?)
    count = Column(Integer, nullable=True)  # Legacy: e.g. 50 words
    pages = Column(String, nullable=True)  # e.g. "S. 10-15"
    order = Column(Integer, default=0)
    parent_id = Column(String, ForeignKey("event_topics.id"), nullable=True)  # For hierarchical structure

    event = relationship("Event", back_populates="topics")
    parent = relationship("EventTopic", remote_side=[id], backref="children")

class EventLink(Base):
    """Links for events"""
    __tablename__ = "event_links"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    event_id = Column(String, ForeignKey("events.id"), nullable=False)
    url = Column(String, nullable=False)
    label = Column(String, nullable=False)
    
    event = relationship("Event", back_populates="links")

class AuditAction(str, enum.Enum):
    EVENT_CREATE = "event_create"
    EVENT_EDIT = "event_edit"
    EVENT_DELETE = "event_delete"
    TOPIC_ADD = "topic_add"
    USER_JOIN = "user_join"
    USER_LEAVE = "user_leave"
    LOGIN = "login"

class AuditLog(Base):
    """Audit logs - auto-delete after 90 days except permanent ones"""
    __tablename__ = "audit_logs"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    class_id = Column(String, ForeignKey("classes.id"), nullable=False)
    user_id = Column(String, ForeignKey("users.id"), nullable=True)
    action = Column(Enum(AuditAction), nullable=False)
    target_id = Column(String, nullable=True)  # Event ID, User ID, etc.
    data = Column(String, nullable=True)  # JSON for extra details
    permanent = Column(Boolean, default=False)  # Event-related logs are permanent
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    clazz = relationship("Class", back_populates="audit_logs")
    user = relationship("User")

class UserPreferences(Base):
    __tablename__ = "user_preferences"

    user_id = Column(String, ForeignKey("users.id"), primary_key=True)
    filter_subjects = Column(String, default="[]")  # JSON list of subjects
    filter_event_types = Column(String, default="[]")  # JSON list of types
    filter_priority = Column(String, default="[]")  # JSON list of priorities (high, medium, low)

    user = relationship("User", backref="preferences")

class Grade(Base):
    """Private grades for registered users - only visible to the user who created them"""
    __tablename__ = "grades"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    event_id = Column(String, ForeignKey("events.id"), nullable=False)
    grade = Column(Float, nullable=False)  # 1.0 - 6.0 (German grading scale)
    weight = Column(Float, default=1.0)  # Weight for averaging (e.g. KA=1.0, Test=0.5)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    user = relationship("User", backref="grades")
    event = relationship("Event", backref="grades")

# === Timetable Models ===

class TimetableSettings(Base):
    """Stundenplan-Einstellungen pro Klasse"""
    __tablename__ = "timetable_settings"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    class_id = Column(String, ForeignKey("classes.id"), unique=True, nullable=False)
    slot_duration = Column(Integer, default=45)  # Minuten pro Stunde
    break_duration = Column(Integer, default=15)  # Minuten Pause
    day_start_hour = Column(Integer, default=8)   # Startzeit Stunde (08:00)
    day_start_minute = Column(Integer, default=0)
    day_end_hour = Column(Integer, default=16)    # Endzeit Stunde (16:00)
    day_end_minute = Column(Integer, default=0)
    
    clazz = relationship("Class", backref="timetable_settings")

class TimetableSlot(Base):
    """Ein Zeitslot im Stundenplan - von Admin erstellt"""
    __tablename__ = "timetable_slots"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    class_id = Column(String, ForeignKey("classes.id"), nullable=False)
    weekday = Column(Integer, nullable=False)  # 0=Mo, 1=Di, 2=Mi, 3=Do, 4=Fr
    slot_number = Column(Integer, nullable=False)  # 1, 2, 3... (Stundennummer des Tages)
    subject_id = Column(String, ForeignKey("subjects.id"), nullable=True)
    subject_name = Column(String, nullable=True)  # Fallback/Override für Fachname
    group_name = Column(String, nullable=True)  # z.B. "Bili", "Grundkurs", "LK"
    room = Column(String, nullable=True)
    
    clazz = relationship("Class", backref="timetable_slots")
    subject = relationship("Subject", backref="timetable_slots")

class UserTimetableSelection(Base):
    """User-Auswahl für Kurse/Gruppen - für personalisierten Stundenplan"""
    __tablename__ = "user_timetable_selections"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    slot_id = Column(String, ForeignKey("timetable_slots.id"), nullable=False)
    
    user = relationship("User", backref="timetable_selections")
    slot = relationship("TimetableSlot", backref="user_selections")

