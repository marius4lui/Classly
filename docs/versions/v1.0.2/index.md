# Classly v1.0.2 – Changelog

**Release date:** 2026-03-02

## Summary

Offizielles Docker-Image `marius4lui/classly` auf Docker Hub veröffentlicht. Die Installationsdokumentation wurde vollständig überarbeitet: Neue Nutzer brauchen kein Git-Repository mehr zu klonen, sondern starten Classly direkt per `docker run` gegen das fertige Image.

## Änderungen

### Docker & Hosting

- **Offizielles Image:** `marius4lui/classly:latest` auf Docker Hub veröffentlicht.
- **`docker-compose.yml`:** `image: classly` hinzugefügt, sodass das Image bei lokalem Build immer den Namen `classly` (statt `verzeichnisname-classly`) erhält.

### Dokumentation

- **`docs/setup/installation.md` (neu geschrieben):**
  - Primäre Methode ist jetzt `docker run` direkt gegen `marius4lui/classly:latest`
  - Schritt-für-Schritt: Ordner + `.env` anlegen, Container starten, testen
  - Update-Workflow via `docker pull` + `docker stop/rm/run` dokumentiert
  - Alternative Docker Compose-Variante (ohne Klonen) dokumentiert
  - Backup-/Restore-Anleitung für lokales `./data`-Volume ergänzt
- **`docs/setup/installation-legacy.md` (umbenannt):**
  - Alte Anleitung (git clone + docker compose build) bleibt als Legacy-Seite bestehen
  - Für Entwickler und fortgeschrittene Nutzer weiterhin verlinkt
- **`docs/setup/configuration.md`:** Hinweis `cp .env.example .env` vor der Variablen-Tabelle ergänzt
- **`docs/development/contributing.md`:** `cp .env.example .env`-Schritt in den lokalen Dev-Setup-Abschnitt eingefügt
- **`README.md`:** Schnellstart-Codeblock auf `docker run`-Oneliner umgestellt
- **`docs/.vitepress/config.mts`:** Sidebar-Eintrag „Installation (Legacy)" hinzugefügt
- **`docs/versions/v1.0.2/index.md`:** Neue Versionsseite in den Docs angelegt
