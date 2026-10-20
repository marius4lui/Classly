from app.database import engine, Base
from app.models import UserPreferences, Class, AuditLog

# Create table
print("Creating user_preferences table...")
Base.metadata.tables["user_preferences"].create(bind=engine, checkfirst=True)
print("Done!")
