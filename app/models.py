import enum
import datetime
import uuid
import secrets
from sqlalchemy import (
    String,
    Integer,
    ForeignKey,
    DateTime,
    Boolean,
    Enum,
    Float,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

# Keep legacy nullability explicit: Python defaults do not imply NOT NULL.
# Optional annotations reflect values that can already exist in stored rows.


def generate_uuid() -> str:
    return str(uuid.uuid4())


def generate_token() -> str:
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

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=generate_uuid, nullable=False
    )
    name: Mapped[str] = mapped_column(String, nullable=False)
    join_token: Mapped[str] = mapped_column(
        String, unique=True, index=True, nullable=False
    )
    owner_id: Mapped[str | None] = mapped_column(String, nullable=True)
    join_enabled: Mapped[bool | None] = mapped_column(
        Boolean, default=True, nullable=True
    )
    # Public share link for timetable (read-only). Token should be non-guessable.
    timetable_public_enabled: Mapped[bool | None] = mapped_column(
        Boolean, default=False, nullable=True
    )
    timetable_public_token: Mapped[str | None] = mapped_column(
        String, nullable=True, index=True
    )
    created_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime, default=datetime.datetime.utcnow, nullable=True
    )

    users: Mapped[list["User"]] = relationship("User", back_populates="clazz")
    events: Mapped[list["Event"]] = relationship("Event", back_populates="clazz")
    subjects: Mapped[list["Subject"]] = relationship("Subject", back_populates="clazz")
    login_tokens: Mapped[list["LoginToken"]] = relationship(
        "LoginToken", back_populates="clazz"
    )
    audit_logs: Mapped[list["AuditLog"]] = relationship(
        "AuditLog", back_populates="clazz"
    )
    integration_tokens: Mapped[list["IntegrationToken"]] = relationship(
        "IntegrationToken", back_populates="clazz"
    )

    timetable_settings: Mapped[list["TimetableSettings"]] = relationship(
        back_populates="clazz"
    )
    timetable_slots: Mapped[list["TimetableSlot"]] = relationship(
        back_populates="clazz"
    )


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=generate_uuid, nullable=False
    )
    name: Mapped[str] = mapped_column(String, nullable=False)
    class_id: Mapped[str] = mapped_column(
        String, ForeignKey("classes.id"), nullable=False
    )
    role: Mapped[UserRole | None] = mapped_column(
        Enum(UserRole), default=UserRole.MEMBER, nullable=True
    )
    created_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime, default=datetime.datetime.utcnow, nullable=True
    )

    # Session token for cookie auth
    session_token: Mapped[str | None] = mapped_column(
        String, default=generate_token, nullable=True
    )

    # Admin auth fields (optional - only for registered admins)
    email: Mapped[str | None] = mapped_column(
        String, unique=True, nullable=True, index=True
    )
    password_hash: Mapped[str | None] = mapped_column(String, nullable=True)
    is_registered: Mapped[bool | None] = mapped_column(
        Boolean, default=False, nullable=True
    )

    # Preferences
    language: Mapped[str | None] = mapped_column(String, default="de", nullable=True)

    # CalDAV fields
    caldav_token: Mapped[str | None] = mapped_column(
        String, default=generate_token, nullable=True
    )
    caldav_enabled: Mapped[bool | None] = mapped_column(
        Boolean, default=False, nullable=True
    )
    caldav_write: Mapped[bool | None] = mapped_column(
        Boolean, default=False, nullable=True
    )

    clazz: Mapped["Class"] = relationship("Class", back_populates="users")
    events: Mapped[list["Event"]] = relationship("Event", back_populates="author")
    integration_tokens: Mapped[list["IntegrationToken"]] = relationship(
        "IntegrationToken",
        back_populates="user",
        foreign_keys="IntegrationToken.user_id",
    )

    preferences: Mapped[list["UserPreferences"]] = relationship(back_populates="user")
    grades: Mapped[list["Grade"]] = relationship(back_populates="user")
    timetable_selections: Mapped[list["UserTimetableSelection"]] = relationship(
        back_populates="user"
    )
    device_tokens: Mapped[list["DeviceToken"]] = relationship(back_populates="user")


class Subject(Base):
    __tablename__ = "subjects"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=generate_uuid, nullable=False
    )
    class_id: Mapped[str] = mapped_column(
        String, ForeignKey("classes.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(String, nullable=False)
    color: Mapped[str | None] = mapped_column(String, default="#666666", nullable=True)

    clazz: Mapped["Class"] = relationship("Class", back_populates="subjects")

    timetable_slots: Mapped[list["TimetableSlot"]] = relationship(
        back_populates="subject"
    )


class LoginToken(Base):
    """Login tokens for specific users - existing or new"""

    __tablename__ = "login_tokens"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=generate_uuid, nullable=False
    )
    class_id: Mapped[str] = mapped_column(
        String, ForeignKey("classes.id"), nullable=False
    )
    token: Mapped[str | None] = mapped_column(
        String, unique=True, index=True, default=generate_token, nullable=True
    )

    # Link to existing user OR name for new user
    user_id: Mapped[str | None] = mapped_column(
        String, ForeignKey("users.id"), nullable=True
    )  # Existing user
    user_name: Mapped[str | None] = mapped_column(
        String, nullable=True
    )  # Name for new user if user_id is None

    # Usage limits
    max_uses: Mapped[int | None] = mapped_column(
        Integer, nullable=True
    )  # None = unlimited
    uses: Mapped[int | None] = mapped_column(Integer, default=0, nullable=True)

    # Role for new users
    role: Mapped[UserRole | None] = mapped_column(
        Enum(UserRole), default=UserRole.MEMBER, nullable=True
    )

    # Expiration
    expires_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime, nullable=True
    )

    # Metadata
    created_by: Mapped[str] = mapped_column(
        String, ForeignKey("users.id"), nullable=False
    )
    created_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime, default=datetime.datetime.utcnow, nullable=True
    )

    clazz: Mapped["Class"] = relationship("Class", back_populates="login_tokens")
    user: Mapped["User | None"] = relationship("User", foreign_keys=[user_id])
    creator: Mapped["User"] = relationship("User", foreign_keys=[created_by])


class IntegrationToken(Base):
    """API Keys für externe Integrationen (Admin-generiert)"""

    __tablename__ = "integration_tokens"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=generate_uuid, nullable=False
    )

    # Menschenlesbarer Name für den Key
    name: Mapped[str | None] = mapped_column(String, nullable=True)

    # Legacy: Klartext-Token (für Rückwärtskompatibilität)
    token: Mapped[str | None] = mapped_column(
        String, unique=True, index=True, default=generate_token, nullable=True
    )

    # NEU: Hash-basierte Speicherung (SHA-256)
    token_hash: Mapped[str | None] = mapped_column(
        String, unique=True, index=True, nullable=True
    )
    token_prefix: Mapped[str | None] = mapped_column(
        String, nullable=True
    )  # z.B. "cl_...abc" für Identifikation

    user_id: Mapped[str] = mapped_column(String, ForeignKey("users.id"), nullable=False)
    class_id: Mapped[str] = mapped_column(
        String, ForeignKey("classes.id"), nullable=False
    )

    # Von welchem Admin erstellt (für Audit)
    created_by: Mapped[str | None] = mapped_column(
        String, ForeignKey("users.id"), nullable=True
    )

    # Granulare Scopes (z.B. "classes:read,events:read,events:write")
    scopes: Mapped[str | None] = mapped_column(
        String, default="read:events", nullable=True
    )

    # Rate-Limiting pro Key
    rate_limit_per_minute: Mapped[int | None] = mapped_column(
        Integer, default=60, nullable=True
    )

    # IP-Allowlist (JSON-Array als String, z.B. '["192.168.1.0/24"]')
    ip_allowlist: Mapped[str | None] = mapped_column(String, nullable=True)

    expires_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime, nullable=True
    )
    created_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime, default=datetime.datetime.utcnow, nullable=True
    )
    last_used_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime, nullable=True
    )
    revoked: Mapped[bool | None] = mapped_column(Boolean, default=False, nullable=True)
    revoked_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime, nullable=True
    )

    user: Mapped["User"] = relationship(
        "User", foreign_keys=[user_id], back_populates="integration_tokens"
    )
    creator: Mapped["User | None"] = relationship("User", foreign_keys=[created_by])
    clazz: Mapped["Class"] = relationship("Class", back_populates="integration_tokens")


class Event(Base):
    __tablename__ = "events"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=generate_uuid, nullable=False
    )
    class_id: Mapped[str] = mapped_column(
        String, ForeignKey("classes.id"), nullable=False
    )
    type: Mapped[EventType] = mapped_column(Enum(EventType), nullable=False)
    priority: Mapped[Priority | None] = mapped_column(
        Enum(Priority), default=Priority.MEDIUM, nullable=True
    )
    subject_id: Mapped[str | None] = mapped_column(
        String, ForeignKey("subjects.id"), nullable=True
    )
    subject_name: Mapped[str | None] = mapped_column(String, nullable=True)
    title: Mapped[str | None] = mapped_column(String, nullable=True)
    date: Mapped[datetime.datetime | None] = mapped_column(DateTime, nullable=True)
    author_id: Mapped[str] = mapped_column(
        String, ForeignKey("users.id"), nullable=False
    )
    created_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime, default=datetime.datetime.utcnow, nullable=True
    )
    updated_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime,
        default=datetime.datetime.utcnow,
        onupdate=datetime.datetime.utcnow,
        nullable=True,
    )

    clazz: Mapped["Class"] = relationship("Class", back_populates="events")
    author: Mapped["User"] = relationship("User", back_populates="events")
    topics: Mapped[list["EventTopic"]] = relationship(
        "EventTopic", back_populates="event", cascade="all, delete-orphan"
    )
    links: Mapped[list["EventLink"]] = relationship(
        "EventLink", back_populates="event", cascade="all, delete-orphan"
    )

    grades: Mapped[list["Grade"]] = relationship(back_populates="event")


class EventTopic(Base):
    """Topics for KA/TEST events - supports hierarchical structure"""

    __tablename__ = "event_topics"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=generate_uuid, nullable=False
    )
    event_id: Mapped[str] = mapped_column(
        String, ForeignKey("events.id"), nullable=False
    )
    topic_type: Mapped[str] = mapped_column(
        String, nullable=False
    )  # e.g. "Vokabeln", "Grammatik"
    content: Mapped[str | None] = mapped_column(
        String, nullable=True
    )  # e.g. "Page 20" (legacy?)
    count: Mapped[int | None] = mapped_column(
        Integer, nullable=True
    )  # Legacy: e.g. 50 words
    pages: Mapped[str | None] = mapped_column(String, nullable=True)  # e.g. "S. 10-15"
    order: Mapped[int | None] = mapped_column(Integer, default=0, nullable=True)
    parent_id: Mapped[str | None] = mapped_column(
        String, ForeignKey("event_topics.id"), nullable=True
    )  # For hierarchical structure

    event: Mapped["Event"] = relationship("Event", back_populates="topics")
    parent: Mapped["EventTopic | None"] = relationship(
        "EventTopic", remote_side=[id], back_populates="children"
    )

    children: Mapped[list["EventTopic"]] = relationship(back_populates="parent")


class EventLink(Base):
    """Links for events"""

    __tablename__ = "event_links"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=generate_uuid, nullable=False
    )
    event_id: Mapped[str] = mapped_column(
        String, ForeignKey("events.id"), nullable=False
    )
    url: Mapped[str] = mapped_column(String, nullable=False)
    label: Mapped[str] = mapped_column(String, nullable=False)

    event: Mapped["Event"] = relationship("Event", back_populates="links")


class AuditAction(str, enum.Enum):
    EVENT_CREATE = "event_create"
    EVENT_EDIT = "event_edit"
    EVENT_DELETE = "event_delete"
    TOPIC_ADD = "topic_add"
    USER_JOIN = "user_join"
    USER_LEAVE = "user_leave"
    LOGIN = "login"

    # API-Key Actions
    API_KEY_CREATE = "api_key_create"
    API_KEY_REVOKE = "api_key_revoke"
    API_KEY_ROTATE = "api_key_rotate"
    API_ACCESS = "api_access"


class AuditLog(Base):
    """Audit logs - auto-delete after 90 days except permanent ones"""

    __tablename__ = "audit_logs"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=generate_uuid, nullable=False
    )
    class_id: Mapped[str] = mapped_column(
        String, ForeignKey("classes.id"), nullable=False
    )
    user_id: Mapped[str | None] = mapped_column(
        String, ForeignKey("users.id"), nullable=True
    )
    action: Mapped[AuditAction] = mapped_column(Enum(AuditAction), nullable=False)
    target_id: Mapped[str | None] = mapped_column(
        String, nullable=True
    )  # Event ID, User ID, etc.
    data: Mapped[str | None] = mapped_column(
        String, nullable=True
    )  # JSON for extra details
    permanent: Mapped[bool | None] = mapped_column(
        Boolean, default=False, nullable=True
    )  # Event-related logs are permanent
    created_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime, default=datetime.datetime.utcnow, nullable=True
    )

    clazz: Mapped["Class"] = relationship("Class", back_populates="audit_logs")
    user: Mapped["User | None"] = relationship("User")


class UserPreferences(Base):
    __tablename__ = "user_preferences"

    user_id: Mapped[str] = mapped_column(
        String, ForeignKey("users.id"), primary_key=True, nullable=False
    )
    filter_subjects: Mapped[str | None] = mapped_column(
        String, default="[]", nullable=True
    )  # JSON list of subjects
    filter_event_types: Mapped[str | None] = mapped_column(
        String, default="[]", nullable=True
    )  # JSON list of types
    filter_priority: Mapped[str | None] = mapped_column(
        String, default="[]", nullable=True
    )  # JSON list of priorities (high, medium, low)

    user: Mapped["User"] = relationship("User", back_populates="preferences")


class Grade(Base):
    """Private grades for registered users - only visible to the user who created them"""

    __tablename__ = "grades"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=generate_uuid, nullable=False
    )
    user_id: Mapped[str] = mapped_column(String, ForeignKey("users.id"), nullable=False)
    event_id: Mapped[str] = mapped_column(
        String, ForeignKey("events.id"), nullable=False
    )
    grade: Mapped[float] = mapped_column(
        Float, nullable=False
    )  # 1.0 - 6.0 (German grading scale)
    weight: Mapped[float | None] = mapped_column(
        Float, default=1.0, nullable=True
    )  # Weight for averaging (e.g. KA=1.0, Test=0.5)
    created_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime, default=datetime.datetime.utcnow, nullable=True
    )

    user: Mapped["User"] = relationship("User", back_populates="grades")
    event: Mapped["Event"] = relationship("Event", back_populates="grades")


# === Timetable Models ===


class TimetableSettings(Base):
    """Stundenplan-Einstellungen pro Klasse"""

    __tablename__ = "timetable_settings"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=generate_uuid, nullable=False
    )
    class_id: Mapped[str] = mapped_column(
        String, ForeignKey("classes.id"), unique=True, nullable=False
    )
    slot_duration: Mapped[int | None] = mapped_column(
        Integer, default=45, nullable=True
    )  # Minuten pro Stunde
    break_duration: Mapped[int | None] = mapped_column(
        Integer, default=15, nullable=True
    )  # Minuten Pause
    day_start_hour: Mapped[int | None] = mapped_column(
        Integer, default=8, nullable=True
    )  # Startzeit Stunde (08:00)
    day_start_minute: Mapped[int | None] = mapped_column(
        Integer, default=0, nullable=True
    )
    day_end_hour: Mapped[int | None] = mapped_column(
        Integer, default=16, nullable=True
    )  # Endzeit Stunde (16:00)
    day_end_minute: Mapped[int | None] = mapped_column(
        Integer, default=0, nullable=True
    )

    clazz: Mapped["Class"] = relationship("Class", back_populates="timetable_settings")


class TimetableSlot(Base):
    """Ein Zeitslot im Stundenplan - von Admin erstellt"""

    __tablename__ = "timetable_slots"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=generate_uuid, nullable=False
    )
    class_id: Mapped[str] = mapped_column(
        String, ForeignKey("classes.id"), nullable=False
    )
    weekday: Mapped[int] = mapped_column(
        Integer, nullable=False
    )  # 0=Mo, 1=Di, 2=Mi, 3=Do, 4=Fr
    slot_number: Mapped[int] = mapped_column(
        Integer, nullable=False
    )  # 1, 2, 3... (Stundennummer des Tages)
    subject_id: Mapped[str | None] = mapped_column(
        String, ForeignKey("subjects.id"), nullable=True
    )
    subject_name: Mapped[str | None] = mapped_column(
        String, nullable=True
    )  # Fallback/Override für Fachname
    group_name: Mapped[str | None] = mapped_column(
        String, nullable=True
    )  # z.B. "Bili", "Grundkurs", "LK"
    room: Mapped[str | None] = mapped_column(String, nullable=True)

    clazz: Mapped["Class"] = relationship("Class", back_populates="timetable_slots")
    subject: Mapped["Subject | None"] = relationship(
        "Subject", back_populates="timetable_slots"
    )

    user_selections: Mapped[list["UserTimetableSelection"]] = relationship(
        back_populates="slot"
    )


class UserTimetableSelection(Base):
    """User-Auswahl für Kurse/Gruppen - für personalisierten Stundenplan"""

    __tablename__ = "user_timetable_selections"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=generate_uuid, nullable=False
    )
    user_id: Mapped[str] = mapped_column(String, ForeignKey("users.id"), nullable=False)
    slot_id: Mapped[str] = mapped_column(
        String, ForeignKey("timetable_slots.id"), nullable=False
    )

    user: Mapped["User"] = relationship("User", back_populates="timetable_selections")
    slot: Mapped["TimetableSlot"] = relationship(
        "TimetableSlot", back_populates="user_selections"
    )


# === OAuth Models ===


class OAuthClient(Base):
    """Registered OAuth clients (e.g., mobile apps)"""

    __tablename__ = "oauth_clients"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=generate_uuid, nullable=False
    )
    client_id: Mapped[str] = mapped_column(
        String, unique=True, index=True, nullable=False
    )
    client_secret: Mapped[str] = mapped_column(String, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    redirect_uri: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime, default=datetime.datetime.utcnow, nullable=True
    )
    redirect_uris: Mapped[list["OAuthClientRedirectUri"]] = relationship(
        "OAuthClientRedirectUri",
        back_populates="client",
        cascade="all, delete-orphan",
    )


class OAuthClientRedirectUri(Base):
    """Allowed redirect URIs for an OAuth client."""

    __tablename__ = "oauth_client_redirect_uris"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=generate_uuid, nullable=False
    )
    oauth_client_id: Mapped[str] = mapped_column(
        String, ForeignKey("oauth_clients.id"), nullable=False
    )
    redirect_uri: Mapped[str] = mapped_column(String, nullable=False, index=True)
    created_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime, default=datetime.datetime.utcnow, nullable=True
    )

    client: Mapped["OAuthClient"] = relationship(
        "OAuthClient", back_populates="redirect_uris"
    )


class OAuthAuthorizationCode(Base):
    """Temporary authorization codes for OAuth flow"""

    __tablename__ = "oauth_authorization_codes"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=generate_uuid, nullable=False
    )
    code: Mapped[str | None] = mapped_column(
        String, unique=True, index=True, default=generate_token, nullable=True
    )
    client_id: Mapped[str] = mapped_column(String, nullable=False)
    user_id: Mapped[str] = mapped_column(String, ForeignKey("users.id"), nullable=False)
    redirect_uri: Mapped[str] = mapped_column(String, nullable=False)
    scope: Mapped[str | None] = mapped_column(
        String, default="read:events", nullable=True
    )
    expires_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False)
    used: Mapped[bool | None] = mapped_column(Boolean, default=False, nullable=True)
    created_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime, default=datetime.datetime.utcnow, nullable=True
    )

    user: Mapped["User"] = relationship("User")


# === Push Notification Models ===


class DeviceToken(Base):
    """FCM/APNs device tokens for push notifications"""

    __tablename__ = "device_tokens"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=generate_uuid, nullable=False
    )
    user_id: Mapped[str] = mapped_column(String, ForeignKey("users.id"), nullable=False)
    device_token: Mapped[str] = mapped_column(String, nullable=False, index=True)
    platform: Mapped[str] = mapped_column(String, nullable=False)  # "fcm" or "apns"
    created_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime, default=datetime.datetime.utcnow, nullable=True
    )
    updated_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime,
        default=datetime.datetime.utcnow,
        onupdate=datetime.datetime.utcnow,
        nullable=True,
    )

    user: Mapped["User"] = relationship("User", back_populates="device_tokens")
