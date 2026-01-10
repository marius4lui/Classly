import sys
import os

# Add parent directory to path so we can import 'app'
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app import models

# Connect to ACTUAL database file
# The file is in root: classly.db
db_path = os.path.join(parent_dir, "classly.db")
SQLALCHEMY_DATABASE_URL = f"sqlite:///{db_path}"
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
    # By using direct cursor
    import sqlite3
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name, role FROM users")
    print("\nRaw DB Values:")
    for row in cursor.fetchall():
        print(f"User: {row[0]}, Role: '{row[1]}'")
    
    conn.close()

if __name__ == "__main__":
    check_roles()
