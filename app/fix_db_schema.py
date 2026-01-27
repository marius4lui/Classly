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

        
        # 1. Add 'language' column to users if missing
        try:
            cursor.execute("SELECT language FROM users LIMIT 1")
        except sqlite3.OperationalError:
            print("Adding 'language' column to users...")
            cursor.execute("ALTER TABLE users ADD COLUMN language VARCHAR DEFAULT 'de'")

        # 2. Add 'role' column to login_tokens if missing
        try:
            cursor.execute("SELECT role FROM login_tokens LIMIT 1")
        except sqlite3.OperationalError:
            print("Adding 'role' column to login_tokens...")
            cursor.execute("ALTER TABLE login_tokens ADD COLUMN role VARCHAR DEFAULT 'member'")
        
        # 3. Add 'event_links' table if missing
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

        # 4. Add 'parent_id' column to event_topics if missing
        try:
            cursor.execute("SELECT parent_id FROM event_topics LIMIT 1")
        except sqlite3.OperationalError:
            print("Adding 'parent_id' column to event_topics for hierarchical structure...")
            cursor.execute("ALTER TABLE event_topics ADD COLUMN parent_id VARCHAR")
            cursor.execute("CREATE INDEX IF NOT EXISTS ix_event_topics_parent_id ON event_topics (parent_id)")

        # 5. Add 'pages' column to event_topics if missing
        try:
            cursor.execute("SELECT pages FROM event_topics LIMIT 1")
        except sqlite3.OperationalError:
            print("Adding 'pages' column to event_topics...")
            cursor.execute("ALTER TABLE event_topics ADD COLUMN pages VARCHAR")

        # 6. Create 'integration_tokens' table if missing
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
        
        # 7. Add 'priority' column to events if missing (before potentially recreating table)
        try:
            cursor.execute("SELECT priority FROM events LIMIT 1")
        except sqlite3.OperationalError:
            print("Adding 'priority' column to events...")
            cursor.execute("ALTER TABLE events ADD COLUMN priority VARCHAR(6)")

        # 8. Make date nullable (SQLite workaround)
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

        # 9. Create 'sys_jobs' table if missing (Required for System Dashboard)
        try:
            cursor.execute("SELECT * FROM sys_jobs LIMIT 1")
        except sqlite3.OperationalError:
            print("Creating 'sys_jobs' table...")
            cursor.execute("""
                CREATE TABLE sys_jobs (
                    id VARCHAR PRIMARY KEY,
                    type VARCHAR NOT NULL,
                    status VARCHAR DEFAULT 'pending',
                    created_at DATETIME,
                    started_at DATETIME,
                    finished_at DATETIME,
                    progress INTEGER DEFAULT 0,
                    total_steps INTEGER DEFAULT 0,
                    current_step INTEGER DEFAULT 0,
                    message VARCHAR,
                    logs VARCHAR DEFAULT '',
                    meta_data VARCHAR DEFAULT '{}',
                    created_by VARCHAR
                )
            """)

        # 10. Create 'timetable_settings' table if missing
        try:
            cursor.execute("SELECT * FROM timetable_settings LIMIT 1")
        except sqlite3.OperationalError:
            print("Creating 'timetable_settings' table...")
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

        # 11. Create 'timetable_slots' table if missing
        try:
            cursor.execute("SELECT * FROM timetable_slots LIMIT 1")
        except sqlite3.OperationalError:
            print("Creating 'timetable_slots' table...")
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

        # 12. Create 'user_timetable_selections' table if missing
        try:
            cursor.execute("SELECT * FROM user_timetable_selections LIMIT 1")
        except sqlite3.OperationalError:
            print("Creating 'user_timetable_selections' table...")
            cursor.execute("""
                CREATE TABLE user_timetable_selections (
                    id VARCHAR PRIMARY KEY,
                    user_id VARCHAR NOT NULL,
                    slot_id VARCHAR NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users(id),
                    FOREIGN KEY (slot_id) REFERENCES timetable_slots(id)
                )
            """)

        # 13. Create 'device_tokens' table if missing
        try:
            cursor.execute("SELECT * FROM device_tokens LIMIT 1")
        except sqlite3.OperationalError:
            print("Creating 'device_tokens' table...")
            cursor.execute("""
                CREATE TABLE device_tokens (
                    id VARCHAR PRIMARY KEY,
                    user_id VARCHAR NOT NULL,
                    device_token VARCHAR NOT NULL,
                    platform VARCHAR NOT NULL,
                    created_at DATETIME,
                    updated_at DATETIME,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)
            cursor.execute("CREATE INDEX IF NOT EXISTS ix_device_tokens_device_token ON device_tokens(device_token)")

        # 14. Create 'grades' table if missing
        try:
            cursor.execute("SELECT * FROM grades LIMIT 1")
        except sqlite3.OperationalError:
            print("Creating 'grades' table...")
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

        # 15. Create 'user_preferences' table if missing
        try:
            cursor.execute("SELECT * FROM user_preferences LIMIT 1")
        except sqlite3.OperationalError:
            print("Creating 'user_preferences' table...")
            cursor.execute("""
                CREATE TABLE user_preferences (
                    user_id VARCHAR PRIMARY KEY,
                    filter_subjects VARCHAR DEFAULT '[]',
                    filter_event_types VARCHAR DEFAULT '[]',
                    filter_priority VARCHAR DEFAULT '[]',
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)

        # 16. Create 'audit_logs' table if missing
        try:
            cursor.execute("SELECT * FROM audit_logs LIMIT 1")
        except sqlite3.OperationalError:
            print("Creating 'audit_logs' table...")
            cursor.execute("""
                CREATE TABLE audit_logs (
                    id VARCHAR PRIMARY KEY,
                    class_id VARCHAR NOT NULL,
                    user_id VARCHAR,
                    action VARCHAR NOT NULL,
                    target_id VARCHAR,
                    data VARCHAR,
                    permanent BOOLEAN DEFAULT 0,
                    created_at DATETIME,
                    FOREIGN KEY (class_id) REFERENCES classes(id),
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)
        
        # 17. Create 'oauth_clients' table if missing
        try:
            cursor.execute("SELECT * FROM oauth_clients LIMIT 1")
        except sqlite3.OperationalError:
            print("Creating 'oauth_clients' table...")
            cursor.execute("""
                CREATE TABLE oauth_clients (
                    id VARCHAR PRIMARY KEY,
                    client_id VARCHAR NOT NULL UNIQUE,
                    client_secret VARCHAR NOT NULL,
                    name VARCHAR NOT NULL,
                    redirect_uri VARCHAR NOT NULL,
                    created_at DATETIME
                )
            """)
            cursor.execute("CREATE INDEX IF NOT EXISTS ix_oauth_clients_client_id ON oauth_clients(client_id)")

        # 18. Create 'oauth_authorization_codes' table if missing
        try:
            cursor.execute("SELECT * FROM oauth_authorization_codes LIMIT 1")
        except sqlite3.OperationalError:
            print("Creating 'oauth_authorization_codes' table...")
            cursor.execute("""
                CREATE TABLE oauth_authorization_codes (
                    id VARCHAR PRIMARY KEY,
                    code VARCHAR NOT NULL UNIQUE,
                    client_id VARCHAR NOT NULL,
                    user_id VARCHAR NOT NULL,
                    redirect_uri VARCHAR NOT NULL,
                    scope VARCHAR DEFAULT 'read:events',
                    expires_at DATETIME NOT NULL,
                    used BOOLEAN DEFAULT 0,
                    created_at DATETIME,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)
            cursor.execute("CREATE INDEX IF NOT EXISTS ix_oauth_authorization_codes_code ON oauth_authorization_codes(code)")
        
        conn.commit()
        conn.close()
        print("Schema fix executed.")
    except Exception as e:
        print(f"Schema fix failed: {e}")
