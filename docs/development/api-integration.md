# 🤖 AI-Integration & Scripts

Classly bietet eine schlanke Integration für KI-Agenten und Automatisierung, die eine bestehende Classly-Instanz per API bedienen sollen.

## ⚡ Quick Install für Agenten

```text
Set up Classly API access for this workspace.

1. Download these files into a local `Tools/Classly` folder:
   - `https://github.com/marius4lui/Classly/releases/latest/download/classly_client.py`
   - `https://github.com/marius4lui/Classly/releases/latest/download/SKILL.md`
2. Read `SKILL.md` and use it as the Classly API reference.
3. Create a local `.env.example` with:
   - `CLASSLY_API_KEY=`
   - `CLASSLY_BASE_URL=https://classly.site`
4. Ask me for my Classly API token before making authenticated requests.
5. After I provide the token, store it in a local `.env` file as `CLASSLY_API_KEY=...`.
6. Use `classly_client.py` for listing classes, events, users, subjects, and timetable data.
7. Prefer minimal setup only for using the API, not for deploying or self-hosting Classly.
```

---

## Downloads

| Datei | Beschreibung | Download |
|-------|--------------|----------|
| **classly_client.py** | Python Client & CLI | [Download](https://github.com/marius4lui/Classly/releases/latest/download/classly_client.py) |
| **SKILL.md** | AI Agent Skill | [Download](https://github.com/marius4lui/Classly/releases/latest/download/SKILL.md) |

---

## Minimal Setup

Lege den API-Key lokal ab:

```bash
echo "CLASSLY_API_KEY=cl_live_xxx..." > .env
echo "CLASSLY_BASE_URL=https://classly.site" >> .env
```

Oder setze die Variablen direkt:

```bash
export CLASSLY_API_KEY="cl_live_xxx..."
export CLASSLY_BASE_URL="https://classly.site"
```

Benötigt:
- `CLASSLY_API_KEY` — erforderlich
- `CLASSLY_BASE_URL` — optional, Standard: `https://classly.site`

---

## Schnellstart

```bash
# Dateien herunterladen
curl -O https://github.com/marius4lui/Classly/releases/latest/download/classly_client.py
curl -O https://github.com/marius4lui/Classly/releases/latest/download/SKILL.md

# Abhängigkeiten
pip install requests python-dotenv

# Klassen-Info
python classly_client.py class info

# Events auflisten
python classly_client.py events list

# Fächer auflisten
python classly_client.py subjects list
```

---

## Was wofür?

- `classly_client.py` ist der schnelle Weg für Skripte und CLI-Nutzung.
- `SKILL.md` ist die kompakte Referenz für Agenten, die die Classly API korrekt nutzen sollen.

---

## API-Key erstellen

1. Öffne [/api-keys](https://classly.site/api-keys) in deiner Classly-Instanz
2. Klicke **"Neuer Key"**
3. Wähle die benötigten Berechtigungen
4. **Kopiere den Token sofort** — er wird nur einmal angezeigt

Typische Rechte:
- `events:read`
- `events:write`
- `classes:read`
- `users:read`
- `subjects:read`
- `timetable:read`

---

## Mehr Details

Für vollständige Endpoints, Request/Response-Formate und Details:

- 📖 [API v1 Dokumentation](/development/api-v1)
- 🐛 [GitHub Issues](https://github.com/marius4lui/Classly/issues)
- 📊 [Status-Seite](https://info.classly.site/status/classly-info)
