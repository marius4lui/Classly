# Classly v1.0.2

Release date: 2026-03-02

## Highlights

- Offizielles Docker-Image `marius4lui/classly` veröffentlicht.
- Neue Haupt-Installationsanleitung auf Basis von `docker run` – kein Repository-Clone mehr nötig.
- Env-Konfiguration (`cp .env.example .env`) in allen relevanten Docs und README ergänzt.
- Alte Installationsanleitung (Klonen + Build) als Legacy-Seite erhalten.

## Changelog

### Setup & Hosting

- Offizielles Docker Hub Image: `marius4lui/classly:latest`
- Neue primäre Installationsanleitung `docs/setup/installation.md`:
  - Dokumentiert explizit das Erstellen des Daten-Ordners (`mkdir -p classly/data`)
  - Dokumentiert das Erstellen der `.env`-Datei (`touch .env`)
  - Hauptbefehl ist jetzt `docker run` direkt gegen das veröffentlichte Image
  - Beinhaltet separaten Abschnitt für Updates via `docker pull` + `docker run`
  - Alternative Docker Compose-Variante ohne Klonen dokumentiert
- Alte `installation.md` (Klonen + `docker compose build`) umbenannt zu `docs/setup/installation-legacy.md` und bleibt für Entwickler erhalten
- `docker-compose.yml`: `image: classly` addiert, damit der Image-Name "classly" heißt statt dem Standard "verzeichnisname-servicename"

### Documentation

- `README.md` Schnellstart auf `docker run`-Oneliner umgestellt
- `docs/setup/configuration.md`: Hinweis auf `cp .env.example .env` bei den Umgebungsvariablen ergänzt
- `docs/development/contributing.md`: `cp .env.example .env`-Schritt in lokalen Dev-Setup ergänzt
- `.vitepress/config.mts` Sidebar: Neuer Eintrag „Installation (Legacy)" hinzugefügt

## Migration

Bestehende Nutzer, die via `git clone` + `docker compose` arbeiten, können wie bisher fortzufahren. Für neue Installationen empfehlen wir den `docker run`-Weg ohne Git-Clone.
