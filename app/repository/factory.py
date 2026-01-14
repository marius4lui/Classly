import os
from app.database import SessionLocal
from app.repository.base import BaseRepository
from app.repository.sql import SqlAlchemyRepository
from app.repository.appwrite import AppwriteRepository

# Global Appwrite Repo instance to reuse client connection
_appwrite_repo = None

def get_repository() -> BaseRepository:
    """
    Dependency provider for FastAPI.
    Returns the appropriate repository based on APPWRITE env var.
    """
    if os.getenv("APPWRITE", "").lower() == "true":
        global _appwrite_repo
        if _appwrite_repo is None:
            _appwrite_repo = AppwriteRepository()
        yield _appwrite_repo
    else:
        db = SessionLocal()
        try:
            yield SqlAlchemyRepository(db)
        finally:
            db.close()

# Synchronous factory for non-FastAPI contexts (scripts etc)
def get_repository_sync() -> BaseRepository:
    if os.getenv("APPWRITE", "").lower() == "true":
        return AppwriteRepository()
    else:
        return SqlAlchemyRepository(SessionLocal())
