
import sqlite3
import os
import logging
from app.database import SQLALCHEMY_DATABASE_URL

logger = logging.getLogger("uvicorn")

def run_auto_migrations():
    """
    Automatically runs necessary DB migrations (ALTER TABLEs, etc.)
    that SQLAlchemy create_all doesn't handle for existing databases.
    """
    # Parse DB path from URL (sqlite:///./classly.db -> ./classly.db)
    if "sqlite" in SQLALCHEMY_DATABASE_URL:
        db_path = SQLALCHEMY_DATABASE_URL.replace("sqlite:///", "")
        
        if not os.path.exists(db_path):
            return

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        try:
            # 1. Check Priority Column in Events
            logger.info("Checking schema migrations...")
            cursor.execute("PRAGMA table_info(events)")
            columns = [info[1] for info in cursor.fetchall()]
            
            if "priority" not in columns:
                logger.info("Migrating: Adding 'priority' column to events table.")
                cursor.execute("ALTER TABLE events ADD COLUMN priority VARCHAR DEFAULT 'MEDIUM'")
                conn.commit()

            # 2. Migrate lowercase priority values to uppercase
            cursor.execute("SELECT COUNT(*) FROM events WHERE priority IN ('high', 'medium', 'low')")
            count = cursor.fetchone()[0]

            if count > 0:
                logger.info(f"Migrating: Converting {count} priority values to uppercase.")
                cursor.execute("UPDATE events SET priority = 'HIGH' WHERE priority = 'high'")
                cursor.execute("UPDATE events SET priority = 'MEDIUM' WHERE priority = 'medium'")
                cursor.execute("UPDATE events SET priority = 'LOW' WHERE priority = 'low'")
                conn.commit()

            # Add other migrations here as needed
            
        except Exception as e:
            logger.error(f"Auto migration failed: {e}")
            conn.rollback()
        finally:
            conn.close()
