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
        calendar_data = calendar_utils.get_month_calendar(year, month, events)
        
        members = []
        if user.role in [models.UserRole.OWNER, models.UserRole.ADMIN]:
            members = crud.get_class_members(db, clazz.id)
        
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
            "base_url": str(request.base_url).rstrip("/")
        })
    else:
        return templates.TemplateResponse("landing.html", {"request": request})
