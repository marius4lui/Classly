"""
Classly API v1 - Timetable Endpoints
=====================================
Endpoints für Stundenplan-Informationen.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from app.repository.factory import get_repository
from app.repository.base import BaseRepository
from app import models
from .deps import require_timetable_read

router = APIRouter(prefix="/timetable", tags=["Timetable"])


@router.get("")
def get_timetable(
    auth = Depends(require_timetable_read),
    repo: BaseRepository = Depends(get_repository),
    weekday: int = Query(None, ge=0, le=4, description="Filter by weekday (0=Mo, 4=Fr)")
):
    """
    Gibt den Stundenplan der Klasse zurück.
    
    **Erforderlicher Scope:** `timetable:read`
    
    Query-Parameter:
    - `weekday`: Optional, filtert nach Wochentag (0=Montag, 4=Freitag)
    """
    class_id = auth["class_id"]
    
    # Direkte DB-Abfrage für TimetableSlots
    query = repo.db.query(models.TimetableSlot).filter(
        models.TimetableSlot.class_id == class_id
    )
    
    if weekday is not None:
        query = query.filter(models.TimetableSlot.weekday == weekday)
    
    slots = query.order_by(
        models.TimetableSlot.weekday,
        models.TimetableSlot.slot_number
    ).all()
    
    # Nach Tag gruppieren
    days = {}
    weekday_names = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag"]
    
    for slot in slots:
        day_key = weekday_names[slot.weekday] if slot.weekday < len(weekday_names) else f"Tag {slot.weekday}"
        if day_key not in days:
            days[day_key] = []
        
        days[day_key].append({
            "id": slot.id,
            "slot_number": slot.slot_number,
            "subject_id": slot.subject_id,
            "subject_name": slot.subject_name,
            "group_name": slot.group_name,
            "room": slot.room
        })
    
    # Slots innerhalb jedes Tages sortieren
    for day in days:
        days[day].sort(key=lambda x: x["slot_number"])
    
    return {
        "class_id": class_id,
        "total_slots": len(slots),
        "timetable": days
    }


@router.get("/settings")
def get_timetable_settings(
    auth = Depends(require_timetable_read),
    repo: BaseRepository = Depends(get_repository)
):
    """
    Gibt die Stundenplan-Einstellungen der Klasse zurück.
    
    **Erforderlicher Scope:** `timetable:read`
    """
    class_id = auth["class_id"]
    
    # Direkte DB-Abfrage für TimetableSettings
    settings = repo.db.query(models.TimetableSettings).filter(
        models.TimetableSettings.class_id == class_id
    ).first()
    
    if not settings:
        # Default-Werte
        return {
            "class_id": class_id,
            "slot_duration": 45,
            "break_duration": 15,
            "day_start": "08:00",
            "day_end": "16:00"
        }
    
    return {
        "class_id": class_id,
        "slot_duration": settings.slot_duration,
        "break_duration": settings.break_duration,
        "day_start": f"{settings.day_start_hour:02d}:{settings.day_start_minute:02d}",
        "day_end": f"{settings.day_end_hour:02d}:{settings.day_end_minute:02d}"
    }
