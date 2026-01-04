from fastapi import APIRouter, Depends, Form, HTTPException, Response
from sqlalchemy.orm import Session
from app.database import get_db
from app import crud, models
from app.core.auth import get_current_user, require_user
import datetime

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

    crud.create_event(
        db=db, 
        class_id=user.class_id, 
        author_id=user.id, 
        type=type, 
        subject_id=subject_id,
        subject_name=actual_subject_name,
        date=event_date, 
        title=title
    )
    
    response.headers["HX-Redirect"] = "/"
    return {"status": "created"}

@router.delete("/events/{event_id}")
def delete_event(
    event_id: str,
    response: Response,
    user: models.User = Depends(require_user),
    db: Session = Depends(get_db)
):
    deleted = crud.delete_event(db, event_id)
    if deleted:
        response.headers["HX-Redirect"] = "/"
        return {"status": "deleted"}
    else:
        raise HTTPException(status_code=404, detail="Event not found")

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
