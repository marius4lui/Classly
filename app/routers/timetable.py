from fastapi import APIRouter, Depends, Form, HTTPException, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.database import get_db
from app import crud, models
from app.core.auth import get_current_user
from app.core import security
from datetime import datetime, time, timedelta
from typing import Optional

router = APIRouter(prefix="/timetable", tags=["timetable"])

# === Helper Functions ===

def require_user(user: models.User = Depends(get_current_user)):
    """Require any logged-in user"""
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user

def require_registered_user(user: models.User = Depends(get_current_user)):
    """
    Backwards-compat helper.

    Timetable should be usable for any logged-in class member, not only users
    with email/password registration.
    """
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user

def require_admin(user: models.User = Depends(get_current_user)):
    """Require admin role for timetable management"""
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    if user.role not in [models.UserRole.OWNER, models.UserRole.ADMIN, models.UserRole.CLASS_ADMIN]:
        raise HTTPException(status_code=403, detail="Admin access required")
    return user

WEEKDAY_NAMES = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag"]

def calculate_slot_time(settings: models.TimetableSettings, slot_number: int):
    """Calculate start/end time for a slot based on settings"""
    start_minutes = settings.day_start_hour * 60 + settings.day_start_minute
    slot_start = start_minutes + (slot_number - 1) * (settings.slot_duration + settings.break_duration)
    slot_end = slot_start + settings.slot_duration
    
    start_h, start_m = divmod(slot_start, 60)
    end_h, end_m = divmod(slot_end, 60)
    
    return f"{start_h:02d}:{start_m:02d}", f"{end_h:02d}:{end_m:02d}"

# === Settings Endpoints ===

@router.get("/settings")
def get_settings(
    user: models.User = Depends(require_user),
    db: Session = Depends(get_db)
):
    """Get timetable settings for user's class"""
    settings = db.query(models.TimetableSettings).filter(
        models.TimetableSettings.class_id == user.class_id
    ).first()
    
    if not settings:
        # Return defaults
        return {
            "slot_duration": 45,
            "break_duration": 15,
            "day_start_hour": 8,
            "day_start_minute": 0,
            "day_end_hour": 16,
            "day_end_minute": 0
        }
    
    return {
        "id": settings.id,
        "slot_duration": settings.slot_duration,
        "break_duration": settings.break_duration,
        "day_start_hour": settings.day_start_hour,
        "day_start_minute": settings.day_start_minute,
        "day_end_hour": settings.day_end_hour,
        "day_end_minute": settings.day_end_minute
    }

@router.put("/settings")
def update_settings(
    slot_duration: int = Form(45),
    break_duration: int = Form(15),
    day_start_hour: int = Form(8),
    day_start_minute: int = Form(0),
    day_end_hour: int = Form(16),
    day_end_minute: int = Form(0),
    user: models.User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Update timetable settings (admin only)"""
    settings = db.query(models.TimetableSettings).filter(
        models.TimetableSettings.class_id == user.class_id
    ).first()
    
    if not settings:
        settings = models.TimetableSettings(class_id=user.class_id)
        db.add(settings)
    
    settings.slot_duration = slot_duration
    settings.break_duration = break_duration
    settings.day_start_hour = day_start_hour
    settings.day_start_minute = day_start_minute
    settings.day_end_hour = day_end_hour
    settings.day_end_minute = day_end_minute
    
    db.commit()
    return {"status": "success"}

# === Slot Endpoints ===

@router.get("/slots")
def get_all_slots(
    user: models.User = Depends(require_user),
    db: Session = Depends(get_db)
):
    """Get all timetable slots for the class"""
    slots = db.query(models.TimetableSlot).filter(
        models.TimetableSlot.class_id == user.class_id
    ).order_by(models.TimetableSlot.weekday, models.TimetableSlot.slot_number).all()
    
    settings = db.query(models.TimetableSettings).filter(
        models.TimetableSettings.class_id == user.class_id
    ).first()
    
    result = []
    for slot in slots:
        start_time, end_time = ("", "")
        if settings:
            start_time, end_time = calculate_slot_time(settings, slot.slot_number)
        
        result.append({
            "id": slot.id,
            "weekday": slot.weekday,
            "weekday_name": WEEKDAY_NAMES[slot.weekday] if slot.weekday < 5 else "?",
            "slot_number": slot.slot_number,
            "subject_id": slot.subject_id,
            "subject_name": slot.subject_name,
            "group_name": slot.group_name,
            "room": slot.room,
            "start_time": start_time,
            "end_time": end_time
        })
    
    return {"slots": result}

@router.post("/slots")
def create_slot(
    weekday: int = Form(...),
    slot_number: int = Form(...),
    subject_name: str = Form(...),
    subject_id: Optional[str] = Form(None),
    group_name: Optional[str] = Form(None),
    room: Optional[str] = Form(None),
    user: models.User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Create a new timetable slot (admin only)"""
    if weekday < 0 or weekday > 4:
        raise HTTPException(status_code=400, detail="Weekday must be 0-4")
    if slot_number < 1 or slot_number > 12:
        raise HTTPException(status_code=400, detail="Slot number must be 1-12")
    
    slot = models.TimetableSlot(
        class_id=user.class_id,
        weekday=weekday,
        slot_number=slot_number,
        subject_id=subject_id if subject_id else None,
        subject_name=subject_name,
        group_name=group_name if group_name else None,
        room=room if room else None
    )
    db.add(slot)
    db.commit()
    db.refresh(slot)
    
    return {"status": "created", "id": slot.id}

@router.post("/slots/bulk")
def create_slots_bulk(
    weekday: int = Form(...),
    slot_numbers: list[int] = Form(...),
    subject_name: str = Form(...),
    subject_id: Optional[str] = Form(None),
    group_name: Optional[str] = Form(None),
    room: Optional[str] = Form(None),
    user: models.User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Create multiple timetable slots at once (admin only)."""
    if weekday < 0 or weekday > 4:
        raise HTTPException(status_code=400, detail="Weekday must be 0-4")

    created_ids: list[str] = []
    for slot_number in slot_numbers:
        if slot_number < 1 or slot_number > 12:
            raise HTTPException(status_code=400, detail="Slot number must be 1-12")

        slot = models.TimetableSlot(
            class_id=user.class_id,
            weekday=weekday,
            slot_number=slot_number,
            subject_id=subject_id if subject_id else None,
            subject_name=subject_name,
            group_name=group_name if group_name else None,
            room=room if room else None,
        )
        db.add(slot)
        db.flush()
        created_ids.append(slot.id)

    db.commit()
    return {"status": "created", "ids": created_ids, "count": len(created_ids)}


# === Public Share (Admin) ===

@router.get("/public/status")
def get_public_status(
    user: models.User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Get current public-share status for this class (admin only)."""
    clazz = db.query(models.Class).filter(models.Class.id == user.class_id).first()
    if not clazz:
        raise HTTPException(status_code=404, detail="Class not found")

    return {
        "enabled": bool(getattr(clazz, "timetable_public_enabled", False)),
        "code": getattr(clazz, "timetable_public_token", None),
    }


@router.post("/public/rotate")
def rotate_public_code(
    user: models.User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Enable + rotate public share code for timetable (admin only)."""
    clazz = db.query(models.Class).filter(models.Class.id == user.class_id).first()
    if not clazz:
        raise HTTPException(status_code=404, detail="Class not found")

    # Avoid collisions with other classes.
    code = security.generate_public_share_code()
    while db.query(models.Class).filter(models.Class.timetable_public_token == code).first():
        code = security.generate_public_share_code()

    clazz.timetable_public_enabled = True
    clazz.timetable_public_token = code
    db.commit()
    return {"enabled": True, "code": code}


@router.post("/public/disable")
def disable_public_code(
    user: models.User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Disable public share link (admin only)."""
    clazz = db.query(models.Class).filter(models.Class.id == user.class_id).first()
    if not clazz:
        raise HTTPException(status_code=404, detail="Class not found")

    clazz.timetable_public_enabled = False
    db.commit()
    return {"enabled": False}

@router.put("/slots/{slot_id}")
def update_slot(
    slot_id: str,
    subject_name: str = Form(...),
    subject_id: Optional[str] = Form(None),
    group_name: Optional[str] = Form(None),
    room: Optional[str] = Form(None),
    user: models.User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Update a timetable slot (admin only)"""
    slot = db.query(models.TimetableSlot).filter(
        models.TimetableSlot.id == slot_id,
        models.TimetableSlot.class_id == user.class_id
    ).first()
    
    if not slot:
        raise HTTPException(status_code=404, detail="Slot not found")
    
    slot.subject_name = subject_name
    slot.subject_id = subject_id if subject_id else None
    slot.group_name = group_name if group_name else None
    slot.room = room if room else None
    
    db.commit()
    return {"status": "updated"}

@router.delete("/slots/{slot_id}")
def delete_slot(
    slot_id: str,
    user: models.User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Delete a timetable slot (admin only)"""
    slot = db.query(models.TimetableSlot).filter(
        models.TimetableSlot.id == slot_id,
        models.TimetableSlot.class_id == user.class_id
    ).first()
    
    if not slot:
        raise HTTPException(status_code=404, detail="Slot not found")
    
    # Also delete user selections for this slot
    db.query(models.UserTimetableSelection).filter(
        models.UserTimetableSelection.slot_id == slot_id
    ).delete()
    
    db.delete(slot)
    db.commit()
    return {"status": "deleted"}

# === User Selection Endpoints ===

@router.get("/my")
def get_my_timetable(
    user: models.User = Depends(require_registered_user),
    db: Session = Depends(get_db)
):
    """Get personalized timetable for user"""
    # Get user's selected slots
    selections = db.query(models.UserTimetableSelection).filter(
        models.UserTimetableSelection.user_id == user.id
    ).all()
    
    selected_slot_ids = [s.slot_id for s in selections]
    
    # Get all slots for the class
    all_slots = db.query(models.TimetableSlot).filter(
        models.TimetableSlot.class_id == user.class_id
    ).order_by(models.TimetableSlot.weekday, models.TimetableSlot.slot_number).all()
    
    settings = db.query(models.TimetableSettings).filter(
        models.TimetableSettings.class_id == user.class_id
    ).first()
    
    # Build result with selection status
    result = []
    for slot in all_slots:
        start_time, end_time = ("", "")
        if settings:
            start_time, end_time = calculate_slot_time(settings, slot.slot_number)
        
        # Check if this slot is selected by user
        is_selected = slot.id in selected_slot_ids
        
        result.append({
            "id": slot.id,
            "weekday": slot.weekday,
            "weekday_name": WEEKDAY_NAMES[slot.weekday] if slot.weekday < 5 else "?",
            "slot_number": slot.slot_number,
            "subject_name": slot.subject_name,
            "group_name": slot.group_name,
            "room": slot.room,
            "start_time": start_time,
            "end_time": end_time,
            "selected": is_selected
        })
    
    return {"slots": result, "selected_count": len(selected_slot_ids)}

@router.post("/select/{slot_id}")
def select_slot(
    slot_id: str,
    user: models.User = Depends(require_registered_user),
    db: Session = Depends(get_db)
):
    """Select a slot for personalized timetable"""
    # Verify slot exists and belongs to user's class
    slot = db.query(models.TimetableSlot).filter(
        models.TimetableSlot.id == slot_id,
        models.TimetableSlot.class_id == user.class_id
    ).first()
    
    if not slot:
        raise HTTPException(status_code=404, detail="Slot not found")
    
    # Check if already selected
    existing = db.query(models.UserTimetableSelection).filter(
        models.UserTimetableSelection.user_id == user.id,
        models.UserTimetableSelection.slot_id == slot_id
    ).first()
    
    if existing:
        return {"status": "already_selected"}
    
    selection = models.UserTimetableSelection(user_id=user.id, slot_id=slot_id)
    db.add(selection)
    db.commit()
    
    return {"status": "selected"}

@router.delete("/select/{slot_id}")
def deselect_slot(
    slot_id: str,
    user: models.User = Depends(require_registered_user),
    db: Session = Depends(get_db)
):
    """Deselect a slot from personalized timetable"""
    selection = db.query(models.UserTimetableSelection).filter(
        models.UserTimetableSelection.user_id == user.id,
        models.UserTimetableSelection.slot_id == slot_id
    ).first()
    
    if selection:
        db.delete(selection)
        db.commit()
    
    return {"status": "deselected"}

# === Next Lesson Widget ===

@router.get("/next")
def get_next_lesson(
    user: models.User = Depends(require_registered_user),
    db: Session = Depends(get_db)
):
    """Get the next upcoming lesson for widget"""
    now = datetime.now()
    current_weekday = now.weekday()  # 0=Monday
    current_time = now.hour * 60 + now.minute
    
    # Get settings
    settings = db.query(models.TimetableSettings).filter(
        models.TimetableSettings.class_id == user.class_id
    ).first()
    
    if not settings:
        return {"next_lesson": None}
    
    # Get user's selected slots
    selections = db.query(models.UserTimetableSelection).filter(
        models.UserTimetableSelection.user_id == user.id
    ).all()
    
    selected_slot_ids = [s.slot_id for s in selections]
    
    if not selected_slot_ids:
        return {"next_lesson": None, "message": "Keine Kurse ausgewählt"}
    
    # Find next lesson
    for day_offset in range(7):  # Check up to a week ahead
        check_day = (current_weekday + day_offset) % 7
        
        # Skip weekends
        if check_day > 4:
            continue
        
        # Get slots for this day
        day_slots = db.query(models.TimetableSlot).filter(
            models.TimetableSlot.class_id == user.class_id,
            models.TimetableSlot.weekday == check_day,
            models.TimetableSlot.id.in_(selected_slot_ids)
        ).order_by(models.TimetableSlot.slot_number).all()
        
        for slot in day_slots:
            start_time_str, end_time_str = calculate_slot_time(settings, slot.slot_number)
            start_h, start_m = map(int, start_time_str.split(":"))
            slot_start_minutes = start_h * 60 + start_m
            
            # For today, check if slot is in the future
            if day_offset == 0 and slot_start_minutes <= current_time:
                continue
            
            # Found next lesson
            return {
                "next_lesson": {
                    "subject_name": slot.subject_name,
                    "group_name": slot.group_name,
                    "room": slot.room,
                    "weekday": WEEKDAY_NAMES[check_day],
                    "start_time": start_time_str,
                    "end_time": end_time_str,
                    "is_today": day_offset == 0,
                    "day_offset": day_offset
                }
            }
    
    return {"next_lesson": None}
