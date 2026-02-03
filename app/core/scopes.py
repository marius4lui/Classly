"""
Classly API Scopes
==================
Zentralisierte Scope-Definitionen und Validierung für die REST API.

Format: <resource>:<action>
Beispiel: events:read, events:write, classes:read
"""

from enum import Enum
from typing import Set


class APIScope(str, Enum):
    """Alle verfügbaren API-Scopes."""
    
    # Klassen
    CLASSES_READ = "classes:read"
    CLASSES_WRITE = "classes:write"
    
    # Benutzer
    USERS_READ = "users:read"
    USERS_WRITE = "users:write"
    
    # Events
    EVENTS_READ = "events:read"
    EVENTS_WRITE = "events:write"
    
    # Legacy-Scope (Rückwärtskompatibilität)
    READ_EVENTS = "read:events"
    
    # Stundenplan
    TIMETABLE_READ = "timetable:read"
    TIMETABLE_WRITE = "timetable:write"
    
    # Fächer
    SUBJECTS_READ = "subjects:read"
    SUBJECTS_WRITE = "subjects:write"
    
    # Webhooks
    WEBHOOKS_MANAGE = "webhooks:manage"


# Scope-Hierarchie: Write-Scopes implizieren Read-Scopes
SCOPE_HIERARCHY: dict[APIScope, Set[APIScope]] = {
    APIScope.CLASSES_WRITE: {APIScope.CLASSES_READ},
    APIScope.USERS_WRITE: {APIScope.USERS_READ},
    APIScope.EVENTS_WRITE: {APIScope.EVENTS_READ, APIScope.READ_EVENTS},
    APIScope.TIMETABLE_WRITE: {APIScope.TIMETABLE_READ},
    APIScope.SUBJECTS_WRITE: {APIScope.SUBJECTS_READ},
}

# Legacy-Mappings für Rückwärtskompatibilität
LEGACY_SCOPE_MAPPINGS: dict[str, APIScope] = {
    "read:events": APIScope.EVENTS_READ,
}


def parse_scopes(scope_string: str) -> Set[APIScope]:
    """
    Parse Comma-separated Scope-String in ein Set von APIScopes.
    
    Args:
        scope_string: Komma-getrennte Scopes, z.B. "events:read,classes:read"
    
    Returns:
        Set von APIScope Enums
    """
    if not scope_string:
        return set()
    
    scopes = set()
    for s in scope_string.split(","):
        s = s.strip()
        if not s:
            continue
        
        # Legacy-Scope mapping
        if s in LEGACY_SCOPE_MAPPINGS:
            scopes.add(LEGACY_SCOPE_MAPPINGS[s])
            continue
        
        # Versuche als APIScope zu parsen
        try:
            scopes.add(APIScope(s))
        except ValueError:
            # Unbekannter Scope - ignorieren (Logging könnte hier sinnvoll sein)
            pass
    
    return scopes


def has_scope(granted: Set[APIScope], required: APIScope) -> bool:
    """
    Prüft ob ein Scope gewährt wurde (inkl. Hierarchie).
    
    Args:
        granted: Set von gewährten Scopes
        required: Der benötigte Scope
    
    Returns:
        True wenn der Scope vorhanden ist (direkt oder impliziert)
    """
    # Direkter Match
    if required in granted:
        return True
    
    # Legacy-Kompatibilität: read:events == events:read
    if required == APIScope.EVENTS_READ and APIScope.READ_EVENTS in granted:
        return True
    if required == APIScope.READ_EVENTS and APIScope.EVENTS_READ in granted:
        return True
    
    # Hierarchie prüfen (Write impliziert Read)
    for scope, implied in SCOPE_HIERARCHY.items():
        if scope in granted and required in implied:
            return True
    
    return False


def scopes_to_string(scopes: Set[APIScope]) -> str:
    """Konvertiert ein Set von Scopes zurück in einen Comma-separated String."""
    return ",".join(s.value for s in sorted(scopes, key=lambda x: x.value))


# Vordefinierte Scope-Sets für häufige Use-Cases
READONLY_SCOPES = {
    APIScope.CLASSES_READ,
    APIScope.EVENTS_READ, 
    APIScope.SUBJECTS_READ,
    APIScope.TIMETABLE_READ,
    APIScope.USERS_READ,
}

FULL_ACCESS_SCOPES = {
    APIScope.CLASSES_READ,
    APIScope.CLASSES_WRITE,
    APIScope.EVENTS_READ,
    APIScope.EVENTS_WRITE,
    APIScope.SUBJECTS_READ,
    APIScope.SUBJECTS_WRITE,
    APIScope.TIMETABLE_READ,
    APIScope.TIMETABLE_WRITE,
    APIScope.USERS_READ,
    APIScope.USERS_WRITE,
    APIScope.WEBHOOKS_MANAGE,
}
