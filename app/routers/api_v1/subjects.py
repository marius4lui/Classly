"""
Classly API v1 - Subjects Endpoints
====================================
Endpoints für Fächer-Informationen.
"""

from fastapi import APIRouter, Depends, HTTPException
from app.repository.factory import get_repository
from app.repository.base import BaseRepository
from .deps import require_subjects_read

router = APIRouter(prefix="/subjects", tags=["Subjects"])


@router.get("")
def list_subjects(
    auth = Depends(require_subjects_read),
    repo: BaseRepository = Depends(get_repository)
):
    """
    Listet alle Fächer der Klasse auf.
    
    **Erforderlicher Scope:** `subjects:read`
    """
    class_id = auth["class_id"]
    subjects = repo.get_subjects_for_class(class_id)
    
    return {
        "class_id": class_id,
        "count": len(subjects),
        "subjects": [
            {
                "id": s.id,
                "name": s.name,
                "color": s.color
            }
            for s in subjects
        ]
    }


@router.get("/{subject_id}")
def get_subject(
    subject_id: str,
    auth = Depends(require_subjects_read),
    repo: BaseRepository = Depends(get_repository)
):
    """
    Gibt ein spezifisches Fach zurück.
    
    **Erforderlicher Scope:** `subjects:read`
    """
    class_id = auth["class_id"]
    subject = repo.get_subject(subject_id)
    
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    
    if subject.class_id != class_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return {
        "id": subject.id,
        "name": subject.name,
        "color": subject.color
    }
