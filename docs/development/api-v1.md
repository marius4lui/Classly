# 🔑 API v1 Dokumentation

Die API v1 ist die empfohlene Schnittstelle für externe Integrationen und Automatisierung.

::: tip 💡 Empfohlen für neue Projekte
API v1 bietet granulare Berechtigungen, bessere Sicherheit und ist zukunftssicher.
:::

---

## Authentifizierung

API v1 verwendet API-Keys mit Bearer Token Authentifizierung:

```bash
curl -X GET "https://classly.site/api/v1/events" \
  -H "Authorization: Bearer cl_live_xxxxxxxxxxxxxxxx"
```

### API-Key erstellen

1. Gehe zu **Einstellungen → API-Keys** (oder `/api-keys`)
2. Klicke auf **"Neuer Key"**
3. Wähle einen Namen und die gewünschten Berechtigungen
4. **Kopiere den Token sofort** - er wird nur einmal angezeigt!

::: warning Wichtig
Der vollständige Token wird nur **einmal** bei der Erstellung angezeigt.  
Speichere ihn sicher - er kann nicht wiederhergestellt werden!
:::

---

## Verfügbare Scopes

| Scope | Beschreibung |
|-------|--------------|
| `events:read` | Events lesen |
| `events:write` | Events erstellen, bearbeiten, löschen |
| `classes:read` | Klassen-Informationen lesen |
| `users:read` | Benutzer-Liste lesen |
| `subjects:read` | Fächer lesen |
| `timetable:read` | Stundenplan lesen |

---

## Endpoints

### API Info

#### GET `/api/v1`

Gibt Informationen über die API zurück.

```bash
curl https://classly.site/api/v1
```

**Response:**
```json
{
  "version": "v1",
  "auth": {
    "type": "Bearer Token",
    "docs": "https://docs.classly.site/development/api"
  },
  "endpoints": {
    "classes": "/api/v1/classes",
    "users": "/api/v1/users",
    "events": "/api/v1/events",
    "subjects": "/api/v1/subjects",
    "timetable": "/api/v1/timetable"
  }
}
```

---

### Klassen

#### GET `/api/v1/classes`

Gibt Informationen über die Klasse des API-Keys zurück.

**Scope:** `classes:read`

**Response:**
```json
{
  "id": "class-uuid-123",
  "name": "10b",
  "created_at": "2026-01-01T00:00:00Z",
  "member_count": 25
}
```

---

### Events

#### GET `/api/v1/events`

Listet alle Events der Klasse auf.

**Scope:** `events:read`

**Query Parameter:**
| Parameter | Typ | Beschreibung |
|-----------|-----|--------------|
| `updated_since` | ISO DateTime | Nur Events nach diesem Zeitpunkt |
| `limit` | int | Max. Anzahl (Standard: 200, Max: 500) |

**Beispiel:**
```bash
curl "https://classly.site/api/v1/events?limit=10" \
  -H "Authorization: Bearer cl_live_xxx"
```

**Response:**
```json
{
  "class_id": "class-uuid-123",
  "count": 2,
  "events": [
    {
      "id": "event-uuid-1",
      "type": "HA",
      "date": "2026-02-10T00:00:00Z",
      "subject": "Mathe",
      "title": "S. 42 Nr. 1-5",
      "author_id": "user-uuid-456",
      "created_at": "2026-02-01T10:00:00Z",
      "updated_at": "2026-02-01T10:00:00Z"
    }
  ]
}
```

---

#### POST `/api/v1/events`

Erstellt ein neues Event.

**Scope:** `events:write`

**Request Body:**
```json
{
  "type": "HA",
  "date": "2026-02-15T00:00:00Z",
  "subject": "Deutsch",
  "title": "Aufsatz schreiben"
}
```

| Feld | Typ | Erforderlich | Beschreibung |
|------|-----|--------------|--------------|
| `type` | string | ✅ | `KA`, `TEST`, `HA`, oder `INFO` |
| `date` | ISO DateTime | ✅ | Datum des Events |
| `subject` | string | ❌ | Fächername |
| `title` | string | ✅ | Titel/Beschreibung |

**Response:**
```json
{
  "id": "new-event-uuid",
  "created": true,
  "event": { ... }
}
```

---

#### PUT `/api/v1/events/{event_id}`

Bearbeitet ein bestehendes Event.

**Scope:** `events:write`

**Request Body:** (nur die zu ändernden Felder)
```json
{
  "title": "Neuer Titel"
}
```

---

#### DELETE `/api/v1/events/{event_id}`

Löscht ein Event.

**Scope:** `events:write`

**Response:**
```json
{
  "deleted": true
}
```

---

### Benutzer

#### GET `/api/v1/users`

Listet alle Mitglieder der Klasse auf.

**Scope:** `users:read`

**Response:**
```json
{
  "class_id": "class-uuid-123",
  "count": 25,
  "users": [
    {
      "id": "user-uuid-1",
      "name": "Max Mustermann",
      "role": "member"
    },
    {
      "id": "user-uuid-2",
      "name": "Admin User",
      "role": "admin"
    }
  ]
}
```

#### GET `/api/v1/users/me`

Gibt Informationen über den Benutzer des API-Keys zurück.

**Scope:** `users:read`

---

### Fächer

#### GET `/api/v1/subjects`

Listet alle Fächer der Klasse auf.

**Scope:** `subjects:read`

**Response:**
```json
{
  "class_id": "class-uuid-123",
  "count": 12,
  "subjects": [
    {
      "id": "subject-uuid-1",
      "name": "Mathematik",
      "short_name": "Ma"
    },
    {
      "id": "subject-uuid-2",
      "name": "Deutsch",
      "short_name": "De"
    }
  ]
}
```

---

### Stundenplan

#### GET `/api/v1/timetable`

Gibt den Stundenplan der Klasse zurück.

**Scope:** `timetable:read`

**Query Parameter:**
| Parameter | Typ | Beschreibung |
|-----------|-----|--------------|
| `weekday` | int | Filter nach Wochentag (0=Mo, 4=Fr) |

**Response:**
```json
{
  "class_id": "class-uuid-123",
  "total_slots": 35,
  "timetable": {
    "Montag": [
      {
        "id": "slot-1",
        "slot_number": 1,
        "subject_name": "Mathematik",
        "room": "R201"
      },
      {
        "id": "slot-2",
        "slot_number": 2,
        "subject_name": "Deutsch",
        "room": "R105"
      }
    ],
    "Dienstag": [ ... ]
  }
}
```

#### GET `/api/v1/timetable/settings`

Gibt die Stundenplan-Einstellungen zurück.

**Scope:** `timetable:read`

**Response:**
```json
{
  "class_id": "class-uuid-123",
  "slot_duration": 45,
  "break_duration": 15,
  "day_start": "08:00",
  "day_end": "16:00"
}
```

---

## Event-Typen

| Typ | Beschreibung | Farbe |
|-----|--------------|-------|
| `KA` | Klassenarbeit | 🔴 Rot |
| `TEST` | Test | 🟠 Orange |
| `HA` | Hausaufgabe | 🟢 Grün |
| `INFO` | Information | 🔵 Blau |

---

## Rate Limiting

API-Keys haben ein Rate Limit von **60 Requests pro Minute** (konfigurierbar).

Bei Überschreitung:
- HTTP Status: `429 Too Many Requests`
- Warte und versuche es erneut

---

## Code-Beispiele

### Python

```python
import requests

API_KEY = "cl_live_xxxx..."
BASE_URL = "https://classly.site/api/v1"

headers = {
    "Authorization": f"Bearer {API_KEY}"
}

# Events abrufen
response = requests.get(f"{BASE_URL}/events", headers=headers)
events = response.json()

# Neues Event erstellen
new_event = {
    "type": "HA",
    "date": "2026-02-20T00:00:00",
    "subject": "Mathe",
    "title": "Übungen S. 50"
}
response = requests.post(f"{BASE_URL}/events", headers=headers, json=new_event)
```

### JavaScript

```javascript
const API_KEY = 'cl_live_xxxx...';
const BASE_URL = 'https://classly.site/api/v1';

// Events abrufen
const response = await fetch(`${BASE_URL}/events`, {
    headers: {
        'Authorization': `Bearer ${API_KEY}`
    }
});
const data = await response.json();

// Neues Event erstellen
await fetch(`${BASE_URL}/events`, {
    method: 'POST',
    headers: {
        'Authorization': `Bearer ${API_KEY}`,
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        type: 'HA',
        date: '2026-02-20T00:00:00',
        subject: 'Mathe',
        title: 'Übungen S. 50'
    })
});
```

### PowerShell

```powershell
$headers = @{
    "Authorization" = "Bearer cl_live_xxxx..."
    "Content-Type" = "application/json"
}

# Events abrufen
Invoke-RestMethod -Uri "https://classly.site/api/v1/events" -Headers $headers

# Neues Event erstellen
$body = @{
    type = "HA"
    date = "2026-02-20T00:00:00"
    subject = "Mathe"
    title = "Übungen S. 50"
} | ConvertTo-Json

Invoke-RestMethod -Uri "https://classly.site/api/v1/events" -Method POST -Headers $headers -Body $body
```
