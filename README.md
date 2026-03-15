# 📚 Classly

**Der einfachste Weg, Klassenarbeiten und Termine mit deiner Klasse zu teilen.**

![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.12-blue?style=for-the-badge&logo=python&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker&logoColor=white)

---

## 👋 Was ist Classly?

Classly ist eine **Web-App für Schulklassen**. Statt zehn verschiedener WhatsApp-Gruppen und Fotos von der Tafel, hast du **einen Link**, unter dem alle Termine (Klassenarbeiten, Tests, Hausaufgaben) übersichtlich zu finden sind.

👉 **[Hier geht's zur kompletten Dokumentation!](https://docs.classly.site)**

### ✨ Features

- 📅 **Zentraler Kalender:** Ein Blick, alles im Griff.
- 📱 **Keine App-Installation:** Läuft im Browser auf jedem Handy.
- 🔗 **Einfacher Zugang:** Login via "Magic Links" – keine Passwörter merken für Schüler.
- 🔒 **Rollen-System:** Owner, Admins, Class-Admins und Mitglieder.
- ☁️ **CalDAV Sync:** Termine direkt im privaten Handy-Kalender abonnieren.
- 🛡️ **Self-Hosted:** Deine Daten, dein Server.

---

## 🚀 Schnellstart (Docker)

Du willst es sofort ausprobieren?

```bash
mkdir -p classly/data && cd classly
touch .env
docker run -d --name classly -p 8000:8000 -v $(pwd)/data:/data --env-file .env marius4lui/classly:latest
```

Öffne dann `http://localhost:8000` im Browser.

➡️ **[Ausführliche Installations-Anleitung](docs/setup/installation.md)**

---

## 📖 Dokumentation

Wir haben eine ausführliche Dokumentation für dich erstellt:

- **[Installation & Setup](docs/setup/installation.md)** (Docker, Config, Updates)
- **[Benutzer-Handbuch](docs/user-guide/getting-started.md)** (Erste Schritte, Funktionen)
- **[Entwicklung](docs/development/contributing.md)** (Lokal entwickeln, Tech Stack)

---

## 📜 Lizenz

Classly verwendet ein **Dual-Licensing-Modell**:

### Community License (kostenlos)

Für nicht-kommerzielle Nutzung – siehe [LICENSE](LICENSE).

| Nutzung | Erlaubt? |
|---------|----------|
| Private Nutzung | ✅ Ja |
| Self-Hosting (privat) | ✅ Ja |
| Bildungseinrichtungen (Schulen, Unis) | ❌ Nein |
| Non-Profit Organisationen | ✅ Ja |
| Modifikation & Beiträge | ✅ Ja |
| Code studieren & lernen | ✅ Ja |
| Kommerzielle Nutzung | ❌ Nein |
| For-Profit Unternehmen | ❌ Nein |
| SaaS / Hosting für Dritte | ❌ Nein |
| Weiterverkauf | ❌ Nein |
| White-Labeling | ❌ Nein |

### Commercial License

Für Unternehmen und kommerzielle Nutzung – siehe [COMMERCIAL.md](COMMERCIAL.md).

> **Hinweis:** Versionen vor diesem Lizenzwechsel (Commit `d29a12d` und früher)
> unterlagen der MIT-Lizenz. Die neue Dual-Licensing-Regelung gilt nur für
> Versionen nach dem Lizenzwechsel.
