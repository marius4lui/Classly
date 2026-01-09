# ⚙️ Konfiguration

Hier erfährst du, wie du Classly an deine Bedürfnisse anpasst. Die meiste Konfiguration geschieht über die `docker-compose.yml` oder Umgebungsvariablen.

---

## 🔧 Grundeinstellungen (`docker-compose.yml`)

Die Datei `docker-compose.yml` steuert, wie Classly ausgeführt wird.

### Port ändern

Standardmäßig läuft Classly auf Port **8000**.
Um dies zu ändern (z.B. auf Port 3000), ändere den `ports`-Abschnitt:

```yaml
services:
  classly:
    # ...
    ports:
      - "3000:8000"  # Format: "DEIN-PORT:INTERNER-PORT"
```

### Umgebungsvariablen

Classly nutzt folgende Umgebungsvariablen zur Konfiguration:

| Variable | Standardwert | Beschreibung |
| :--- | :--- | :--- |
| `DATABASE_URL` | `sqlite:////data/classly.db` | Pfad zur Datenbank (SQLAlchemy Format). |

> [!NOTE]
> Aktuell ist Classly primär für **SQLite** optimiert. PostgreSQL support ist experimentell.

---

## 🌐 Reverse Proxy (HTTPS & Domains)

Damit Classly sicher über das Internet erreichbar ist (z.B. unter `deine-klasse.de`), solltest du einen Reverse Proxy davor schalten.

### Option A: Traefik (Empfohlen)

Wenn du bereits Traefik in deinem Docker-Setup nutzt, füge einfach Labels hinzu. Erstelle dazu am besten eine `docker-compose.override.yml`:

```yaml
services:
  classly:
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.classly.rule=Host(`classly.deine-domain.de`)"
      - "traefik.http.routers.classly.entrypoints=websecure"
      - "traefik.http.routers.classly.tls.certresolver=letsencrypt"
networks:
  default:
    external: true
    name: dein-traefik-netzwerk  # Anpassen!
```

### Option B: Nginx

Füge folgenden Block zu deiner Nginx-Konfiguration hinzu:

```nginx
server {
    listen 80;
    server_name classly.deine-domain.de;
    
    # Weiterleitung zu HTTPS (optional aber empfohlen)
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl;
    server_name classly.deine-domain.de;

    # SSL Zertifikate hier einbinden...

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

## 📦 Datenbank & Schema

Classly prüft beim Start automatisch, ob die Datenbank-Struktur aktuell ist (`fix_db_schema.py`). Das bedeutet, du musst dich meistens nicht um Migrationen kümmern – einfach Updates installieren und neu starten.

### SQLite Volume

Stelle sicher, dass du das Volume nicht verlierst:

```yaml
volumes:
  - classly_data:/data
```

Dieses Volume (`classly_data`) enthält deine Datenbank. Solange dieses Volume existiert, bleiben deine Daten erhalten.
