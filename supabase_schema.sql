
-- Auto-generated SQL Migration Script for Native Supabase
--
-- INSTRUCTIONS:
-- 1. Go to your Supabase Project Dashboard
-- 2. Open the SQL Editor
-- 3. Create a new Query
-- 4. Copy and Paste the following SQL commands
-- 5. Run the query to set up your database schema.

-- Use standard Postgres constraints and types

-- --- TABLES ---

CREATE TABLE IF NOT EXISTS classes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    join_token TEXT UNIQUE NOT NULL,
    owner_id TEXT,
    join_enabled BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc', now())
);
CREATE INDEX IF NOT EXISTS ix_classes_join_token ON classes(join_token);

CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    class_id UUID NOT NULL REFERENCES classes(id) ON DELETE CASCADE,
    role TEXT DEFAULT 'member',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc', now()),
    session_token TEXT,
    email TEXT UNIQUE,
    password_hash TEXT,
    is_registered BOOLEAN DEFAULT FALSE,
    language TEXT DEFAULT 'de',
    caldav_token TEXT,
    caldav_enabled BOOLEAN DEFAULT FALSE,
    caldav_write BOOLEAN DEFAULT FALSE
);
CREATE INDEX IF NOT EXISTS ix_users_email ON users(email);

CREATE TABLE IF NOT EXISTS subjects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    class_id UUID NOT NULL REFERENCES classes(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    color TEXT DEFAULT '#666666'
);

CREATE TABLE IF NOT EXISTS events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    class_id UUID NOT NULL REFERENCES classes(id) ON DELETE CASCADE,
    type TEXT NOT NULL,
    priority TEXT DEFAULT 'MEDIUM',
    subject_id UUID REFERENCES subjects(id) ON DELETE SET NULL,
    subject_name TEXT,
    title TEXT,
    date TIMESTAMP WITH TIME ZONE,
    author_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc', now()),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc', now())
);

CREATE TABLE IF NOT EXISTS event_topics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_id UUID NOT NULL REFERENCES events(id) ON DELETE CASCADE,
    topic_type TEXT NOT NULL,
    content TEXT,
    count INTEGER,
    pages TEXT,
    "order" INTEGER DEFAULT 0,
    parent_id UUID REFERENCES event_topics(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS event_links (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_id UUID NOT NULL REFERENCES events(id) ON DELETE CASCADE,
    url TEXT NOT NULL,
    label TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS sys_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    type TEXT NOT NULL,
    status TEXT DEFAULT 'pending',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc', now()),
    started_at TIMESTAMP WITH TIME ZONE,
    finished_at TIMESTAMP WITH TIME ZONE,
    progress INTEGER DEFAULT 0,
    total_steps INTEGER DEFAULT 0,
    current_step INTEGER DEFAULT 0,
    message TEXT,
    logs TEXT DEFAULT '',
    meta_data TEXT DEFAULT '{}',
    created_by TEXT
);

CREATE TABLE IF NOT EXISTS timetable_settings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    class_id UUID NOT NULL UNIQUE REFERENCES classes(id) ON DELETE CASCADE,
    slot_duration INTEGER DEFAULT 45,
    break_duration INTEGER DEFAULT 15,
    day_start_hour INTEGER DEFAULT 8,
    day_start_minute INTEGER DEFAULT 0,
    day_end_hour INTEGER DEFAULT 16,
    day_end_minute INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS timetable_slots (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    class_id UUID NOT NULL REFERENCES classes(id) ON DELETE CASCADE,
    weekday INTEGER NOT NULL,
    slot_number INTEGER NOT NULL,
    subject_id UUID REFERENCES subjects(id) ON DELETE SET NULL,
    subject_name TEXT,
    group_name TEXT,
    room TEXT
);

CREATE TABLE IF NOT EXISTS user_timetable_selections (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    slot_id UUID NOT NULL REFERENCES timetable_slots(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS grades (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    event_id UUID NOT NULL REFERENCES events(id) ON DELETE CASCADE,
    grade FLOAT NOT NULL,
    weight FLOAT DEFAULT 1.0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc', now())
);

CREATE TABLE IF NOT EXISTS user_preferences (
    user_id UUID PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    filter_subjects TEXT DEFAULT '[]',
    filter_event_types TEXT DEFAULT '[]',
    filter_priority TEXT DEFAULT '[]'
);

CREATE TABLE IF NOT EXISTS audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    class_id UUID NOT NULL REFERENCES classes(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    action TEXT NOT NULL,
    target_id TEXT,
    data TEXT,
    permanent BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc', now())
);

CREATE TABLE IF NOT EXISTS oauth_clients (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    client_id TEXT UNIQUE NOT NULL,
    client_secret TEXT NOT NULL,
    name TEXT NOT NULL,
    redirect_uri TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc', now())
);
CREATE INDEX IF NOT EXISTS ix_oauth_clients_client_id ON oauth_clients(client_id);

CREATE TABLE IF NOT EXISTS oauth_authorization_codes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code TEXT UNIQUE NOT NULL,
    client_id TEXT NOT NULL,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    redirect_uri TEXT NOT NULL,
    scope TEXT DEFAULT 'read:events',
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    used BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc', now())
);
CREATE INDEX IF NOT EXISTS ix_oauth_authorization_codes_code ON oauth_authorization_codes(code);

CREATE TABLE IF NOT EXISTS device_tokens (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    device_token TEXT NOT NULL,
    platform TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc', now()),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc', now())
);
CREATE INDEX IF NOT EXISTS ix_device_tokens_device_token ON device_tokens(device_token);

CREATE TABLE IF NOT EXISTS login_tokens (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    class_id UUID NOT NULL REFERENCES classes(id) ON DELETE CASCADE,
    token TEXT UNIQUE DEFAULT md5(random()::text),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    user_name TEXT,
    max_uses INTEGER,
    uses INTEGER DEFAULT 0,
    role TEXT DEFAULT 'member',
    expires_at TIMESTAMP WITH TIME ZONE,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc', now())
);

CREATE TABLE IF NOT EXISTS integration_tokens (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    token TEXT UNIQUE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    class_id UUID NOT NULL REFERENCES classes(id) ON DELETE CASCADE,
    scopes TEXT DEFAULT 'read:events',
    expires_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc', now()),
    last_used_at TIMESTAMP WITH TIME ZONE,
    revoked BOOLEAN DEFAULT FALSE
);

-- --- ROW LEVEL SECURITY (RLS) ---

-- Enable RLS on ALL tables
ALTER TABLE classes ENABLE ROW LEVEL SECURITY;
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE subjects ENABLE ROW LEVEL SECURITY;
ALTER TABLE events ENABLE ROW LEVEL SECURITY;
ALTER TABLE event_topics ENABLE ROW LEVEL SECURITY;
ALTER TABLE event_links ENABLE ROW LEVEL SECURITY;
ALTER TABLE sys_jobs ENABLE ROW LEVEL SECURITY;
ALTER TABLE timetable_settings ENABLE ROW LEVEL SECURITY;
ALTER TABLE timetable_slots ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_timetable_selections ENABLE ROW LEVEL SECURITY;
ALTER TABLE grades ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_preferences ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE oauth_clients ENABLE ROW LEVEL SECURITY;
ALTER TABLE oauth_authorization_codes ENABLE ROW LEVEL SECURITY;
ALTER TABLE device_tokens ENABLE ROW LEVEL SECURITY;
ALTER TABLE login_tokens ENABLE ROW LEVEL SECURITY;
ALTER TABLE integration_tokens ENABLE ROW LEVEL SECURITY;

-- Minimal RLS Policies
-- NOTE: These policies assume you authenticate using Supabase Auth and your 'users.id' matches 'auth.uid()'.
-- If you use the Service Role Key (backend), these policies are bypassed automatically.

-- 1. USERS: Users can see themselves
DROP POLICY IF EXISTS "Users can read own profile" ON users;
CREATE POLICY "Users can read own profile" ON users
  FOR SELECT USING (auth.uid() = id);

DROP POLICY IF EXISTS "Users can update own profile" ON users;
CREATE POLICY "Users can update own profile" ON users
  FOR UPDATE USING (auth.uid() = id);

-- 2. CLASSES: Members can see their class
-- (Requires a lookup or joining, which can be complex in RLS. Simple version: Publicly readable or check if user exists in class)
-- For minimal setup, we allow authenticated users to read classes they know the ID of.
DROP POLICY IF EXISTS "Authenticated users can read classes" ON classes;
CREATE POLICY "Authenticated users can read classes" ON classes
  FOR SELECT TO authenticated USING (true);

-- 3. EVENTS: Users can see events in their class (Simplified)
-- Ideally: USING (class_id IN (SELECT class_id FROM users WHERE id = auth.uid()))
DROP POLICY IF EXISTS "Users can see class events" ON events;
CREATE POLICY "Users can see class events" ON events
  FOR SELECT USING (
    EXISTS (SELECT 1 FROM users WHERE users.id = auth.uid() AND users.class_id = events.class_id)
  );

DROP POLICY IF EXISTS "Authors can edit their events" ON events;
CREATE POLICY "Authors can edit their events" ON events
  FOR ALL USING (auth.uid() = author_id);

-- 4. GRADES: Users can strictly only see their own grades
DROP POLICY IF EXISTS "Users see own grades" ON grades;
CREATE POLICY "Users see own grades" ON grades
  FOR SELECT USING (auth.uid() = user_id);

-- 5. DEVICE TOKENS: Private
DROP POLICY IF EXISTS "Users manage device tokens" ON device_tokens;
CREATE POLICY "Users manage device tokens" ON device_tokens
  FOR ALL USING (auth.uid() = user_id);

-- 6. PREFERENCES: Private
DROP POLICY IF EXISTS "Users manage preferences" ON user_preferences;
CREATE POLICY "Users manage preferences" ON user_preferences
  FOR ALL USING (auth.uid() = user_id);

-- 7. SYSTEM JOBS: Only admins? or Authenticated?
-- Let's allow authenticated mostly for now, or assume Service Role handles it.
DROP POLICY IF EXISTS "Authenticated read sys jobs" ON sys_jobs;
CREATE POLICY "Authenticated read sys jobs" ON sys_jobs
  FOR SELECT TO authenticated USING (true);

