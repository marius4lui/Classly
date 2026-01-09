import sys
import os
sys.path.append(os.getcwd())

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app import models

# Connect to ACTUAL database file
# The file is in root: classly.db
SQLALCHEMY_DATABASE_URL = "sqlite:///./classly.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def check_roles():
    db = SessionLocal()
    users = db.query(models.User).all()
    print(f"Found {len(users)} users:")
    for u in users:
        print(f"User: {u.name}, ID: {u.id}, Role Value: '{u.role.value}', Role Enum: {u.role}")
    
    # Also check if 'member' is present in DB as string
    # By using direct cursor
    import sqlite3
    conn = sqlite3.connect("classly.db")
    cursor = conn.cursor()
    cursor.execute("SELECT name, role FROM users")
    print("\nRaw DB Values:")
    for row in cursor.fetchall():
        print(f"User: {row[0]}, Role: '{row[1]}'")
    
    conn.close()

if __name__ == "__main__":
    check_roles()
