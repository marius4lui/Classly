from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
import json

from app.database import get_db
from app.models import User, UserPreferences
from app.core.auth import get_current_user

router = APIRouter(
    prefix="/preferences",
    tags=["preferences"],
    responses={404: {"description": "Not found"}},
)

class PreferencesUpdate(BaseModel):
    filter_subjects: List[str]
    filter_event_types: List[str]
    filter_priority: List[str] = []

@router.get("")
def get_preferences(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    prefs = db.query(UserPreferences).filter(UserPreferences.user_id == current_user.id).first()
    
    if not prefs:
        # Return defaults
        return {
            "filter_subjects": [],
            "filter_event_types": [],
            "filter_priority": []
        }
        
    return {
        "filter_subjects": json.loads(prefs.filter_subjects),
        "filter_event_types": json.loads(prefs.filter_event_types),
        "filter_priority": json.loads(prefs.filter_priority),
    }

@router.put("")
def update_preferences(
    data: PreferencesUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    prefs = db.query(UserPreferences).filter(UserPreferences.user_id == current_user.id).first()
    
    if not prefs:
        prefs = UserPreferences(user_id=current_user.id)
        db.add(prefs)
    
    prefs.filter_subjects = json.dumps(data.filter_subjects)
    prefs.filter_event_types = json.dumps(data.filter_event_types)
    prefs.filter_priority = json.dumps(data.filter_priority)
    
    db.commit()
    return {"status": "ok"}
