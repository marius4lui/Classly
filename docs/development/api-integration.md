# 🤖 AI-Integration & Scripts

Classly bietet spezielle Tools für die Integration mit KI-Agenten und Automatisierung.

## Downloads

| Datei | Beschreibung | Download |
|-------|--------------|----------|
| **classly_client.py** | Python Client & CLI | [Download](https://github.com/marius4lui/Classly/releases/latest/download/classly_client.py) |
| **SKILL.md** | AI Agent Skill | [Download](https://github.com/marius4lui/Classly/releases/latest/download/SKILL.md) |

---

## 🐍 Python Client

Das `classly_client.py` Script bietet einen vollständigen API-Client für Python.

### Installation

```bash
# Script herunterladen
curl -O https://github.com/marius4lui/Classly/releases/latest/download/classly_client.py

# Abhängigkeiten installieren
pip install requests python-dotenv
```

### Konfiguration

Erstelle eine `.env` Datei oder setze die Umgebungsvariable:

```bash
# Option 1: .env Datei
echo "CLASSLY_API_KEY=cl_live_xxx..." > .env

# Option 2: Umgebungsvariable
export CLASSLY_API_KEY="cl_live_xxx..."
```

### CLI-Verwendung

```bash
# Events auflisten
python classly_client.py events list

# Event erstellen
python classly_client.py events create --type HA --date 2026-02-15 --title "Aufgabe"

# Mit Fach
python classly_client.py events create --type TEST --date 2026-02-20 --subject Mathe --title "Kapitel 5"

# Event löschen
python classly_client.py events delete --id <event-id>

# Klassen-Info
python classly_client.py class info

# Benutzer auflisten
python classly_client.py users list

# Fächer auflisten
python classly_client.py subjects list

# Stundenplan
python classly_client.py timetable show
```

### Als Python-Modul

```python
from classly_client import ClasslyClient

# Client initialisieren (lädt API-Key aus CLASSLY_API_KEY)
client = ClasslyClient()

# Oder mit explizitem API-Key
client = ClasslyClient(api_key="cl_live_xxx...")

# Events abrufen
events = client.get_events()
for event in events:
    print(f"{event['date']}: {event['title']}")

# Event erstellen
new_event = client.create_event(
    type="HA",
    date="2026-02-15",
    subject="Deutsch",
    title="Aufsatz schreiben"
)
print(f"Erstellt: {new_event['id']}")

# Event löschen
client.delete_event(event_id="abc-123")

# Klassen-Info
info = client.get_class_info()
print(f"Klasse: {info['name']}")

# Benutzer
users = client.get_users()
print(f"{len(users)} Mitglieder")

# Fächer
subjects = client.get_subjects()
for subj in subjects:
    print(f"- {subj['name']}")

# Stundenplan
timetable = client.get_timetable()
for day, slots in timetable['timetable'].items():
    print(f"{day}: {len(slots)} Stunden")
```

---

## 🤖 AI Agent Skill

Das `SKILL.md` ist für KI-Agenten wie Claude, GPT, oder andere LLM-basierte Systeme optimiert.

### Was ist ein AI Skill?

Ein Skill ist eine strukturierte Anleitung, die KI-Agenten hilft, die Classly API zu verstehen und korrekt zu nutzen. Es enthält:

- Alle verfügbaren Endpoints
- Request/Response-Formate
- Authentifizierungsdetails
- Beispiel-Requests

### Verwendung mit AI-Agenten

1. **Download**: Lade `SKILL.md` herunter
2. **Einbinden**: Füge es deinem AI-Agent als Kontext hinzu
3. **API-Key**: Stelle sicher, dass `CLASSLY_API_KEY` verfügbar ist

#### Beispiel: Claude mit MCP

```json
{
  "skills": [
    {
      "name": "classly",
      "path": "./skills/SKILL.md"
    }
  ]
}
```

#### Beispiel: Custom Agent

```python
# Skill als Kontext laden
with open("SKILL.md", "r") as f:
    classly_skill = f.read()

# An LLM übergeben
prompt = f"""
Du hast Zugriff auf die Classly API. Hier ist die Dokumentation:

{classly_skill}

Aufgabe: Erstelle eine Hausaufgabe für morgen in Mathe.
"""
```

---

## Skill-Inhalt

Das `SKILL.md` enthält folgende Informationen für KI-Agenten:

### Endpoints

| Ressource | Endpoints |
|-----------|-----------|
| Events | `GET/POST /api/v1/events`, `PUT/DELETE /api/v1/events/{id}` |
| Klassen | `GET /api/v1/classes` |
| Benutzer | `GET /api/v1/users`, `GET /api/v1/users/me` |
| Fächer | `GET /api/v1/subjects` |
| Stundenplan | `GET /api/v1/timetable` |

### Event-Typen

| Typ | Beschreibung |
|-----|--------------|
| `KA` | Klassenarbeit |
| `TEST` | Test |
| `HA` | Hausaufgabe |
| `INFO` | Information |

### Authentifizierung

```bash
Authorization: Bearer $CLASSLY_API_KEY
```

---

## Umgebungsvariablen

| Variable | Beschreibung | Standard |
|----------|--------------|----------|
| `CLASSLY_API_KEY` | API-Key für Authentifizierung | *erforderlich* |
| `CLASSLY_BASE_URL` | Server-URL | `https://classly.site` |

---

## Beispiel: Automatisierung

### Tägliche Hausaufgaben-Erinnerung

```python
#!/usr/bin/env python3
"""Sendet tägliche Hausaufgaben-Übersicht per E-Mail."""

from classly_client import ClasslyClient
from datetime import datetime, timedelta

client = ClasslyClient()

# Events für morgen abrufen
tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
events = client.get_events()

# Nur Hausaufgaben für morgen
homework = [
    e for e in events 
    if e["type"] == "HA" and e["date"].startswith(tomorrow)
]

if homework:
    print(f"📚 {len(homework)} Hausaufgaben für morgen:")
    for hw in homework:
        print(f"  - {hw['subject']}: {hw['title']}")
else:
    print("✅ Keine Hausaufgaben für morgen!")
```

### Moodle-Sync

```python
#!/usr/bin/env python3
"""Synchronisiert Moodle-Aufgaben mit Classly."""

from classly_client import ClasslyClient
import moodle_api  # Hypothetische Moodle-API

client = ClasslyClient()

# Moodle-Aufgaben abrufen
moodle_tasks = moodle_api.get_assignments()

for task in moodle_tasks:
    # In Classly erstellen
    client.create_event(
        type="HA",
        date=task["due_date"],
        subject=task["course_name"],
        title=task["name"]
    )
    print(f"✅ Erstellt: {task['name']}")
```

---

## API-Key erstellen

1. Öffne [/api-keys](https://classly.site/api-keys) in deiner Classly-Instanz
2. Klicke **"Neuer Key"**
3. Wähle Namen und Berechtigungen:
   - `events:read` - Events lesen
   - `events:write` - Events erstellen/bearbeiten/löschen
   - `classes:read` - Klassen-Info
   - `users:read` - Benutzer-Liste
   - `subjects:read` - Fächer
   - `timetable:read` - Stundenplan
4. **Kopiere den Token sofort** - er wird nur einmal angezeigt!

---

## Support

- 📖 [API v1 Dokumentation](/development/api-v1)
- 🐛 [GitHub Issues](https://github.com/marius4lui/Classly/issues)
- 📊 [Status-Seite](https://info.classly.site/status/classly-info)
