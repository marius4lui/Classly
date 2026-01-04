# 🏠 Classly selbst hosten – Anfänger-Guide

Diese Anleitung erklärt Schritt für Schritt, wie du Classly auf deinem eigenen Server betreibst.

---

## 📋 Voraussetzungen

Du brauchst:
- Einen **Server** (VPS, Raspberry Pi, oder alter PC)
- **Docker** installiert
- Ca. **5 Minuten** Zeit

### Docker installieren

**Ubuntu/Debian:**
```bash
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
# Neu einloggen, dann testen:
docker --version
```

**Windows/Mac:**
Lade [Docker Desktop](https://www.docker.com/products/docker-desktop/) herunter.

---

## 🚀 Installation

### 1. Projekt herunterladen

```bash
git clone https://github.com/your-user/classly.git
cd classly
```

Oder manuell: Lade die ZIP von GitHub herunter und entpacke sie.

### 2. Starten

```bash
docker compose up -d
```

Das war's! ✅

### 3. Testen

Öffne im Browser: `http://SERVER-IP:8000`

---

## 🌐 Mit Domain & HTTPS (empfohlen)

### Traefik Reverse Proxy (empfohlen)

Erstelle eine `docker-compose.override.yml`:

```yaml
services:
  classly:
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.classly.rule=Host(`classly.deine-domain.de`)"
      - "traefik.http.routers.classly.entrypoints=websecure"
      - "traefik.http.routers.classly.tls.certresolver=letsencrypt"
```

### Nginx Reverse Proxy

```nginx
server {
    listen 80;
    server_name classly.deine-domain.de;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## 💾 Backup & Daten

### Wo sind meine Daten?

```bash
# Docker Volume anzeigen
docker volume inspect classly_classly_data
```

Die SQLite-Datenbank liegt im Docker Volume unter `/data/classly.db`.

### Backup erstellen

```bash
# DB aus Container kopieren
docker cp classly:/data/classly.db ./backup.db
```

### Backup wiederherstellen

```bash
# DB in Container kopieren
docker cp ./backup.db classly:/data/classly.db

# Container neu starten
docker compose restart
```

---

## 🔄 Updates

```bash
# Neue Version holen
git pull

# Neu bauen & starten
docker compose down
docker compose up -d --build
```

---

## 🔧 Konfiguration

### Umgebungsvariablen

In `docker-compose.yml` kannst du anpassen:

```yaml
environment:
  - DATABASE_URL=sqlite:////data/classly.db  # DB Pfad
```

### Anderen Port verwenden

```yaml
ports:
  - "3000:8000"  # Jetzt auf Port 3000 erreichbar
```

---

## ❓ Häufige Probleme

### Container startet nicht

```bash
# Logs anzeigen
docker compose logs -f
```

### Port bereits belegt

```bash
# Anderen Port wählen in docker-compose.yml
ports:
  - "8080:8000"
```

### Daten weg nach Update

Stelle sicher, dass du ein Volume verwendest (ist im Standard-Setup bereits so):
```yaml
volumes:
  - classly_data:/data
```

---

## 🆘 Hilfe

1. Logs prüfen: `docker compose logs -f`
2. Container Status: `docker compose ps`
3. Neustart: `docker compose restart`

---

Viel Spaß mit Classly! 🎉
