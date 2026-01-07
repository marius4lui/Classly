from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from app.core.auth import get_current_user
from app import crud, models
from app.database import get_db
from sqlalchemy.orm import Session
from app.core import calendar_utils
import datetime

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/")
def index(
    request: Request, 
    user: models.User | None = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    if user:
        clazz = crud.get_class(db, user.class_id)
        
        today = datetime.datetime.now()
        year = today.year
        month = today.month
        
        events = crud.get_events_for_class(db, clazz.id)
        subjects = crud.get_subjects_for_class(db, clazz.id)
        # calendar_data initialized later with dated events only
        
        # Filter upcoming events (today or future, sorted by date)
        # Handle nullable date: if date is None, it's undated (Info).
        # We only want dated events for 'upcoming_events' and 'calendar'.
        
        dated_events = [e for e in events if e.date is not None]
        upcoming_events = [e for e in dated_events if e.date.date() >= today.date()]
        upcoming_events = sorted(upcoming_events, key=lambda x: x.date)[:10]  # Top 10
        
        # Infos (Type INFO), specific logic:
        # Show all INFO events regardless of date? Or sorted by creation?
        # User said "must not be bound to a date".
        # We'll fetch all INFO events separately or filter from 'events'.
        infos = [e for e in events if e.type == models.EventType.INFO]
        # Sort by creation date desc (newest first) or date if present?
        # Let's sort by created_at desc.
        infos = sorted(infos, key=lambda x: x.created_at if x.created_at else datetime.datetime.min, reverse=True)
        
        members = []
        login_tokens = []
        if user.role in [models.UserRole.OWNER, models.UserRole.ADMIN]:
            members = crud.get_class_members(db, clazz.id)
            login_tokens = crud.get_login_tokens_for_class(db, clazz.id)
        
        # Calendar needs dated events only
        calendar_data = calendar_utils.get_month_calendar(year, month, dated_events)
        
        return templates.TemplateResponse("dashboard.html", {
            "request": request, 
            "user": user, 
            "clazz": clazz,
            "calendar": calendar_data,
            "current_month": today.strftime("%B %Y"),
            "current_year": year,
            "current_month_num": month,
            "today": today,
            "members": members,
            "subjects": subjects,
            "login_tokens": login_tokens,
            "upcoming_events": upcoming_events,
            "infos": infos,
            "base_url": str(request.base_url).rstrip("/")
        })
    else:
        return templates.TemplateResponse("landing.html", {"request": request})
