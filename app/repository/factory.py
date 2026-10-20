import os
from fastapi import Depends, HTTPException
from collections.abc import Iterator
from app.database import SessionLocal
from app.repository.base import BaseRepository
from app.repository.sql import SqlAlchemyRepository
from app.repository.appwrite import AppwriteRepository

# Global Appwrite Repo instance to reuse client connection
_appwrite_repo = None


def get_repository() -> Iterator[BaseRepository]:
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


def require_sql_repository(repo: BaseRepository) -> SqlAlchemyRepository:
    """Narrow SQL-only operations without pretending Appwrite exposes a Session."""
    if not isinstance(repo, SqlAlchemyRepository):
        raise HTTPException(
            status_code=501,
            detail="This operation is unavailable for the configured storage backend.",
        )
    return repo


def get_sql_repository(
    repo: BaseRepository = Depends(get_repository),
) -> SqlAlchemyRepository:
    return require_sql_repository(repo)
