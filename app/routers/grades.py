from fastapi import APIRouter, Depends, Form, HTTPException, Response
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app import crud, models
from app.core.auth import get_current_user

router = APIRouter(prefix="/grades", tags=["grades"])

def require_registered_user(user: models.User = Depends(get_current_user)):
    """Require a registered user for grade management"""
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    if not user.is_registered:
        raise HTTPException(status_code=403, detail="Registration required for grade management")
    return user

@router.post("")
def create_or_update_grade(
    event_id: str = Form(...),
    grade: float = Form(...),
    weight: float = Form(1.0),
    user: models.User = Depends(require_registered_user),
    db: Session = Depends(get_db)
):
    """Create or update a grade for an event"""
    # Validate grade range
    if grade < 1.0 or grade > 6.0:
        raise HTTPException(status_code=400, detail="Grade must be between 1.0 and 6.0")
    
    # Validate weight range
    if weight < 0.1 or weight > 2.0:
        weight = 1.0
    
    # Validate that event exists and belongs to user's class
    event = crud.get_event(db, event_id)
    if not event or event.class_id != user.class_id:
        raise HTTPException(status_code=404, detail="Event not found")
    
    # Only allow grades for KA/TEST events
    if event.type not in [models.EventType.KA, models.EventType.TEST]:
        raise HTTPException(status_code=400, detail="Grades can only be added to KA/TEST events")
    
    result = crud.create_grade(db, user.id, event_id, grade, weight)
    if not result:
        raise HTTPException(status_code=400, detail="Failed to save grade")
    
    return {"status": "success", "grade": result.grade, "weight": result.weight}

@router.get("/event/{event_id}")
def get_grade_for_event(
    event_id: str,
    user: models.User = Depends(require_registered_user),
    db: Session = Depends(get_db)
):
    """Get the user's grade for a specific event"""
    grade = crud.get_grade(db, user.id, event_id)
    if grade:
        return {"grade": grade.grade, "weight": grade.weight, "id": grade.id}
    return {"grade": None, "weight": None}

@router.delete("/{grade_id}")
def delete_grade(
    grade_id: str,
    user: models.User = Depends(require_registered_user),
    db: Session = Depends(get_db)
):
    """Delete a grade"""
    if crud.delete_grade(db, grade_id, user.id):
        return {"status": "deleted"}
    raise HTTPException(status_code=404, detail="Grade not found")

@router.get("/statistics")
def get_statistics(
    user: models.User = Depends(require_registered_user),
    db: Session = Depends(get_db)
):
    """Get grade statistics for the current user"""
    stats = crud.get_grade_statistics(db, user.id, user.class_id)
    return stats
