# 📱 Legacy API Dokumentation

Die Legacy API (`/api/`) ist für bestehende Integrationen und Mobile Apps gedacht.

::: warning Hinweis
Für neue Projekte empfehlen wir die [API v1](/development/api-v1) mit API-Keys.
:::

---

## Authentifizierung

Die Legacy API unterstützt zwei Authentifizierungsmethoden:

### 1. Bearer Token

```bash
curl -X GET "https://classly.site/api/events" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 2. OAuth 2.0 Access Token

Siehe [OAuth 2.0 Dokumentation](/development/api-oauth) für den vollständigen Flow.

---

## Endpoints

### Benutzer-Info

#### GET `/api/me`

Gibt Informationen über den authentifizierten Benutzer und Token zurück.

**Response:**
```json
{
  "user": {
    "id": "user-uuid-123",
    "name": "Max Mustermann",
    "role": "member",
    "class_id": "class-uuid-456"
  },
  "token": {
    "id": "token-uuid",
    "scopes": "read:events",
    "expires_at": null
  },
  "class": {
    "id": "class-uuid-456",
    "name": "10b"
  }
}
```

---

### Events

#### GET `/api/events`

Listet alle Events der Klasse auf.

**Query Parameter:**
| Parameter | Typ | Beschreibung |
|-----------|-----|--------------|
| `updated_since` | ISO DateTime | Nur Events nach diesem Zeitpunkt |
| `limit` | int | Max. Anzahl (Standard: 200, Max: 500) |

**Beispiel:**
```bash
curl "https://classly.site/api/events?limit=50&updated_since=2026-02-01T00:00:00Z" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response:**
```json
{
  "events": [
    {
      "id": "event-uuid-1",
      "type": "HA",
      "date": "2026-02-10T00:00:00Z",
      "subject": "Mathe",
      "title": "S. 42 Nr. 1-5",
      "created_at": "2026-02-01T10:00:00Z"
    }
  ],
  "count": 1,
  "class_id": "class-uuid-456"
}
```

---

### Fächer

#### GET `/api/subjects`

Listet alle Fächer der Klasse auf.

**Response:**
```json
{
  "subjects": [
    {
      "id": "subject-uuid-1",
      "name": "Mathematik",
      "short_name": "Ma"
    }
  ],
  "count": 12
}
```

---

### Token erstellen

#### POST `/api/token`

Erstellt einen persönlichen API Token.

::: warning Veraltet
Für neue Integrationen verwende stattdessen [API-Keys](/development/api-v1).
:::

**Response:**
```json
{
  "token": "pat_xxxx...",
  "expires_at": null
}
```

---

## Push Notifications

Die Legacy API unterstützt Push Notifications für Mobile Apps.

### Registrierung

#### POST `/api/push/register`

Registriert einen Device Token für Push Notifications.

**Header:**
```
Authorization: Bearer YOUR_TOKEN
Content-Type: application/json
```

**Request Body:**
```json
{
  "device_token": "fcm_token_abc123...",
  "platform": "fcm"
}
```

| Parameter | Typ | Erforderlich | Beschreibung |
|-----------|-----|--------------|--------------|
| `device_token` | string | ✅ | FCM oder APNs Device Token |
| `platform` | string | ✅ | `fcm` (Android) oder `apns` (iOS) |

**Response:**
```json
{
  "status": "registered",
  "device_token": "fcm_token_abc123...",
  "platform": "fcm"
}
```

---

### Deregistrierung

#### DELETE `/api/push/unregister`

Entfernt einen Device Token (z.B. beim Logout).

**Request Body:**
```json
{
  "device_token": "fcm_token_abc123..."
}
```

**Response:**
```json
{
  "status": "unregistered"
}
```

---

### Token auflisten

#### GET `/api/push/tokens`

Listet alle registrierten Device Tokens des Benutzers auf.

**Response:**
```json
{
  "tokens": [
    {
      "device_token": "fcm_token_abc123...",
      "platform": "fcm",
      "created_at": "2026-01-14T20:00:00Z",
      "updated_at": "2026-01-14T20:00:00Z"
    }
  ]
}
```

---

## Migration zu API v1

Um von der Legacy API auf API v1 zu migrieren:

| Legacy API | API v1 | Änderungen |
|------------|--------|------------|
| `GET /api/events` | `GET /api/v1/events` | Neuer Response-Format |
| `GET /api/subjects` | `GET /api/v1/subjects` | Neuer Response-Format |
| `GET /api/me` | `GET /api/v1/users/me` | Anderer Endpoint |
| OAuth Token | API-Key | Andere Authentifizierung |

### Vorteile von API v1

- ✅ Granulare Scopes (z.B. nur Events lesen)
- ✅ Keine User-Session erforderlich
- ✅ Key-Rotation mit 24h Grace Period
- ✅ IP-Allowlisting möglich
- ✅ Bessere Rate Limiting Kontrolle

→ [Zur API v1 Dokumentation](/development/api-v1)
