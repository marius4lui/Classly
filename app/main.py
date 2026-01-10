import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.database import engine, Base, SQLALCHEMY_DATABASE_URL, SessionLocal
from app.routers import auth, pages, events, admin, caldav, preferences
from app import fix_db_schema, crud

# Fix DB Schema (Add missing columns to old SQLite volumes)
fix_db_schema.fix_schema(SQLALCHEMY_DATABASE_URL)

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
