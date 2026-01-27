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
| `MIGRATE_FROM_DOMAIN` | - | Alte Domain für Umleitungen (z.B. `old.com`). Users werden automatisch migriert. |
| `MIGRATE_TO_DOMAIN` | - | Neue Domain Ziel (z.B. `new.com`). |
| `APPWRITE` | `false` | Setze auf `true` um Appwrite als Backend zu nutzen. |
| `APPWRITE_ENDPOINT` | `https://cloud.appwrite.io/v1` | URL zum Appwrite Server. |
| `APPWRITE_PROJECT_ID` | - | Appwrite Project ID. |
| `APPWRITE_API_KEY` | - | Appwrite API Key (Secret). |
| `APPWRITE_DATABASE_ID` | `classly_db` | Name der Appwrite Datenbank. |
| `AUTOMIGRATE_TO` | - | Setze auf `appwrite` um beim Start Daten von SQLite automatisch zu migrieren. |
| `CLASSLY_ADMIN_SECRET` | - | **Wichtig:** Setze ein sicheres Passwort, um das System-Dashboard unter `/system/login` zu aktivieren. Hier kannst du Backups und Migrationen steuern. |
| `CLASSLY_DB_PRIMARY` | `sqlite` | Primäre Datenbank für das System-Dashboard (`sqlite`, `appwrite`, `supabase`). |
| `CLASSLY_BACKUP_TARGET` | `local` | Standard-Ziel für Backups (`local`, `s3`, `supabase`, `appwrite`). |
| `S3_ENDPOINT` | - | S3 Endpoint URL für Backups. |
| `S3_ACCESS_KEY` | - | S3 Access Key. |
| `S3_SECRET_KEY` | - | S3 Secret Key. |
| `S3_BUCKET` | - | S3 Bucket Name. |
| `SUPABASE_URL` | - | PostgreSQL Connection String für Supabase Integrationen. |

> [!NOTE]
> Classly ist für **SQLite** optimiert, unterstützt aber auch **Appwrite** als Backend für skalierbare Setups. PostgreSQL support ist experimentell.

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
