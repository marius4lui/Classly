from fastapi import APIRouter, Depends, Form, HTTPException, Response
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app import crud, models
from app.core.auth import get_current_user, require_user
import datetime
import json

router = APIRouter()

@router.post("/events")
def create_event(
    response: Response,
    type: str = Form(...),
    subject_id: str = Form(None),
    subject_name: str = Form(None),
    date: str = Form(...),
    title: str = Form(None),
    user: models.User = Depends(require_user),
    db: Session = Depends(get_db)
):
    try:
        event_date = datetime.datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format")

    # Get subject name if subject_id provided
    actual_subject_name = subject_name
    if subject_id:
        subject = crud.get_subject(db, subject_id)
        if subject:
            actual_subject_name = subject.name

    event = crud.create_event(
        db=db, 
        class_id=user.class_id, 
        author_id=user.id, 
        type=type, 
        subject_id=subject_id,
        subject_name=actual_subject_name,
        date=event_date, 
        title=title
    )
    
    # Audit log (permanent)
    crud.create_audit_log(db, user.class_id, user.id, models.AuditAction.EVENT_CREATE,
                          target_id=event.id, data=json.dumps({"type": type, "subject": actual_subject_name}),
                          permanent=True)
    
    response.headers["HX-Redirect"] = "/"
    return {"status": "created", "event_id": event.id}

@router.get("/events/{event_id}")
def get_event_details(
    event_id: str,
    user: models.User = Depends(require_user),
    db: Session = Depends(get_db)
):
    event = crud.get_event(db, event_id)
    if not event or event.class_id != user.class_id:
        raise HTTPException(status_code=404, detail="Event not found")
    
    topics = crud.get_topics_for_event(db, event_id)
    
    return {
        "id": event.id,
        "type": event.type.value,
        "subject_name": event.subject_name,
        "title": event.title,
        "date": event.date.strftime("%Y-%m-%d"),
        "author": event.author.name if event.author else "Unbekannt",
        "created_at": event.created_at.isoformat() if event.created_at else None,
        "topics": [{"id": t.id, "type": t.topic_type, "content": t.content, "count": t.count} for t in topics]
    }

@router.put("/events/{event_id}")
def edit_event(
    event_id: str,
    response: Response,
    type: str = Form(None),
    subject_name: str = Form(None),
    title: str = Form(None),
    date: str = Form(None),
    user: models.User = Depends(require_user),
    db: Session = Depends(get_db)
):
    event = crud.get_event(db, event_id)
    if not event or event.class_id != user.class_id:
        raise HTTPException(status_code=404, detail="Event not found")
    
    event_date = None
    if date:
        try:
            event_date = datetime.datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format")
    
    event_type = None
    if type:
        try:
            event_type = models.EventType(type)
        except:
            pass
    
    crud.update_event(db, event_id, type=event_type, subject_name=subject_name, title=title, date=event_date)
    
    # Audit log (permanent)
    crud.create_audit_log(db, user.class_id, user.id, models.AuditAction.EVENT_EDIT,
                          target_id=event_id, data=json.dumps({"edited_by": user.name}),
                          permanent=True)
    
    response.headers["HX-Redirect"] = "/"
    return {"status": "updated"}

@router.delete("/events/{event_id}")
def delete_event(
    event_id: str,
    response: Response,
    user: models.User = Depends(require_user),
    db: Session = Depends(get_db)
):
    event = crud.get_event(db, event_id)
    if not event or event.class_id != user.class_id:
        raise HTTPException(status_code=404, detail="Event not found")
    
    # Audit log before delete (permanent)
    crud.create_audit_log(db, user.class_id, user.id, models.AuditAction.EVENT_DELETE,
                          target_id=event_id, data=json.dumps({"type": event.type.value, "subject": event.subject_name}),
                          permanent=True)
    
    crud.delete_event(db, event_id)
    response.headers["HX-Redirect"] = "/"
    return {"status": "deleted"}

# --- Topic Endpoints ---
@router.post("/events/{event_id}/topics")
def add_topic(
    event_id: str,
    response: Response,
    topic_type: str = Form(...),
    content: str = Form(None),
    count: int = Form(None),
    user: models.User = Depends(require_user),
    db: Session = Depends(get_db)
):
    event = crud.get_event(db, event_id)
    if not event or event.class_id != user.class_id:
        raise HTTPException(status_code=404, detail="Event not found")
    
    # Only KA/TEST can have topics
    if event.type not in [models.EventType.KA, models.EventType.TEST]:
        raise HTTPException(status_code=400, detail="Only KA/TEST can have topics")
    
    existing_topics = crud.get_topics_for_event(db, event_id)
    if len(existing_topics) >= 20:
        raise HTTPException(status_code=400, detail="Max 20 topics")
    
    topic = crud.create_event_topic(db, event_id, topic_type, content, count, order=len(existing_topics))
    
    # Audit log (permanent)
    crud.create_audit_log(db, user.class_id, user.id, models.AuditAction.TOPIC_ADD,
                          target_id=event_id, data=json.dumps({"topic": topic_type}),
                          permanent=True)
    
    return {"status": "created", "topic_id": topic.id}

@router.delete("/events/{event_id}/topics/{topic_id}")
def delete_topic_endpoint(
    event_id: str,
    topic_id: str,
    user: models.User = Depends(require_user),
    db: Session = Depends(get_db)
):
    event = crud.get_event(db, event_id)
    if not event or event.class_id != user.class_id:
        raise HTTPException(status_code=404, detail="Event not found")
    
    crud.delete_topic(db, topic_id)
    return {"status": "deleted"}

# --- Subject Endpoints ---
@router.post("/subjects")
def create_subject(
    response: Response,
    name: str = Form(...),
    color: str = Form("#666666"),
    user: models.User = Depends(require_user),
    db: Session = Depends(get_db)
):
    crud.create_subject(db, class_id=user.class_id, name=name, color=color)
    response.headers["HX-Redirect"] = "/"
    return {"status": "created"}

@router.delete("/subjects/{subject_id}")
def delete_subject(
    subject_id: str,
    response: Response,
    user: models.User = Depends(require_user),
    db: Session = Depends(get_db)
):
    deleted = crud.delete_subject(db, subject_id)
    if deleted:
        response.headers["HX-Redirect"] = "/"
        return {"status": "deleted"}
    else:
        raise HTTPException(status_code=404, detail="Subject not found")

