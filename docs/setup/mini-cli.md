# Setup Mini CLI

Die Setup Mini CLI ist ein interaktiver Wizard Für Docker-Hosting von Classly.
Sie hilft dir, `.env` und `docker-compose` sicher zu konfigurieren mit:

- Quick-Modus (wenige Fragen)
- Advanced-Modus (vollstaendige Konfiguration)
- Diff-Preview vor dem Schreiben
- automatischen Backups
- Restore aus Backup

## Voraussetzungen

- Python 3.9+
- Projekt-Checkout mit `scripts/classly_setup_cli.py`
- Abhaengigkeiten aus `requirements.txt`

## Start

```bash
python scripts/classly_setup_cli.py wizard
```

Oder ueber den Wrapper:

```bash
bash scripts/setup.sh
```

## Modi

### Quick

Nur die wichtigsten Fragen mit sicheren Defaults:

```bash
python scripts/classly_setup_cli.py quick
```

### Advanced

Voller Wizard inkl. Appwrite-Optionen:

```bash
python scripts/classly_setup_cli.py advanced
```

## Wichtige Befehle

### Nur Vorschau (keine Datei-Aenderung)

```bash
python scripts/classly_setup_cli.py preview
```

### Aktuelle Konfiguration validieren

```bash
python scripts/classly_setup_cli.py validate
```

### Mit expliziten Dateien arbeiten

```bash
python scripts/classly_setup_cli.py quick --env-file .env --compose-file docker-compose.yml
```

### Coolify-Flow

```bash
python scripts/classly_setup_cli.py advanced --target coolify --compose-file docker-compose.coolify.yml
```

## Sicherheitsverhalten

Standardmaessig macht die CLI:

1. Diff-Preview anzeigen
2. Bestaetigung abfragen
3. Backup in `.backups/<timestamp>/` erstellen
4. Dateien schreiben

Mit `--yes` wird nur die Bestaetigung uebersprungen:

```bash
python scripts/classly_setup_cli.py quick --yes
```

## Backup wiederherstellen

```bash
python scripts/classly_setup_cli.py restore --backup .backups/20260213-120000
```

Das stellt alle Dateien wieder her, die in `meta.json` des Backups gelistet sind.

## Was wird angepasst

- `.env` Werte Für Laufzeit-Konfiguration
- `services.classly` im Compose-File:
  - `environment`
  - `env_file`
  - `ports` (normal) oder `expose` (coolify)

Unbekannte Compose-Keys bleiben erhalten.

## Troubleshooting

### Fehlende Python-Module

```bash
pip install -r requirements.txt
```

### Compose-Struktur nicht erkannt

Die CLI erwartet `services.classly` im ausgewaehlten Compose-File.
Wenn deine Datei stark abweicht, einmal manuell anpassen und danach erneut laufen lassen.

