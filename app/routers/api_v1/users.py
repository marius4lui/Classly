"""
Classly API v1 - Users Endpoints
================================
Endpoints für Benutzer-Informationen.
"""

from fastapi import APIRouter, Depends, HTTPException
from app.repository.factory import get_repository
from app.repository.base import BaseRepository
from .deps import require_users_read

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("")
def list_users(
    auth = Depends(require_users_read),
    repo: BaseRepository = Depends(get_repository)
):
    """
    Listet alle Benutzer der Klasse auf.
    
    **Erforderlicher Scope:** `users:read`
    
    > DSGVO-Hinweis: Nur nicht-sensible Daten werden zurückgegeben.
    """
    class_id = auth["class_id"]
    members = repo.get_class_members(class_id)
    
    return {
        "class_id": class_id,
        "count": len(members),
        "users": [
            {
                "id": user.id,
                "name": user.name,
                "role": user.role.value if hasattr(user.role, "value") else user.role,
                "created_at": user.created_at.isoformat() if user.created_at else None
            }
            for user in members
        ]
    }


@router.get("/me")
def get_current_user(
    auth = Depends(require_users_read),
    repo: BaseRepository = Depends(get_repository)
):
    """
    Gibt Informationen zum Benutzer des API-Keys zurück.
    
    **Erforderlicher Scope:** `users:read`
    """
    user = auth["user"]
    api_key = auth["api_key"]
    
    return {
        "user": {
            "id": user.id,
            "name": user.name,
            "role": user.role.value if hasattr(user.role, "value") else user.role,
            "class_id": user.class_id,
            "created_at": user.created_at.isoformat() if user.created_at else None
        },
        "api_key": {
            "id": api_key.id,
            "name": api_key.name,
            "scopes": api_key.scopes,
            "expires_at": api_key.expires_at.isoformat() if api_key.expires_at else None,
            "last_used_at": api_key.last_used_at.isoformat() if api_key.last_used_at else None
        }
    }


@router.get("/{user_id}")
def get_user(
    user_id: str,
    auth = Depends(require_users_read),
    repo: BaseRepository = Depends(get_repository)
):
    """
    Gibt Informationen zu einem spezifischen Benutzer zurück.
    
    **Erforderlicher Scope:** `users:read`
    """
    class_id = auth["class_id"]
    user = repo.get_user(user_id)
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Nur Zugriff auf User der eigenen Klasse
    if user.class_id != class_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return {
        "id": user.id,
        "name": user.name,
        "role": user.role.value if hasattr(user.role, "value") else user.role,
        "created_at": user.created_at.isoformat() if user.created_at else None
    }
