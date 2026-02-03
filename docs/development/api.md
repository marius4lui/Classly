# 🔌 API Übersicht

Classly bietet mehrere APIs für unterschiedliche Anwendungsfälle. Wähle die passende API für dein Projekt.

## Verfügbare APIs

| API | Verwendung | Authentifizierung | Status |
|-----|------------|-------------------|--------|
| [**API v1**](/development/api-v1) | Externe Integrationen, Automatisierung | API-Keys | ✅ Empfohlen |
| [**Legacy API**](/development/api-legacy) | Bestehende Integrationen, Mobile Apps | OAuth 2.0 / Token | ⚠️ Legacy |
| [**OAuth 2.0**](/development/api-oauth) | Mobile Apps, Drittanbieter-Login | Authorization Code Flow | ✅ Aktiv |
| [**AI-Integration**](/development/api-integration) | KI-Agenten, Python Scripts | API-Keys | ✅ Neu |

---

## Schnellstart

### 1. API-Key erstellen

1. Öffne [/api-keys](https://classly.site/api-keys) in deiner Classly-Instanz
2. Klicke auf **"Neuer Key"**
3. Wähle einen Namen und die benötigten Berechtigungen
4. **Kopiere den Token sofort** - er wird nur einmal angezeigt!

### 2. Erste Anfrage

```bash
curl -X GET "https://classly.site/api/v1/events" \
  -H "Authorization: Bearer cl_live_xxxx..."
```

### 3. Response

```json
{
  "class_id": "abc-123",
  "count": 5,
  "events": [
    {
      "id": "event-123",
      "type": "HA",
      "title": "Mathe S. 42",
      "date": "2026-02-15T00:00:00Z"
    }
  ]
}
```

---

## API-Auswahl

### Wann API v1 verwenden?

- ✅ Neue Integrationen
- ✅ Server-zu-Server Kommunikation
- ✅ Automatisierung (z.B. Moodle, Schulserver)
- ✅ Wenn du granulare Berechtigungen brauchst

→ [API v1 Dokumentation](/development/api-v1)

### Wann Legacy API / OAuth verwenden?

- ✅ Mobile Apps mit User-Login
- ✅ Bestehende Integrationen
- ✅ Wenn der Benutzer sich selbst authentifizieren soll

→ [Legacy API Dokumentation](/development/api-legacy)  
→ [OAuth 2.0 Dokumentation](/development/api-oauth)

---

## Fehlerbehandlung

Alle APIs verwenden einheitliche Fehler-Responses:

```json
{
  "detail": "Fehlerbeschreibung"
}
```

| HTTP Code | Bedeutung |
|-----------|-----------|
| 400 | Ungültige Anfrage |
| 401 | Nicht authentifiziert |
| 403 | Keine Berechtigung |
| 404 | Nicht gefunden |
| 429 | Rate Limit überschritten |
| 500 | Serverfehler |

---

## Support

- 📖 [GitHub Issues](https://github.com/marius4lui/Classly/issues)
- 📊 [Status-Seite](https://info.classly.site/status/classly-info)
