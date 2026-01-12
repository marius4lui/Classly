import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.database import engine, Base, SQLALCHEMY_DATABASE_URL, SessionLocal
from app.routers import auth, pages, events, admin, caldav, preferences, grades, timetable, i18n_router
from app import fix_db_schema, crud, auto_migrate

# Fix DB Schema (Add missing columns to old SQLite volumes)
fix_db_schema.fix_schema(SQLALCHEMY_DATABASE_URL)
auto_migrate.run_auto_migrations()

# Create Tables
Base.metadata.create_all(bind=engine)

# Run Data Migrations
def run_migrations():
    db = SessionLocal()
    try:
        crud.migrate_capitalize_user_names(db)
    finally:
        db.close()

run_migrations()

app = FastAPI(title="Classly")

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Domain Migration Middleware
from fastapi import Request
from fastapi.responses import RedirectResponse
from app.i18n import i18n

@app.middleware("http")
async def language_middleware(request: Request, call_next):
    # 1. Query Param
    lang = request.query_params.get("lang")

    # 2. Cookie
    if not lang:
        lang = request.cookies.get("NEXT_LOCALE") or request.cookies.get("lang")

    # 3. Accept-Language Header
    if not lang:
        accept = request.headers.get("Accept-Language")
        if accept:
            # Simple parser: take first 2 chars of first part
            # e.g., "de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7" -> "de"
            lang = accept.split(",")[0].strip()[:2]

    # 4. Fallback
    if not lang:
        lang = i18n.default_lang

    # Validation (check if we have translation)
    if lang not in i18n.translations:
        lang = i18n.default_lang

    request.state.lang = lang

    # Helper function for templates
    def t(key):
        return i18n.get_translation(request.state.lang, key)

    request.state.t = t

    response = await call_next(request)
    return response

@app.middleware("http")
async def domain_migration_middleware(request: Request, call_next):
    # Configuration via Environment Variables
    # Example: MIGRATE_FROM_DOMAIN="old.example.com", MIGRATE_TO_DOMAIN="new.example.com"
    old_domain = os.getenv("MIGRATE_FROM_DOMAIN")
    new_domain = os.getenv("MIGRATE_TO_DOMAIN")
    
    if old_domain and new_domain:
        host = request.headers.get("host", "").split(":")[0]
        
        if host == old_domain:
            # Check for session token
            session_token = request.cookies.get("session_token")
            
            if session_token:
                # Redirect with token for migration
                # Ensure we use https if likely (or respect scheme)
                return RedirectResponse(f"https://{new_domain}/auth/migrate-session?token={session_token}")
            else:
                # Just redirect guests
                return RedirectResponse(f"https://{new_domain}")
            
    return await call_next(request)

# Include Routers
app.include_router(auth.router)
app.include_router(pages.router)
app.include_router(events.router)
app.include_router(admin.router)
app.include_router(caldav.router)
app.include_router(preferences.router)
app.include_router(grades.router)
app.include_router(timetable.router)
app.include_router(i18n_router.router)
