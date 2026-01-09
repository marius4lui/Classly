# 💻 Entwicklung & Mitmachen

Du willst an Classly mitarbeiten? Super! Hier findest du alles, was du wissen musst.

---

## 🛠️ Tech Stack

Classly setzt auf bewährte, schlanke Technologien:

- **Backend:** [FastAPI](https://fastapi.tiangolo.com/) (Python hat die Power!)
- **Datenbank:** SQLite (via SQLAlchemy)
- **Frontend:** Server-Side Rendering mit [Jinja2](https://jinja.palletsprojects.com/) Templates.
- **Styling:** Vanilla CSS & Tailwind (via CDN oder eingebaut) – Fokus auf Performance.
- **Deployment:** Docker & Docker Compose.

---

## 🏃‍♂️ Lokal starten (ohne Docker)

Für die Entwicklung ist es oft einfacher, den Server direkt lokal laufen zu lassen.

### 1. Umgebung einrichten

```bash
# Repository klonen
git clone https://github.com/marius4lui/classly.git
cd classly

# Python Virtual Environment erstellen
python -m venv venv

# Aktivieren
# Windows:
.\venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Abhängigkeiten installieren
pip install -r requirements.txt
```

### 2. Server starten

```bash
uvicorn app.main:app --reload
```

Der Server läuft nun unter `http://localhost:8000`.
`--reload` sorgt dafür, dass der Server bei Code-Änderungen automatisch neu startet.

---

## 📂 Projektstruktur

```plaintext
classly/
├── app/
│   ├── main.py          # Einstiegspunkt
│   ├── models.py        # Datenbank-Modelle (SQLAlchemy)
│   ├── crud.py          # Datenbank-Operationen (Create, Read, Update, Delete)
│   ├── routers/         # API Endpoints (Auth, Events, Pages, ...)
│   ├── templates/       # HTML Dateien (Jinja2)
│   └── static/          # CSS, JS, Bilder
├── docs/                # Diese Dokumentation
├── docker-compose.yml   # Docker Config
└── requirements.txt     # Python Dependencies
```

---

## 🧪 API Dokumentation

FastAPI generiert automatisch eine interaktive API-Dokumentation.
Wenn der Server läuft, besuche einfach:

- **Swagger UI:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`

Hier kannst du alle API-Endpunkte direkt testen.
