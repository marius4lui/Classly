"""
Classly API v1 - Router Package
===============================
Sammelt alle API v1 Sub-Router und exportiert den Haupt-Router.
"""

from fastapi import APIRouter
from . import classes, users, events, subjects, timetable

# Haupt-Router für API v1
router = APIRouter(prefix="/api/v1", tags=["API v1"])

# Sub-Router einbinden
router.include_router(classes.router)
router.include_router(users.router)
router.include_router(events.router)
router.include_router(subjects.router)
router.include_router(timetable.router)


# Info-Endpoint für API-Discovery
@router.get("", tags=["API v1"])
def api_info():
    """
    API v1 Info-Endpoint.
    
    Gibt verfügbare Endpoints und Authentifizierungs-Informationen zurück.
    """
    return {
        "version": "v1",
        "auth": {
            "type": "Bearer Token",
            "header": "Authorization: Bearer <api-key>",
            "docs": "https://docs.classly.site/development/api"
        },
        "endpoints": {
            "classes": "/api/v1/classes",
            "users": "/api/v1/users",
            "events": "/api/v1/events",
            "subjects": "/api/v1/subjects",
            "timetable": "/api/v1/timetable"
        },
        "scopes": {
            "classes:read": "Klassen-Informationen lesen",
            "users:read": "Benutzer-Informationen lesen",
            "events:read": "Events lesen",
            "events:write": "Events erstellen/bearbeiten/löschen",
            "subjects:read": "Fächer lesen",
            "timetable:read": "Stundenplan lesen"
        }
    }

