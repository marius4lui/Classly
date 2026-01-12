import os

class Settings:
    # Core Features
    FEATURE_GRADES = os.getenv("FEATURE_GRADES", "true").lower() == "true"
    FEATURE_TIMETABLE = os.getenv("FEATURE_TIMETABLE", "true").lower() == "true"
    FEATURE_EXAMS = os.getenv("FEATURE_EXAMS", "true").lower() == "true"
    FEATURE_SUBJECTS = os.getenv("FEATURE_SUBJECTS", "true").lower() == "true"

    # Advanced Features
    FEATURE_CALDAV = os.getenv("FEATURE_CALDAV", "true").lower() == "true"
    FEATURE_RSS_FEED = os.getenv("FEATURE_RSS_FEED", "true").lower() == "true"
    FEATURE_PUBLIC_SHARING = os.getenv("FEATURE_PUBLIC_SHARING", "false").lower() == "true"

    # Social/Collaborative
    FEATURE_COMMENTS = os.getenv("FEATURE_COMMENTS", "true").lower() == "true"
    FEATURE_FILE_UPLOADS = os.getenv("FEATURE_FILE_UPLOADS", "true").lower() == "true"

    # Admin
    FEATURE_PUBLIC_REGISTRATION = os.getenv("FEATURE_PUBLIC_REGISTRATION", "false").lower() == "true"
    FEATURE_USER_INVITES = os.getenv("FEATURE_USER_INVITES", "true").lower() == "true"
    FEATURE_AUDIT_LOG = os.getenv("FEATURE_AUDIT_LOG", "true").lower() == "true"

    # Privacy/Compliance
    AUDIT_LOG_RETENTION_DAYS = int(os.getenv("AUDIT_LOG_RETENTION_DAYS", "90"))
    ENABLE_ANALYTICS = os.getenv("ENABLE_ANALYTICS", "false").lower() == "true"
    ENABLE_ERROR_REPORTING = os.getenv("ENABLE_ERROR_REPORTING", "false").lower() == "true"

    # Other configs
    GTM_ID = os.getenv("GTM_ID")

settings = Settings()

def is_feature_enabled(feature_name: str) -> bool:
    feature_flag = f"FEATURE_{feature_name.upper()}"
    return getattr(settings, feature_flag, False)
