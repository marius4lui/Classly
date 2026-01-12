from fastapi import APIRouter, Depends, Form, HTTPException, Response, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app import crud, models
from app.core.auth import get_current_user, require_user, require_class_admin
from app.quotas import check_event_quota, check_subject_quota
from app.limiter import limiter
import datetime
import json

router = APIRouter()

@router.post("/events")
@limiter.limit("5/minute")
def create_event(
    request: Request,
    response: Response,
    type: str = Form(...),
    subject_id: str = Form(None),
    subject_name: str = Form(None),
    priority: str = Form("medium"), # Default medium

    date: str = Form(None),
    title: str = Form(None),
    user: models.User = Depends(require_user),
    db: Session = Depends(get_db)
):
    event_date = None
    if date:
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
    
    # Parse Priority
    try:
        event_priority = models.Priority(priority)
    except ValueError:
        event_priority = models.Priority.MEDIUM

    # Check Quota
    check_event_quota(db, user)

    event = crud.create_event(
        db=db, 
        class_id=user.class_id, 
        author_id=user.id, 
        type=type, 
        subject_id=subject_id,
        subject_name=actual_subject_name,
        date=event_date, 
        title=title,
        priority=event_priority
    )
    
    # Audit log (permanent)
    crud.create_audit_log(db, user.class_id, user.id, models.AuditAction.EVENT_CREATE,
                          target_id=event.id, data=json.dumps({"type": type, "subject": actual_subject_name, "priority": priority}),
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
        "priority": event.priority.value if event.priority else "medium", 
        "subject_name": event.subject_name,
        "title": event.title,
        "date": event.date.strftime("%Y-%m-%d") if event.date else None,
        "author": event.author.name if event.author else "Unbekannt",
        "created_at": event.created_at.isoformat() if event.created_at else None,
        "topics": [{"id": t.id, "type": t.topic_type, "content": t.content, "count": t.count, "parent_id": t.parent_id} for t in topics],
        "links": [{"id": l.id, "url": l.url, "label": l.label} for l in event.links]
    }

@router.put("/events/{event_id}")
def edit_event(
    event_id: str,
    response: Response,
    type: str = Form(None),
    subject_name: str = Form(None),
    title: str = Form(None),
    date: str = Form(None),
    priority: str = Form(None),
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
            
    event_priority = None
    if priority:
        try:
            event_priority = models.Priority(priority)
        except:
            pass
    
    crud.update_event(db, event_id, type=event_type, subject_name=subject_name, 
                      title=title, date=event_date, priority=event_priority)
    
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
    parent_id: str = Form(None),
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

    # Validate parent_id if provided
    if parent_id:
        parent_topic = db.query(models.EventTopic).filter(
            models.EventTopic.id == parent_id,
            models.EventTopic.event_id == event_id
        ).first()
        if not parent_topic:
            raise HTTPException(status_code=400, detail="Parent topic not found")

    topic = crud.create_event_topic(db, event_id, topic_type, content, count, order=len(existing_topics), parent_id=parent_id)
    
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

# --- Link Endpoints ---
@router.post("/events/{event_id}/links")
def add_link(
    event_id: str,
    url: str = Form(...),
    label: str = Form(...),
    user: models.User = Depends(require_user),
    db: Session = Depends(get_db)
):
    event = crud.get_event(db, event_id)
    if not event or event.class_id != user.class_id:
        raise HTTPException(status_code=404, detail="Event not found")
    
    # Check max links?
    if len(event.links) >= 10:
        raise HTTPException(status_code=400, detail="Max 10 links")

    link = crud.create_event_link(db, event_id, url, label)
    return {"status": "created", "link_id": link.id}

@router.delete("/events/{event_id}/links/{link_id}")
def delete_link_endpoint(
    event_id: str,
    link_id: str,
    user: models.User = Depends(require_user),
    db: Session = Depends(get_db)
):
    event = crud.get_event(db, event_id)
    if not event or event.class_id != user.class_id:
        raise HTTPException(status_code=404, detail="Event not found")
    
    crud.delete_link(db, link_id)
    return {"status": "deleted"}

# --- Subject Endpoints ---
@router.post("/subjects")
@limiter.limit("10/minute")
def create_subject(
    request: Request,
    response: Response,
    name: str = Form(...),
    color: str = Form("#666666"),
    user: models.User = Depends(require_class_admin),
    db: Session = Depends(get_db)
):
    # Check Quota
    check_subject_quota(db, user)

    crud.create_subject(db, class_id=user.class_id, name=name, color=color)
    response.headers["HX-Redirect"] = "/"
    return {"status": "created"}

@router.delete("/subjects/{subject_id}")
def delete_subject(
    subject_id: str,
    response: Response,
    user: models.User = Depends(require_class_admin),
    db: Session = Depends(get_db)
):
    deleted = crud.delete_subject(db, subject_id)
    if deleted:
        response.headers["HX-Redirect"] = "/"
        return {"status": "deleted"}
    else:
        raise HTTPException(status_code=404, detail="Subject not found")


# --- Feed Endpoints ---
@router.get("/feed/rss")
def get_rss_feed(
    request: Request,
    class_id: str = None,
    db: Session = Depends(get_db)
):
    if not class_id:
        return Response(content="Missing class_id", status_code=400)
    
    # Get INFO events
    events = db.query(models.Event).filter(
        models.Event.class_id == class_id,
        models.Event.type == models.EventType.INFO
    ).order_by(models.Event.created_at.desc()).limit(20).all()

    base_url = str(request.base_url).rstrip("/")
    
    # Build RSS 2.0 compliant items
    rss_items = ""
    for e in events:
        # RFC 822 date format
        pub_date = e.created_at.strftime("%a, %d %b %Y %H:%M:%S +0100") if e.created_at else ""
        title = (e.subject_name or 'Info') + (f": {e.title}" if e.title else "")
        # Escape XML special characters
        title = title.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        description = (e.title or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        item_link = f"{base_url}/#event-{e.id}"
        
        rss_items += f"""
  <item>
    <title>{title}</title>
    <link>{item_link}</link>
    <description>{description}</description>
    <pubDate>{pub_date}</pubDate>
    <guid>{item_link}</guid>
  </item>"""

    rss_content = f"""<?xml version="1.0" encoding="UTF-8" ?>
<rss version="2.0">

<channel>
  <title>Classly Info Feed</title>
  <link>{base_url}</link>
  <description>Neuigkeiten aus Classly</description>
  <language>de-de</language>
{rss_items}

</channel>
</rss>"""
    return Response(content=rss_content, media_type="text/xml")

@router.get("/feed/xml")
def get_xml_feed(
    class_id: str = None,
    db: Session = Depends(get_db)
):
    if not class_id:
        return Response(content="Missing class_id", status_code=400)
        
    events = db.query(models.Event).filter(
        models.Event.class_id == class_id,
        models.Event.type == models.EventType.INFO
    ).order_by(models.Event.created_at.desc()).limit(20).all()

    xml_items = ""
    for e in events:
        xml_items += f"""
    <event id="{e.id}">
        <subject>{e.subject_name or 'Info'}</subject>
        <content>{e.title or ''}</content>
        <createdAt>{e.created_at.isoformat() if e.created_at else ''}</createdAt>
    </event>"""

    xml_content = f"""<?xml version="1.0" encoding="UTF-8" ?>
<events>
{xml_items}
</events>"""
    return Response(content=xml_content, media_type="application/xml")
