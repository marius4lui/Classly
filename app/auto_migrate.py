
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

            # 3. Check if grades table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='grades'")
            if not cursor.fetchone():
                logger.info("Migrating: Creating 'grades' table.")
                cursor.execute("""
                    CREATE TABLE grades (
                        id VARCHAR PRIMARY KEY,
                        user_id VARCHAR NOT NULL,
                        event_id VARCHAR NOT NULL,
                        grade FLOAT NOT NULL,
                        weight FLOAT DEFAULT 1.0,
                        created_at DATETIME,
                        FOREIGN KEY (user_id) REFERENCES users(id),
                        FOREIGN KEY (event_id) REFERENCES events(id)
                    )
                """)
                cursor.execute("CREATE INDEX ix_grades_user_id ON grades(user_id)")
                cursor.execute("CREATE INDEX ix_grades_event_id ON grades(event_id)")
                conn.commit()
            else:
                # 4. Check if weight column exists in grades table
                cursor.execute("PRAGMA table_info(grades)")
                grade_columns = [info[1] for info in cursor.fetchall()]
                if "weight" not in grade_columns:
                    logger.info("Migrating: Adding 'weight' column to grades table.")
                    cursor.execute("ALTER TABLE grades ADD COLUMN weight FLOAT DEFAULT 1.0")
                    conn.commit()

            # 5. Create timetable_settings table if not exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='timetable_settings'")
            if not cursor.fetchone():
                logger.info("Migrating: Creating 'timetable_settings' table.")
                cursor.execute("""
                    CREATE TABLE timetable_settings (
                        id VARCHAR PRIMARY KEY,
                        class_id VARCHAR NOT NULL UNIQUE,
                        slot_duration INTEGER DEFAULT 45,
                        break_duration INTEGER DEFAULT 15,
                        day_start_hour INTEGER DEFAULT 8,
                        day_start_minute INTEGER DEFAULT 0,
                        day_end_hour INTEGER DEFAULT 16,
                        day_end_minute INTEGER DEFAULT 0,
                        FOREIGN KEY (class_id) REFERENCES classes(id)
                    )
                """)
                conn.commit()

            # 6. Create timetable_slots table if not exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='timetable_slots'")
            if not cursor.fetchone():
                logger.info("Migrating: Creating 'timetable_slots' table.")
                cursor.execute("""
                    CREATE TABLE timetable_slots (
                        id VARCHAR PRIMARY KEY,
                        class_id VARCHAR NOT NULL,
                        weekday INTEGER NOT NULL,
                        slot_number INTEGER NOT NULL,
                        subject_id VARCHAR,
                        subject_name VARCHAR,
                        group_name VARCHAR,
                        room VARCHAR,
                        FOREIGN KEY (class_id) REFERENCES classes(id),
                        FOREIGN KEY (subject_id) REFERENCES subjects(id)
                    )
                """)
                cursor.execute("CREATE INDEX ix_timetable_slots_class_id ON timetable_slots(class_id)")
                conn.commit()

            # 7. Create user_timetable_selections table if not exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='user_timetable_selections'")
            if not cursor.fetchone():
                logger.info("Migrating: Creating 'user_timetable_selections' table.")
                cursor.execute("""
                    CREATE TABLE user_timetable_selections (
                        id VARCHAR PRIMARY KEY,
                        user_id VARCHAR NOT NULL,
                        slot_id VARCHAR NOT NULL,
                        FOREIGN KEY (user_id) REFERENCES users(id),
                        FOREIGN KEY (slot_id) REFERENCES timetable_slots(id)
                    )
                """)
                cursor.execute("CREATE INDEX ix_user_timetable_selections_user_id ON user_timetable_selections(user_id)")
                conn.commit()

            # Add other migrations here as needed
            
        except Exception as e:
            logger.error(f"Auto migration failed: {e}")
            conn.rollback()
        finally:
            conn.close()
