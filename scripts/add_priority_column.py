import sqlite3
import os

# Build path to database
# Assuming standard location
DB_PATH = "classly.db"

def migrate():
    if not os.path.exists(DB_PATH):
        print("Database not found. Skipping migration.")
        return

    print(f"Migrating database: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # Check if column exists
        cursor.execute("PRAGMA table_info(events)")
        columns = [info[1] for info in cursor.fetchall()]
        
        if "priority" in columns:
            print("Column 'priority' already exists. Skipping.")
        else:
            print("Adding column 'priority'...")
            # SQLite supports ADD COLUMN
            # Default to 'medium'
            cursor.execute("ALTER TABLE events ADD COLUMN priority VARCHAR DEFAULT 'medium'")
            conn.commit()
            print("Migration successful.")
            
    except Exception as e:
        print(f"Migration failed: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
