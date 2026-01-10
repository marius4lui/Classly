from app.database import engine, Base
from app.models import UserPreferences, Class, AuditLog

# Create table
print("Creating user_preferences table...")
UserPreferences.__table__.create(bind=engine, checkfirst=True)
print("Done!")
