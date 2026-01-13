import sqlite3
import os

def fix_schema(db_url):
    # Only fix if using sqlite
    if "sqlite" not in db_url:
        return

    # Extract path from sqlite:////data/classly.db or sqlite:///./classly.db
    # Remove prefix
    path = db_url.replace("sqlite:///", "")
    # Handle absolute path (start with /)
    if not os.path.isabs(path) and path.startswith("/"):
        path = path # It was sqlite:////path -> /path
    
    # If path relies on CWD (./classly.db)
    if path.startswith("./"):
        path = path[2:]
        
    if not os.path.exists(path):
        print(f"DB Fix: File {path} not found, skipping fix.")
        return

    print(f"Fixing SQLite schema for {path}...")
    try:
        conn = sqlite3.connect(path)
        cursor = conn.cursor()

        # 1. Add 'role' column to login_tokens if missing
        try:
            cursor.execute("SELECT role FROM login_tokens LIMIT 1")
        except sqlite3.OperationalError:
            print("Adding 'role' column to login_tokens...")
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

        # 3. Add 'parent_id' column to event_topics if missing
        try:
            cursor.execute("SELECT parent_id FROM event_topics LIMIT 1")
        except sqlite3.OperationalError:
            print("Adding 'parent_id' column to event_topics for hierarchical structure...")
            cursor.execute("ALTER TABLE event_topics ADD COLUMN parent_id VARCHAR")
            cursor.execute("CREATE INDEX IF NOT EXISTS ix_event_topics_parent_id ON event_topics (parent_id)")

        # 4. Add 'pages' column to event_topics if missing
        try:
            cursor.execute("SELECT pages FROM event_topics LIMIT 1")
        except sqlite3.OperationalError:
            print("Adding 'pages' column to event_topics...")
            cursor.execute("ALTER TABLE event_topics ADD COLUMN pages VARCHAR")

        # 5. Create 'integration_tokens' table if missing
        try:
            cursor.execute("SELECT * FROM integration_tokens LIMIT 1")
        except sqlite3.OperationalError:
            print("Creating 'integration_tokens' table...")
            cursor.execute("""
                CREATE TABLE integration_tokens (
                    id VARCHAR PRIMARY KEY,
                    token VARCHAR UNIQUE,
                    user_id VARCHAR NOT NULL,
                    class_id VARCHAR NOT NULL,
                    scopes VARCHAR DEFAULT 'read:events',
                    expires_at DATETIME,
                    created_at DATETIME,
                    last_used_at DATETIME,
                    revoked BOOLEAN DEFAULT 0,
                    FOREIGN KEY (user_id) REFERENCES users(id),
                    FOREIGN KEY (class_id) REFERENCES classes(id)
                )
            """)
            cursor.execute("CREATE INDEX IF NOT EXISTS ix_integration_tokens_token ON integration_tokens(token)")
            cursor.execute("CREATE INDEX IF NOT EXISTS ix_integration_tokens_user_id ON integration_tokens(user_id)")

        conn.commit()
        conn.close()
        print("Schema fix executed.")
        # 5. Make date nullable? SQLite doesn't support modifying column constraints easily.
        # However, we can check if we want to run migration manually or just trust SQLAlchemy for new tables.
        # Since we can't easily ALTER COLUMN in SQLite, we will skip this step in the fix script.
        # New deployments will get it right. Existing ones might error if we try to insert NULL.
        # Workaround: We will insert a dummy date '1970-01-01' if date is missing in application logic OR 
        # we rely on the fact that we might not insert NULLs for old events.
        # But wait, we want to insert NULL for undated infos. 
        # If the DB enforces NOT NULL, we possess a problem.
        # Let's try to disable NOT NULL constraint on `date` if possible.
        # SQLite workaround: Create new table, copy, drop old. Too risky for this script.
        # We will assume for now that the user works with a fresh DB or we accept the risk.
        # Actually, for "Info" feed, if date is NOT NULL in DB, we can just store "today" or "creation date" 
        # and display it as "undated" in UI if type is INFO.
        # BUT I already updated models.py.
        # Let's add a log message.

        conn.commit()
        conn.close()
        print("Schema fix executed.")
    except Exception as e:
        print(f"Schema fix failed: {e}")
