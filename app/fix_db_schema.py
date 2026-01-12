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

        # 5. Make date nullable (SQLite workaround)
        # Check if events table exists and if date column is NOT NULL
        cursor.execute("PRAGMA table_info(events)")
        columns = cursor.fetchall()
        # column structure: (cid, name, type, notnull, dflt_value, pk)
        date_col = next((c for c in columns if c[1] == 'date'), None)

        if date_col and date_col[3] == 1: # notnull == 1 means NOT NULL
            print("Fixing 'events.date' column constraint (making it nullable)...")

            # Commit any pending transaction to ensure PRAGMA works
            conn.commit()

            # Disable foreign keys
            cursor.execute("PRAGMA foreign_keys=OFF")

            # 1. Rename old table
            cursor.execute("ALTER TABLE events RENAME TO events_old")

            # 2. Create new table with nullable date
            # We copy the schema from models.py but make date nullable
            cursor.execute("""
                CREATE TABLE events (
                    id VARCHAR NOT NULL,
                    class_id VARCHAR NOT NULL,
                    type VARCHAR(4) NOT NULL,
                    priority VARCHAR(6),
                    subject_id VARCHAR,
                    subject_name VARCHAR,
                    title VARCHAR,
                    date TIMESTAMP,
                    author_id VARCHAR NOT NULL,
                    created_at TIMESTAMP,
                    updated_at TIMESTAMP,
                    PRIMARY KEY (id),
                    FOREIGN KEY(class_id) REFERENCES classes (id),
                    FOREIGN KEY(subject_id) REFERENCES subjects (id),
                    FOREIGN KEY(author_id) REFERENCES users (id)
                )
            """)

            # 3. Copy data
            # Dynamically get columns from events_old to handle potential extra columns gracefully (though likely not needed)
            # But here we strictly map known columns to ensure structure matches models.py
            cursor.execute("""
                INSERT INTO events (id, class_id, type, priority, subject_id, subject_name, title, date, author_id, created_at, updated_at)
                SELECT id, class_id, type, priority, subject_id, subject_name, title, date, author_id, created_at, updated_at FROM events_old
            """)

            # 4. Drop old table
            cursor.execute("DROP TABLE events_old")

            # Re-enable foreign keys
            cursor.execute("PRAGMA foreign_keys=ON")

            # Check for indices (recreation if needed)
            # Currently 'events' table only has implicit indices on PK and potentially FKs depending on DB config.
            # models.py does not define explicit indices on events table columns except ID.
            # Verify if any index was dropped.
            # (In this specific case, we assume standard schema).

            print("Fixed 'events.date' constraint.")
        else:
            # Check if it was because table didn't exist or column didn't exist
            if not date_col:
                # If table exists but no date column? Rare but possible.
                # Or table doesn't exist.
                pass
            else:
                 # It is already nullable (date_col[3] == 0)
                 pass

        conn.commit()
        conn.close()
        print("Schema fix executed.")
    except Exception as e:
        print(f"Schema fix failed: {e}")
