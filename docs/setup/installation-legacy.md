# 🛠️ Installation & Setup

Diese Anleitung führt dich durch die Installation von Classly. Wir empfehlen die Nutzung von **Docker**, da es die Einrichtung extrem vereinfacht und alle Abhängigkeiten mitbringt.

---

## 📋 Voraussetzungen

Bevor du startest, stelle sicher, dass du folgende Dinge bereit hast:

1.  **Einen Server oder PC:** Das kann ein VPS (z.B. Hetzner, DigitalOcean), ein Raspberry Pi oder dein lokaler Rechner sein.
2.  **Docker & Docker Compose:** Die Software, die Classly ausführt.

### Docker installieren

<details>
<summary>Klicke hier für Installations-Befehle (Linux)</summary>

```bash
# Docker holen & installieren
curl -fsSL https://get.docker.com | sh

# Deinen User zur Docker-Gruppe hinzufügen (wichtig!)
sudo usermod -aG docker $USER

# Einmal abmelden und wieder anmelden, damit die Rechte greifen.
```
</details>

<details>
<summary>Klicke hier für Windows/Mac</summary>

Lade einfach [Docker Desktop](https://www.docker.com/products/docker-desktop/) herunter und installiere es.
</details>

---

## 🚀 Installation via Docker (Empfohlen)

### 1. Repository klonen

Lade den Code von GitHub herunter:

```bash
git clone https://github.com/marius4lui/classly.git
cd classly
```

### 2. Konfiguration

Erstelle eine Konfigurationsdatei aus der Vorlage:

```bash
cp .env.example .env
```
*(Windows: `copy .env.example .env`)*

### 3. Starten

Starten den Server mit einem einzigen Befehl:

```bash
docker compose up -d
```

Der Parameter `-d` bedeutet "detached", also im Hintergrund.

### 4. Zugriff testen

Öffne deinen Browser und gehe auf:
`http://DEINE-IP:8000` (oder `http://localhost:8000` wenn lokal).

Du solltest nun die Classly Startseite sehen! 🎉

### 5. Setup Wizard (Recommended)

Wenn du Classly auf einem öffentlichen Server hostest und nicht willst, dass sich Fremde registrieren, kannst du:
1.  Ein Limit für Klassen setzen (siehe unten).
2.  Den interaktiven Setup-Wizard nutzen, um deine Klasse zu erstellen.

```bash
# Lade das Setup-Script und starte es
curl -sL https://scripts.classly.site/setup.sh | bash
```
Das Skript startet die interaktive Setup Mini CLI (quick/advanced), zeigt eine Vorschau und erstellt vor dem Schreiben Backups.
Hinweis: Auf dem Server muss Python installiert sein.

Mehr Details: [Setup Mini CLI](./mini-cli.md)

---

## ⚙️ Limitierung (Self-Hosting)

Du kannst in der `.env` Datei festlegen, wie viele Klassen auf deinem Server maximal erlaubt sind.

```bash
# .env
MAX_CLASSES=1 
```
Wenn dieses Limit erreicht ist (z.B. 1), können über die Webseite keine weiteren Klassen mehr erstellt werden. Perfekt, wenn du Classly nur für deine eigene Klasse hostest!

## 🔄 Updates installieren

Classly wird stetig verbessert. Um auf die neueste Version zu aktualisieren:

```bash
# 1. Neuesten Code holen
git pull

# 2. Container neu bauen und starten
docker compose up -d --build
```

---

## 💾 Backups & Datenverwaltung

Deine Daten sind wichtig! Classly speichert standardmäßig alles in einer SQLite-Datenbank (`classly.db`).

### Wo liegen meine Daten?

Docker speichert die Daten in einem **Volume** namens `classly_data`.
Innerhalb des Containers liegen die Daten unter `/data`.

### Backup erstellen (Wichtig!)

Um ein Backup deiner Datenbank zu machen:

```bash
# Kopiert die Datenbank aus dem laufenden Container in dein aktuelles Verzeichnis
docker cp classly:/data/classly.db ./backup_$(date +%F).db
```

Sichere diese Datei an einem sicheren Ort.

### Backup wiederherstellen

1.  Container stoppen: `docker compose down`
2.  Datenbank zurückspielen:
    ```bash
    # Kopiere dein Backup zurück in das Volume (Trick via temporärem Container oder direkt Starten und kopieren)
    # Einfacher Weg bei laufendem Container (Daten werden live überschrieben, Vorsicht!):
    
    docker compose up -d
    docker cp ./dein-backup.db classly:/data/classly.db
    docker compose restart
    ```

---

## ❓ Häufige Probleme

**Container startet nicht / "Permission denied"**
Stelle sicher, dass du in der `docker` Gruppe bist (`sudo usermod -aG docker $USER`) oder benutze `sudo` (nicht empfohlen).

**Port 8000 ist belegt**
Du kannst den Port in der `docker-compose.yml` ändern. Siehe dazu [Konfiguration](configuration.md).
