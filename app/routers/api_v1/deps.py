"""
Classly API v1 - Dependencies
=============================
Shared Dependencies für alle API v1 Endpoints.
Beinhaltet API-Key Authentifizierung mit Scope-Prüfung.
"""

import datetime
import json
from fastapi import Header, HTTPException, Request, Depends
from app.repository.factory import get_repository
from app.repository.base import BaseRepository
from app.core.scopes import APIScope, parse_scopes, has_scope
from app import crud, models


class APIKeyAuth:
    """
    Dependency für API-Key Authentifizierung mit Scope-Prüfung.
    
    Usage:
        @router.get("/events")
        def list_events(auth = Depends(APIKeyAuth(APIScope.EVENTS_READ))):
            ...
    """
    
    def __init__(self, required_scope: APIScope = None):
        self.required_scope = required_scope
    
    def __call__(
        self,
        request: Request,
        authorization: str = Header(None),
        repo: BaseRepository = Depends(get_repository)
    ):
        # Token extrahieren
        if not authorization:
            raise HTTPException(
                status_code=401,
                detail="Missing Authorization header",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        if not authorization.startswith("Bearer "):
            raise HTTPException(
                status_code=401,
                detail="Invalid Authorization header. Expected 'Bearer <token>'",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        raw_token = authorization[7:].strip()
        if not raw_token:
            raise HTTPException(
                status_code=401,
                detail="Empty token",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        # Token validieren (unterstützt Hash + Legacy)
        api_key = crud.get_api_key_by_token(repo.db, raw_token)
        if not api_key:
            raise HTTPException(status_code=401, detail="Invalid API key")
        
        # Revoked prüfen
        if api_key.revoked:
            raise HTTPException(status_code=401, detail="API key has been revoked")
        
        # Ablauf prüfen
        if api_key.expires_at and api_key.expires_at < datetime.datetime.utcnow():
            raise HTTPException(status_code=401, detail="API key expired")
        
        # IP-Allowlist prüfen (falls konfiguriert)
        if api_key.ip_allowlist:
            try:
                allowed_ips = json.loads(api_key.ip_allowlist)
                client_ip = request.client.host if request.client else None
                if client_ip and allowed_ips and client_ip not in allowed_ips:
                    raise HTTPException(status_code=403, detail="IP address not allowed")
            except json.JSONDecodeError:
                pass  # Ignore invalid JSON
        
        # Scope prüfen
        granted_scopes = parse_scopes(api_key.scopes)
        if self.required_scope and not has_scope(granted_scopes, self.required_scope):
            raise HTTPException(
                status_code=403,
                detail=f"Missing required scope: {self.required_scope.value}"
            )
        
        # Last-used aktualisieren
        api_key.last_used_at = datetime.datetime.utcnow()
        repo.db.commit()
        
        # User laden
        user = repo.get_user(api_key.user_id)
        if not user:
            raise HTTPException(status_code=401, detail="User not found for API key")
        
        return {
            "api_key": api_key,
            "user": user,
            "scopes": granted_scopes,
            "class_id": api_key.class_id
        }


# Convenience-Dependencies für häufige Scope-Anforderungen
require_classes_read = APIKeyAuth(APIScope.CLASSES_READ)
require_classes_write = APIKeyAuth(APIScope.CLASSES_WRITE)
require_events_read = APIKeyAuth(APIScope.EVENTS_READ)
require_events_write = APIKeyAuth(APIScope.EVENTS_WRITE)
require_users_read = APIKeyAuth(APIScope.USERS_READ)
require_users_write = APIKeyAuth(APIScope.USERS_WRITE)
require_timetable_read = APIKeyAuth(APIScope.TIMETABLE_READ)
require_timetable_write = APIKeyAuth(APIScope.TIMETABLE_WRITE)
require_subjects_read = APIKeyAuth(APIScope.SUBJECTS_READ)
require_subjects_write = APIKeyAuth(APIScope.SUBJECTS_WRITE)
require_webhooks_manage = APIKeyAuth(APIScope.WEBHOOKS_MANAGE)

# Ohne Scope-Anforderung (nur gültiger Token)
require_any_auth = APIKeyAuth()

