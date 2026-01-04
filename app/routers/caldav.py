from fastapi import APIRouter, Depends, HTTPException, Response, Form
from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app import crud, models
from app.core.auth import require_user
from icalendar import Calendar, Event
import datetime

router = APIRouter()

@router.get("/caldav/{token}/calendar.ics")
def get_calendar(
    token: str,
    db: Session = Depends(get_db)
):
    """Get calendar as ICS file"""
    user = crud.get_user_by_caldav_token(db, token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid CalDAV token")
    
    events = crud.get_events_for_class(db, user.class_id)
    clazz = crud.get_class(db, user.class_id)
    
    # Build ICS
    cal = Calendar()
    cal.add('prodid', '-//Classly//Calendar//DE')
    cal.add('version', '2.0')
    cal.add('x-wr-calname', f'{clazz.name} - Classly')
    
    for ev in events:
        event = Event()
        event.add('uid', f'{ev.id}@classly')
        event.add('summary', f'{ev.type.value}: {ev.subject_name or ev.title or "Event"}')
        event.add('dtstart', ev.date.date())
        event.add('dtend', ev.date.date() + datetime.timedelta(days=1))
        if ev.title:
            event.add('description', ev.title)
        cal.add_component(event)
    
    return PlainTextResponse(
        content=cal.to_ical().decode('utf-8'),
        media_type='text/calendar',
        headers={'Content-Disposition': 'attachment; filename="calendar.ics"'}
    )

# CalDAV settings endpoints
@router.post("/caldav/enable")
def enable_caldav(
    response: Response,
    write: bool = Form(False),
    user: models.User = Depends(require_user),
    db: Session = Depends(get_db)
):
    crud.enable_caldav(db, user.id, write=write)
    response.headers["HX-Redirect"] = "/"
    return {"status": "enabled"}

@router.post("/caldav/disable")
def disable_caldav(
    response: Response,
    user: models.User = Depends(require_user),
    db: Session = Depends(get_db)
):
    crud.disable_caldav(db, user.id)
    response.headers["HX-Redirect"] = "/"
    return {"status": "disabled"}

@router.post("/caldav/regenerate")
def regenerate_caldav_token(
    response: Response,
    user: models.User = Depends(require_user),
    db: Session = Depends(get_db)
):
    crud.regenerate_caldav_token(db, user.id)
    response.headers["HX-Redirect"] = "/"
    return {"status": "regenerated"}
