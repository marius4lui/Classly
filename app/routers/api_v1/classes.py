"""
Classly API v1 - Classes Endpoints
==================================
Endpoints für Klassen-Informationen.
"""

from fastapi import APIRouter, Depends, HTTPException
from app.repository.factory import get_repository
from app.repository.base import BaseRepository
from .deps import require_classes_read

router = APIRouter(prefix="/classes", tags=["Classes"])


@router.get("")
def list_classes(
    auth = Depends(require_classes_read),
    repo: BaseRepository = Depends(get_repository)
):
    """
    Gibt Informationen zur Klasse des API-Keys zurück.
    
    > Hinweis: API-Keys sind an eine Klasse gebunden, daher wird nur diese zurückgegeben.
    
    **Erforderlicher Scope:** `classes:read`
    """
    class_id = auth["class_id"]
    clazz = repo.get_class(class_id)
    
    if not clazz:
        raise HTTPException(status_code=404, detail="Class not found")
    
    return {
        "id": clazz.id,
        "name": clazz.name,
        "created_at": clazz.created_at.isoformat() if clazz.created_at else None,
        "member_count": len(clazz.users) if clazz.users else 0
    }


@router.get("/{class_id}")
def get_class(
    class_id: str,
    auth = Depends(require_classes_read),
    repo: BaseRepository = Depends(get_repository)
):
    """
    Detailinformationen zu einer Klasse.
    
    **Erforderlicher Scope:** `classes:read`
    """
    # Nur Zugriff auf eigene Klasse erlaubt
    if class_id != auth["class_id"]:
        raise HTTPException(status_code=403, detail="Access denied to this class")
    
    clazz = repo.get_class(class_id)
    if not clazz:
        raise HTTPException(status_code=404, detail="Class not found")
    
    subjects = repo.get_subjects_for_class(class_id)
    
    return {
        "id": clazz.id,
        "name": clazz.name,
        "created_at": clazz.created_at.isoformat() if clazz.created_at else None,
        "subjects": [
            {"id": s.id, "name": s.name, "color": s.color}
            for s in subjects
        ],
        "member_count": len(clazz.users) if clazz.users else 0
    }
