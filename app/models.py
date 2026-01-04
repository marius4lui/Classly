import enum
import datetime
import uuid
import secrets
from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Boolean, Enum
from sqlalchemy.orm import relationship
from app.database import Base

def generate_uuid():
    return str(uuid.uuid4())

def generate_token():
    return secrets.token_urlsafe(32)

class UserRole(str, enum.Enum):
    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"
    GUEST = "guest"

class EventType(str, enum.Enum):
    KA = "KA"
    TEST = "TEST"
    HA = "HA"
    INFO = "INFO"

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

class Event(Base):
    __tablename__ = "events"

    id = Column(String, primary_key=True, default=generate_uuid)
    class_id = Column(String, ForeignKey("classes.id"), nullable=False)
    type = Column(Enum(EventType), nullable=False)
    subject_id = Column(String, ForeignKey("subjects.id"), nullable=True)
    subject_name = Column(String, nullable=True)
    title = Column(String, nullable=True)
    date = Column(DateTime, nullable=False)
    author_id = Column(String, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    clazz = relationship("Class", back_populates="events")
    author = relationship("User", back_populates="events")
    topics = relationship("EventTopic", back_populates="event", cascade="all, delete-orphan")
    links = relationship("EventLink", back_populates="event", cascade="all, delete-orphan")

class EventTopic(Base):
    """Topics for KA/TEST events"""
    __tablename__ = "event_topics"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    event_id = Column(String, ForeignKey("events.id"), nullable=False)
    topic_type = Column(String, nullable=False)  # e.g. "Vokabeln", "Grammatik"
    content = Column(String, nullable=True)  # e.g. "Page 20"
    count = Column(Integer, nullable=True)  # e.g. 50 words
    order = Column(Integer, default=0)
    
    event = relationship("Event", back_populates="topics")

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
    
    clazz = relationship("Class")
    user = relationship("User")
