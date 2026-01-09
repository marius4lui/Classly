# 📚 Classly Dokumentation

Willkommen in der offiziellen Dokumentation von **Classly** – dem einfachsten Weg, Klassenarbeiten und Termine mit deiner Klasse zu organisiere.

Classly wurde entwickelt, um Schülern und Lehrern (oder Klassensprechern) eine einfache, mobile-first Plattform zu bieten, um den Überblick über alle anstehenden Termine zu behalten.

---

## 🚀 Was kann Classly?

Classly ist mehr als nur ein Kalender. Es ist auf die Bedürfnisse von Schulklassen zugeschnitten:

- **📅 Klassen-Kalender:** Alle Termine zentral für die ganze Klasse.
- **📝 Spezielle Event-Typen:** Unterscheide sofort zwischen `Klassenarbeit`, `Test`, `Hausaufgabe` oder `Info`.
- **🎯 Themen-Blöcke:** Füge detaillierte Themen zu Arbeiten hinzu (z.B. "Vokabeln Unit 1" oder "Seite 50-55").
- **👥 Rollen-System:** Rechteverwaltung für `Owner`, `Admin`, `Class Admin` und `Member`.
- **🔗 Einfaches Teilen:** Einladungs-Links und Login-Tokens machen das Beitreten kinderleicht – kein Passwort-Chaos.
- **📱 Mobile First:** Funktioniert perfekt auf deinem Smartphone als Web-App.
- **🔒 Datenschutz:** Du hostest es selbst – deine Daten gehören dir.

---

## 📖 Inhaltsverzeichnis

### 🛠️ Einrichtung & Hosting
Wie du Classly auf deinem eigenen Server installierst.

- [Installation & Setup](setup/installation.md) – Docker, Manuell, Updates.
- [Konfiguration](setup/configuration.md) – Umgebungsvariablen, Ports, Reverse Proxy (Traefik/Nginx).

### 👤 Benutzerhandbuch
Wie du Classly als Nutzer oder Admin verwendest.

- [Erste Schritte](user-guide/getting-started.md) – Klasse erstellen, Leute einladen.
- [Funktionen & Rollen](user-guide/features.md) – Was bedeuten die Rollen? Was sind Audit-Logs?

### 💻 Entwicklung
Für Entwickler, die Classly verbessern wollen.

- [Mitmachen](development/contributing.md) – Tech-Stack, lokale Entwicklung, API.

---

## 🆘 Hilfe & Support

Wenn du Probleme hast:
1. Prüfe die [Konfigurations-Seite](setup/configuration.md).
2. Schau in die Logs (`docker compose logs -f`).
3. Erstelle ein Issue auf GitHub.
