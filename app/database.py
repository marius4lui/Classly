import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./classly.db")

connect_args = {}
engine_args = {}

if SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}
else:
    # Pool settings for non-SQLite databases
    pool_size = int(os.getenv("DATABASE_POOL_SIZE", "10"))
    pool_recycle = int(os.getenv("DATABASE_POOL_MAX_LIFETIME", "3600"))
    engine_args = {
        "pool_size": pool_size,
        "pool_recycle": pool_recycle,
    }

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args=connect_args,
    **engine_args
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
