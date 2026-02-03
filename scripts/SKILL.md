---
name: classly
description: Interagiere mit der Classly Schulklassen-Plattform API um Events, Benutzer, Fächer und Stundenplan zu verwalten.
---

# Classly AI Skill

Du kannst mit der Classly API interagieren, um Schulklassen-Daten zu verwalten.

## Authentifizierung

Der API-Key wird aus der Umgebungsvariable `CLASSLY_API_KEY` geladen. Alle Requests benötigen den Header:

```
Authorization: Bearer <CLASSLY_API_KEY>
```

## Basis-URL

```
https://classly.site/api/v1
```

## Verfügbare Endpoints

### Events

| Endpoint | Methode | Beschreibung |
|----------|---------|--------------|
| `/api/v1/events` | GET | Alle Events abrufen |
| `/api/v1/events` | POST | Neues Event erstellen |
| `/api/v1/events/{id}` | PUT | Event bearbeiten |
| `/api/v1/events/{id}` | DELETE | Event löschen |

**Event-Typen:**
- `KA` = Klassenarbeit
- `TEST` = Test  
- `HA` = Hausaufgabe
- `INFO` = Information

**Event erstellen:**
```json
POST /api/v1/events
{
  "type": "HA",
  "date": "2026-02-15T00:00:00",
  "subject": "Mathe",
  "title": "S. 42 Nr. 1-5"
}
```

### Klassen

| Endpoint | Methode | Beschreibung |
|----------|---------|--------------|
| `/api/v1/classes` | GET | Klassen-Informationen |

### Benutzer

| Endpoint | Methode | Beschreibung |
|----------|---------|--------------|
| `/api/v1/users` | GET | Alle Klassenmitglieder |
| `/api/v1/users/me` | GET | Aktueller Benutzer |

### Fächer

| Endpoint | Methode | Beschreibung |
|----------|---------|--------------|
| `/api/v1/subjects` | GET | Alle Fächer |

### Stundenplan

| Endpoint | Methode | Beschreibung |
|----------|---------|--------------|
| `/api/v1/timetable` | GET | Stundenplan abrufen |
| `/api/v1/timetable/settings` | GET | Stundenplan-Einstellungen |

## Request-Beispiele

### Events abrufen

```bash
curl -X GET "https://classly.site/api/v1/events" \
  -H "Authorization: Bearer $CLASSLY_API_KEY"
```

Response:
```json
{
  "class_id": "abc-123",
  "count": 5,
  "events": [
    {
      "id": "event-1",
      "type": "HA",
      "date": "2026-02-15T00:00:00Z",
      "subject": "Mathe",
      "title": "S. 42"
    }
  ]
}
```

### Event erstellen

```bash
curl -X POST "https://classly.site/api/v1/events" \
  -H "Authorization: Bearer $CLASSLY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"type": "HA", "date": "2026-02-15T00:00:00", "subject": "Deutsch", "title": "Aufsatz"}'
```

### Event löschen

```bash
curl -X DELETE "https://classly.site/api/v1/events/{event_id}" \
  -H "Authorization: Bearer $CLASSLY_API_KEY"
```

## Fehlerbehandlung

| HTTP Code | Bedeutung |
|-----------|-----------|
| 200 | Erfolgreich |
| 400 | Ungültige Anfrage |
| 401 | Nicht authentifiziert (API-Key ungültig) |
| 403 | Keine Berechtigung (fehlender Scope) |
| 404 | Nicht gefunden |
| 429 | Rate Limit überschritten |

Fehler-Response:
```json
{
  "detail": "Fehlerbeschreibung"
}
```

## Python Client

Für komplexere Integrationen kann das `classly_client.py` Script verwendet werden:

```python
from classly_client import ClasslyClient

client = ClasslyClient()  # Lädt API-Key aus CLASSLY_API_KEY

# Events abrufen
events = client.get_events()

# Event erstellen
client.create_event(
    type="HA",
    date="2026-02-15",
    subject="Mathe",
    title="Übungen S. 50"
)

# Klassen-Info
info = client.get_class_info()

# Benutzer
users = client.get_users()

# Fächer
subjects = client.get_subjects()

# Stundenplan
timetable = client.get_timetable()
```

## Wichtige Hinweise

1. **API-Key Scopes**: Je nach API-Key können unterschiedliche Berechtigungen verfügbar sein
2. **Rate Limit**: 60 Requests pro Minute
3. **Datumsformat**: ISO 8601 (YYYY-MM-DDTHH:MM:SS)
4. **Alle Zeiten**: UTC
