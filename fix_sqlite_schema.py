import sqlite3

DB_PATH = "classly.db"

def fix_schema():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("Fixing SQLite schema...")

    # 1. Add 'role' column to login_tokens if missing
    try:
        cursor.execute("SELECT role FROM login_tokens LIMIT 1")
    except sqlite3.OperationalError:
        print("Adding 'role' column to login_tokens...")
        # Add column with default 'member' (UserRole.MEMBER value)
        cursor.execute("ALTER TABLE login_tokens ADD COLUMN role VARCHAR DEFAULT 'member'")
    
    # 2. Add 'event_links' table if missing
    try:
        cursor.execute("SELECT * FROM event_links LIMIT 1")
    except sqlite3.OperationalError:
        print("Creating 'event_links' table...")
        cursor.execute("""
            CREATE TABLE event_links (
                id VARCHAR NOT NULL, 
                event_id VARCHAR, 
                url VARCHAR, 
                label VARCHAR, 
                PRIMARY KEY (id), 
                FOREIGN KEY(event_id) REFERENCES events (id) ON DELETE CASCADE
            )
        """)

    conn.commit()
    conn.close()
    print("Schema fixed successfully.")

if __name__ == "__main__":
    fix_schema()
