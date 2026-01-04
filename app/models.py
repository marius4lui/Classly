import enum
import datetime
import uuid
from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Boolean, Enum
from sqlalchemy.orm import relationship
from app.database import Base

def generate_uuid():
    return str(uuid.uuid4())

class UserRole(str, enum.Enum):
    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"

class EventType(str, enum.Enum):
    KA = "KA"     # Klassenarbeit
    TEST = "TEST" # Test
    HA = "HA"     # Hausaufgabe
    INFO = "INFO" # Sonstiges

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

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String, nullable=False)
    class_id = Column(String, ForeignKey("classes.id"), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.MEMBER)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    session_token = Column(String, default=generate_uuid)

    clazz = relationship("Class", back_populates="users")
    events = relationship("Event", back_populates="author")

class Subject(Base):
    """Fächer pro Klasse"""
    __tablename__ = "subjects"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    class_id = Column(String, ForeignKey("classes.id"), nullable=False)
    name = Column(String, nullable=False)  # z.B. "Mathe", "Deutsch"
    color = Column(String, default="#666666")  # Optional color
    
    clazz = relationship("Class", back_populates="subjects")

class Event(Base):
    __tablename__ = "events"

    id = Column(String, primary_key=True, default=generate_uuid)
    class_id = Column(String, ForeignKey("classes.id"), nullable=False)
    type = Column(Enum(EventType), nullable=False)
    subject_id = Column(String, ForeignKey("subjects.id"), nullable=True)
    subject_name = Column(String, nullable=True)  # Fallback if no subject_id
    title = Column(String, nullable=True)
    date = Column(DateTime, nullable=False)
    author_id = Column(String, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    clazz = relationship("Class", back_populates="events")
    author = relationship("User", back_populates="events")
