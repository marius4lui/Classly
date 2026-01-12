import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.database import engine, Base, SQLALCHEMY_DATABASE_URL, SessionLocal
from app.routers import auth, pages, events, admin, caldav, preferences, grades, timetable
from app import fix_db_schema, crud, auto_migrate
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from app.limiter import limiter

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

# Rate Limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# Max File Size Middleware
from fastapi import Request
from fastapi.responses import JSONResponse
MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", "10"))
MAX_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024

@app.middleware("http")
async def check_content_length(request: Request, call_next):
    content_length = request.headers.get("content-length")
    if content_length:
        try:
            length = int(content_length)
            if length > MAX_BYTES:
                 return JSONResponse(status_code=413, content={"detail": f"Request entity too large. Max {MAX_FILE_SIZE_MB}MB."})
        except ValueError:
            pass
    return await call_next(request)

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
app.include_router(grades.router)
app.include_router(timetable.router)
