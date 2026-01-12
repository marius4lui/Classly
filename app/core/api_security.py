from fastapi import Security, HTTPException, Depends
from fastapi.security.api_key import APIKeyHeader
from starlette.status import HTTP_403_FORBIDDEN
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import ApiKey
import hashlib
from datetime import datetime

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

async def get_api_key_user(
    api_key_header: str = Security(api_key_header),
    db: Session = Depends(get_db)
):
    if not api_key_header:
        return None

    # Hash the key
    key_hash = hashlib.sha256(api_key_header.encode()).hexdigest()

    # Find in DB
    api_key = db.query(ApiKey).filter(ApiKey.key_hash == key_hash).first()

    if not api_key:
        return None

    # Check expiry
    if api_key.expires_at and api_key.expires_at < datetime.utcnow():
        return None

    return api_key.user
