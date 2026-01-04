from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.database import engine, Base, SQLALCHEMY_DATABASE_URL
from app.routers import auth, pages, events, admin, caldav
from app import fix_db_schema

# Fix DB Schema (Add missing columns to old SQLite volumes)
fix_db_schema.fix_schema(SQLALCHEMY_DATABASE_URL)

# Create Tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Classly")

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Include Routers
app.include_router(auth.router)
app.include_router(pages.router)
app.include_router(events.router)
app.include_router(admin.router)
app.include_router(caldav.router)
