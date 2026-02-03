"""
Classly API v1 - Audit Log Endpoints
=====================================
Endpoints für Audit-Log Abfragen (nur Admins).
"""

from fastapi import APIRouter, Depends, Query
from app.repository.factory import get_repository
from app.repository.base import BaseRepository
from app import models
from .deps import require_audit_read

router = APIRouter(prefix="/audit-log", tags=["Audit"])


@router.get("")
def get_audit_log(
    auth = Depends(require_audit_read),
    repo: BaseRepository = Depends(get_repository),
    limit: int = Query(100, le=500, description="Max entries to return"),
    offset: int = Query(0, ge=0, description="Offset for pagination")
):
    """
    Ruft Audit-Logs der Klasse ab.
    
    **Erforderlicher Scope:** `audit:read`
    
    > DSGVO-Hinweis: Audit-Logs werden nach 90 Tagen automatisch gelöscht
    > (außer permanente Einträge wie Event-Löschungen).
    
    Query-Parameter:
    - `limit`: Max Einträge (default: 100, max: 500)
    - `offset`: Offset für Pagination
    """
    class_id = auth["class_id"]
    
    # Direkte DB-Abfrage mit Pagination
    logs = repo.db.query(models.AuditLog).filter(
        models.AuditLog.class_id == class_id
    ).order_by(
        models.AuditLog.created_at.desc()
    ).offset(offset).limit(limit).all()
    
    return {
        "class_id": class_id,
        "count": len(logs),
        "offset": offset,
        "limit": limit,
        "logs": [
            {
                "id": log.id,
                "action": log.action.value if hasattr(log.action, "value") else log.action,
                "user_id": log.user_id,
                "target_id": log.target_id,
                "data": log.data,
                "permanent": log.permanent,
                "created_at": log.created_at.isoformat() if log.created_at else None
            }
            for log in logs
        ]
    }
