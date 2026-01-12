# 📚 Classly

**Der einfachste Weg, Klassenarbeiten und Termine mit deiner Klasse zu teilen.**

![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.12-blue?style=for-the-badge&logo=python&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker&logoColor=white)

---

## 👋 Was ist Classly?

Classly ist eine **Web-App für Schulklassen**. Statt zehn verschiedener WhatsApp-Gruppen und Fotos von der Tafel, hast du **einen Link**, unter dem alle Termine (Klassenarbeiten, Tests, Hausaufgaben) übersichtlich zu finden sind.

👉 **[Hier geht's zur kompletten Dokumentation!](docs/index.md)**

### ✨ Features

- 📅 **Zentraler Kalender:** Ein Blick, alles im Griff.
- 📱 **Keine App-Installation:** Läuft im Browser auf jedem Handy.
- 🔗 **Einfacher Zugang:** Login via "Magic Links" – keine Passwörter merken für Schüler.
- 🔒 **Rollen-System:** Owner, Admins, Class-Admins und Mitglieder.
- ☁️ **CalDAV Sync:** Termine direkt im privaten Handy-Kalender abonnieren.
- 🛡️ **Self-Hosted:** Deine Daten, dein Server.
- 🗄️ **Multi-Database:** Unterstützt SQLite, PostgreSQL und MySQL/MariaDB.

---

## 🚀 Schnellstart (Docker)

Du willst es sofort ausprobieren?

```bash
git clone https://github.com/marius4lui/classly.git
cd classly
docker compose up -d
```

Öffne dann `http://localhost:8000` im Browser.

➡️ **[Ausführliche Installations-Anleitung](docs/setup/installation.md)**

### Erweiterte Konfiguration

#### Datenbank
Classly unterstützt SQLite (Standard), PostgreSQL und MySQL.
Setze die Environment-Variable `DATABASE_URL`:

- **PostgreSQL**: `postgresql://user:pass@host:5432/dbname`
- **MySQL/MariaDB**: `mysql+pymysql://user:pass@host:3306/dbname`
- **SQLite**: `sqlite:///./classly.db` (Default)

Connection Pooling kann über `DATABASE_POOL_SIZE` (default: 10) und `DATABASE_POOL_MAX_LIFETIME` (default: 3600) konfiguriert werden.

#### Redis Session Cache
Für bessere Skalierung können Sessions im Redis gecached werden.
Setze dazu:
- `SESSION_STORE=redis`
- `REDIS_URL=redis://localhost:6379`

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
