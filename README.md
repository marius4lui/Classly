# 📚 Classly

**Der einfachste Weg, Klassenarbeiten und Termine mit deiner Klasse zu teilen.**

![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.12-blue?style=for-the-badge&logo=python&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker&logoColor=white)

---

## ✨ Features

- 📅 **Kalender** – Übersicht aller Termine auf einen Blick
- 📝 **Event-Typen** – KA, Test, Hausaufgaben, Info
- 🎯 **Themen-Blöcke** – Bei KA/Tests: z.B. "Vokabeln S. 20-30 (50 Wörter)"
- 👥 **Klassen-System** – Erstelle eine Klasse, teile den Link
- 🔗 **Login-Links** – Personalisierte Links für jeden Schüler
- 📱 **Mobile-First** – Perfekt auf dem Handy nutzbar
- 🔒 **Owner-Login** – Optional mit E-Mail/Passwort sichern
- 📊 **Audit-Logs** – Wer hat was geändert? (90 Tage)

---

## 🚀 Schnellstart mit Docker

```bash
# 1. Repo klonen
git clone https://github.com/marius4lui/classly.git
cd classly

# 2. Starten
docker compose up -d

# 3. Öffnen
open http://localhost:8000
```

**Das war's!** 🎉

---

## 📖 Dokumentation

➡️ Siehe [docs/SELFHOST.md](docs/SELFHOST.md) für die vollständige Anleitung

---

## 🛠️ Entwicklung

```bash
# Virtual Environment erstellen
python -m venv venv
./venv/Scripts/activate  # Windows
source venv/bin/activate  # Linux/Mac

# Dependencies installieren
pip install -r requirements.txt

# Server starten
uvicorn app.main:app --reload --port 8000
```

---

## 📁 Projektstruktur

```
classly/
├── app/
│   ├── main.py          # FastAPI App
│   ├── models.py        # SQLAlchemy Models
│   ├── crud.py          # Datenbankoperationen
│   ├── database.py      # DB Connection
│   ├── routers/         # API Endpoints
│   │   ├── auth.py      # Login/Register
│   │   ├── pages.py     # HTML Pages
│   │   ├── events.py    # Events CRUD
│   │   ├── admin.py     # Admin Functions
│   │   └── caldav.py    # CalDAV Support
│   ├── templates/       # Jinja2 HTML
│   └── static/          # CSS/JS
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

---

## 📜 Lizenz

MIT License – Mach damit was du willst! 🎁
