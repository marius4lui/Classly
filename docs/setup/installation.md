# 🛠️ Installation & Setup

Diese Anleitung führt dich durch die Installation von Classly. Wir hosten ein fertiges Docker-Image für dich, sodass du nichts selbst herunterladen oder bauen musst.

---

## 📋 Voraussetzungen

Bevor du startest, stelle sicher, dass du folgende Dinge bereit hast:

1.  **Einen Server oder PC:** Das kann ein VPS (z.B. Hetzner, DigitalOcean), ein Raspberry Pi oder dein lokaler Rechner sein.
2.  **Docker:** Die Software, die Classly als Image ausführt.

<details>
<summary>Klicke hier für Docker-Installationsbefehle (Linux)</summary>

```bash
# Docker holen & installieren
curl -fsSL https://get.docker.com | sh

# Deinen User zur Docker-Gruppe hinzufügen (wichtig!)
sudo usermod -aG docker $USER

# Einmal abmelden und wieder anmelden, damit die Rechte greifen.
```
</details>

---

## 🚀 Installation via Docker Run (Empfohlen)

Mit ein paar Befehlen kannst du das offizielle Classly-Image starten, ohne das GitHub-Repository herunterladen zu müssen.

### 1. Ordner & Konfiguration erstellen

Erstelle einen neuen Ordner für deine Classly-Datenbank und die Konfiguration:

```bash
# 1. Neuen Ordner erstellen & betreten
mkdir -p classly/data
cd classly

# 2. Konfigurationsdatei (.env) erstellen
touch .env
```

*(Optional)* Du kannst einen Texteditor (z.B. `nano .env`) nutzen, um Limits und Konfigurationen festzulegen (siehe [Konfiguration](configuration.md)).

### 2. Classly starten

Lade das aktuelle Image von Docker Hub herunter und starte den Server mit folgendem Befehl:

```bash
docker run -d \
  --name classly \
  --restart unless-stopped \
  -p 8000:8000 \
  -v $(pwd)/data:/data \
  --env-file .env \
  marius4lui/classly:latest
```

*(Windows-Nutzer in der PowerShell: Ersetze `$(pwd)` durch `${PWD}` oder einen absoluten Pfad zur Data-Ordner.)*


### 3. Zugriff testen

Öffne deinen Browser und gehe auf:
`http://DEINE-IP:8000` (oder `http://localhost:8000` wenn lokal).

Du solltest nun die Classly Startseite sehen! 🎉

### 4. Setup Wizard (Optional)

Wenn du Classly auf einem öffentlichen Server hostest und nicht willst, dass sich Fremde registrieren, kannst du:
1.  Ein Limit für Klassen setzen in der `.env` (`MAX_CLASSES=1`).
2.  Den interaktiven Setup-Wizard im Container ausführen:

```bash
docker exec -it classly bash -c "curl -sL https://scripts.classly.site/setup.sh | bash"
```
Mehr Details dazu: [Setup Mini CLI](./mini-cli.md)

---

## 🔄 Updates installieren

Da du ein fertiges Image nutzt, ist ein Update super schnell erledigt:

```bash
# 1. Neues Image herunterladen
docker pull marius4lui/classly:latest

# 2. Alten Container stoppen & löschen (Deine Daten in ./data bleiben erhalten!)
docker stop classly
docker rm classly

# 3. Mit dem gleichen Befehl wie vorher wieder starten:
docker run -d \
  --name classly \
  --restart unless-stopped \
  -p 8000:8000 \
  -v $(pwd)/data:/data \
  --env-file .env \
  marius4lui/classly:latest
```

---

## 🐳 Installation via Docker Compose (Alternative)

Falls du `docker-compose.yml` bevorzugst (z.B. für komplexere Setups oder leichtere Updates), erstelle in deinem leeren `classly` Ordner eine Datei namens `docker-compose.yml`:

```yaml
services:
  classly:
    image: marius4lui/classly:latest
    container_name: classly
    ports:
      - "8000:8000"
    volumes:
      - ./data:/data
    env_file:
      - .env
    restart: unless-stopped
```

Führe anschließend einfach aus: `docker compose up -d`.

---

## 💾 Backups & Datenverwaltung

Deine Daten sind wichtig! Classly speichert standardmäßig alles in einer SQLite-Datenbank.

### Wo liegen meine Daten?

Da wir beim Starten ein Volume (`$(pwd)/data`) gemappt haben, liegt deine Datenbank nun sicher und offen zugänglich auf deinem lokalen Dateisystem:

Im Unterordner `classly/data/` direkt neben deiner `.env` findest du die Datei `classly.db` und Bilder.

### Backup erstellen (Wichtig!)

Um ein Backup der Datenbank zu machen, kopier einfach diese Datei an einen sicheren Ort:

```bash
# Kopiere die DB aus dem data-Ordner in ein Backup
cp data/classly.db ./backup_$(date +%F).db
```

### Backup wiederherstellen

1.  Container stoppen: `docker stop classly` (bzw. `docker compose down`)
2.  Backup-Datei nach `data/classly.db` zurück kopieren und die alte überschreiben.
3.  Container wieder starten: `docker start classly` (bzw. `docker compose up -d`)

---

## ❓ Häufige Probleme

**Container startet nicht / "Permission denied" auf /data**
Stelle sicher, dass du in der `docker` Gruppe bist (`sudo usermod -aG docker $USER`), oder dass der von dir erstellte `./data` Ordner für den Docker-Container beschreibbar ist.

**Port 8000 ist belegt**
Du kannst den Port beim `docker run` Befehl ändern: `-p 3000:8000` bindet Classly an Port 3000. Bei Docker Compose passt du analog den linken Portwert an. Siehe dazu [Konfiguration](configuration.md).

---

> _Tipp für Entwickler:_ Falls du stattdessen selbst das gesamte Repository klonen und den Container aus dem Quellcode kompilieren / lokal bauen möchtest, findest du die ursprüngliche Anleitung [im Legacy-Setup](./installation-legacy.md).
