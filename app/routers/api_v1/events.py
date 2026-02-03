"""
Classly API v1 - Events Endpoints
=================================
Endpoints für Event-Verwaltung (Read/Write).
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.repository.factory import get_repository
from app.repository.base import BaseRepository
from app import models
from .deps import require_events_read, require_events_write

router = APIRouter(prefix="/events", tags=["Events"])


# --- Pydantic Schemas ---

class EventCreate(BaseModel):
    """Schema für Event-Erstellung."""
    type: str  # KA, TEST, HA, INFO
    subject_id: Optional[str] = None
    subject_name: Optional[str] = None
    title: Optional[str] = None
    date: datetime
    priority: Optional[str] = "MEDIUM"


class EventUpdate(BaseModel):
    """Schema für Event-Aktualisierung."""
    title: Optional[str] = None
    subject_name: Optional[str] = None
    date: Optional[datetime] = None
    priority: Optional[str] = None


# --- Endpoints ---

@router.get("")
def list_events(
    auth = Depends(require_events_read),
    repo: BaseRepository = Depends(get_repository),
    updated_since: Optional[str] = Query(None, description="ISO timestamp filter"),
    limit: int = Query(200, le=500, description="Max events to return")
):
    """
    Listet alle Events der Klasse auf.
    
    **Erforderlicher Scope:** `events:read`
    
    Query-Parameter:
    - `updated_since`: Nur Events nach diesem Zeitpunkt (ISO-Format)
    - `limit`: Maximale Anzahl (default: 200, max: 500)
    """
    class_id = auth["class_id"]
    
    since_dt = None
    if updated_since:
        try:
            since_dt = datetime.fromisoformat(updated_since.replace("Z", "+00:00"))
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid updated_since format. Use ISO 8601.")
    
    events = repo.list_events(
        class_id=class_id,
        limit=limit,
        updated_since=since_dt
    )
    
    return {
        "class_id": class_id,
        "count": len(events),
        "events": [_serialize_event(e) for e in events]
    }


@router.get("/{event_id}")
def get_event(
    event_id: str,
    auth = Depends(require_events_read),
    repo: BaseRepository = Depends(get_repository)
):
    """
    Gibt ein spezifisches Event zurück.
    
    **Erforderlicher Scope:** `events:read`
    """
    class_id = auth["class_id"]
    event = repo.get_event(event_id)
    
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    if event.class_id != class_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return _serialize_event(event, include_topics=True, include_links=True)


@router.post("", status_code=201)
def create_event(
    event: EventCreate,
    auth = Depends(require_events_write),
    repo: BaseRepository = Depends(get_repository)
):
    """
    Erstellt ein neues Event.
    
    **Erforderlicher Scope:** `events:write`
    """
    class_id = auth["class_id"]
    user = auth["user"]
    api_key = auth["api_key"]
    
    # Typ validieren
    try:
        event_type = models.EventType(event.type)
    except ValueError:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid event type. Allowed: {[e.value for e in models.EventType]}"
        )
    
    # Priorität validieren
    try:
        priority = models.Priority(event.priority) if event.priority else models.Priority.MEDIUM
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid priority. Allowed: {[p.value for p in models.Priority]}"
        )
    
    new_event = repo.create_event(
        class_id=class_id,
        author_id=user.id,
        type=event_type,
        date=event.date,
        subject_id=event.subject_id,
        subject_name=event.subject_name,
        title=event.title,
        priority=priority
    )
    
    # Audit-Log
    repo.create_audit_log(
        class_id=class_id,
        user_id=user.id,
        action=models.AuditAction.EVENT_CREATE,
        target_id=new_event.id,
        data=f'{{"via": "api_v1", "key_id": "{api_key.id}", "key_name": "{api_key.name or "unnamed"}"}}'
    )
    
    return {
        "id": new_event.id,
        "created": True,
        "event": _serialize_event(new_event)
    }


@router.put("/{event_id}")
def update_event(
    event_id: str,
    event: EventUpdate,
    auth = Depends(require_events_write),
    repo: BaseRepository = Depends(get_repository)
):
    """
    Aktualisiert ein bestehendes Event.
    
    **Erforderlicher Scope:** `events:write`
    """
    class_id = auth["class_id"]
    user = auth["user"]
    api_key = auth["api_key"]
    
    existing = repo.get_event(event_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Event not found")
    
    if existing.class_id != class_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Priorität validieren falls angegeben
    priority = None
    if event.priority:
        try:
            priority = models.Priority(event.priority)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid priority")
    
    updated = repo.update_event(
        event_id=event_id,
        title=event.title,
        subject_name=event.subject_name,
        date=event.date,
        priority=priority
    )
    
    # Audit-Log
    repo.create_audit_log(
        class_id=class_id,
        user_id=user.id,
        action=models.AuditAction.EVENT_EDIT,
        target_id=event_id,
        data=f'{{"via": "api_v1", "key_id": "{api_key.id}"}}'
    )
    
    return {
        "id": event_id,
        "updated": True,
        "event": _serialize_event(updated)
    }


@router.delete("/{event_id}")
def delete_event(
    event_id: str,
    auth = Depends(require_events_write),
    repo: BaseRepository = Depends(get_repository)
):
    """
    Löscht ein Event.
    
    **Erforderlicher Scope:** `events:write`
    """
    class_id = auth["class_id"]
    user = auth["user"]
    api_key = auth["api_key"]
    
    event = repo.get_event(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    if event.class_id != class_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    repo.delete_event(event_id)
    
    # Audit-Log
    repo.create_audit_log(
        class_id=class_id,
        user_id=user.id,
        action=models.AuditAction.EVENT_DELETE,
        target_id=event_id,
        data=f'{{"via": "api_v1", "key_id": "{api_key.id}"}}',
        permanent=True  # Event-Löschungen sind permanent
    )
    
    return {"id": event_id, "deleted": True}


# --- Helpers ---

def _serialize_event(
    event: models.Event, 
    include_topics: bool = False, 
    include_links: bool = False
) -> dict:
    """Serialisiert ein Event-Model zu einem Dict."""
    result = {
        "id": event.id,
        "class_id": event.class_id,
        "type": event.type.value if hasattr(event.type, "value") else event.type,
        "priority": event.priority.value if event.priority and hasattr(event.priority, "value") else (event.priority or "MEDIUM"),
        "subject_id": event.subject_id,
        "subject_name": event.subject_name,
        "title": event.title,
        "date": event.date.isoformat() if event.date else None,
        "author_id": event.author_id,
        "created_at": event.created_at.isoformat() if event.created_at else None,
        "updated_at": event.updated_at.isoformat() if event.updated_at else None
    }
    
    if include_topics:
        try:
            topics = event.topics or []
            result["topics"] = [
                {
                    "id": t.id,
                    "topic_type": t.topic_type,
                    "content": t.content,
                    "count": t.count,
                    "pages": t.pages,
                    "order": t.order,
                    "parent_id": t.parent_id
                }
                for t in topics
            ]
        except Exception:
            result["topics"] = []
    
    if include_links:
        try:
            links = event.links or []
            result["links"] = [
                {"id": l.id, "url": l.url, "label": l.label}
                for l in links
            ]
        except Exception:
            result["links"] = []
    
    return result
