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
    """Shareable login tokens - single or multi-use"""
    __tablename__ = "login_tokens"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    class_id = Column(String, ForeignKey("classes.id"), nullable=False)
    token = Column(String, unique=True, index=True, default=generate_token)
    
    # Usage limits
    max_uses = Column(Integer, nullable=True)  # None = unlimited
    uses = Column(Integer, default=0)
    
    # Expiration
    expires_at = Column(DateTime, nullable=True)
    
    # Metadata
    label = Column(String, nullable=True)  # e.g. "Link für Tom"
    created_by = Column(String, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    clazz = relationship("Class", back_populates="login_tokens")
    creator = relationship("User")

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

    clazz = relationship("Class", back_populates="events")
    author = relationship("User", back_populates="events")
