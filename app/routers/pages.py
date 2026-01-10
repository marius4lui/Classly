from fastapi import APIRouter, Request, Depends, Query
from fastapi.templating import Jinja2Templates
from app.core.auth import get_current_user
from app import crud, models
from app.database import get_db
from sqlalchemy.orm import Session
from app.core import calendar_utils
import datetime

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/impressum")
def impressum(request: Request):
    legal_info = {
        "name": os.getenv("IMPRESSUM_NAME", "Nicht konfiguriert"),
        "street": os.getenv("IMPRESSUM_STREET", "Nicht konfiguriert"),
        "plz_ort": os.getenv("IMPRESSUM_PLZ_ORT", "Nicht konfiguriert"),
        "email": os.getenv("CONTACT_EMAIL", "Nicht konfiguriert")
    }
    return templates.TemplateResponse("impressum.html", {"request": request, "legal_info": legal_info})

@router.get("/datenschutz")
def datenschutz(request: Request):
    legal_info = {
        "name": os.getenv("IMPRESSUM_NAME", "Nicht konfiguriert"),
        "street": os.getenv("IMPRESSUM_STREET", "Nicht konfiguriert"),
        "plz_ort": os.getenv("IMPRESSUM_PLZ_ORT", "Nicht konfiguriert"),
        "email": os.getenv("CONTACT_EMAIL", "Nicht konfiguriert")
    }
    return templates.TemplateResponse("datenschutz.html", {"request": request, "legal_info": legal_info})

@router.get("/")
def index(
    request: Request, 
    user: models.User | None = Depends(get_current_user), 
    db: Session = Depends(get_db),
    year: int = Query(default=None),
    month: int = Query(default=None, ge=1, le=12)
):
    if user:
        clazz = crud.get_class(db, user.class_id)
        
        today = datetime.datetime.now()
        
        # Use query params or default to current month
        cal_year = year if year else today.year
        cal_month = month if month else today.month
        
        # Validate year range (reasonable bounds)
        if cal_year < 2020 or cal_year > 2100:
            cal_year = today.year
        
        # Calculate previous and next month
        prev_month = cal_month - 1
        prev_year = cal_year
        if prev_month < 1:
            prev_month = 12
            prev_year -= 1
        
        next_month = cal_month + 1
        next_year = cal_year
        if next_month > 12:
            next_month = 1
            next_year += 1
        
        events = crud.get_events_for_class(db, clazz.id)
        subjects = crud.get_subjects_for_class(db, clazz.id)
        
        # Filter upcoming events (today or future, sorted by date)
        dated_events = [e for e in events if e.date is not None]
        upcoming_events = [e for e in dated_events if e.date.date() >= today.date()]
        upcoming_events = sorted(upcoming_events, key=lambda x: x.date)[:10]
        
        # Infos (Type INFO)
        infos = [e for e in events if e.type == models.EventType.INFO]
        infos = sorted(infos, key=lambda x: x.created_at if x.created_at else datetime.datetime.min, reverse=True)
        
        members = []
        login_tokens = []
        if user.role in [models.UserRole.OWNER, models.UserRole.ADMIN, models.UserRole.CLASS_ADMIN]:
            members = crud.get_class_members(db, clazz.id)
            login_tokens = crud.get_login_tokens_for_class(db, clazz.id)
        
        # Single month calendar
        calendar_data = calendar_utils.get_month_calendar(cal_year, cal_month, dated_events)
        current_month_name = datetime.date(cal_year, cal_month, 1).strftime("%B %Y")
        
        return templates.TemplateResponse("dashboard.html", {
            "request": request, 
            "user": user, 
            "clazz": clazz,
            "calendar": calendar_data,
            "current_month": current_month_name,
            "current_year": cal_year,
            "current_month_num": cal_month,
            "prev_year": prev_year,
            "prev_month": prev_month,
            "next_year": next_year,
            "next_month": next_month,
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
