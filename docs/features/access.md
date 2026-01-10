# 🔑 Zugang & Datenschutz

Classly verfolgt einen modernen Ansatz beim Thema Login: **Weg mit den Passwörtern!**

## Das Link-System

Statt dass sich jeder Schüler Benutzername und Passwort merken muss (was sie eh vergessen), funktioniert Classly über **Links**.

### 1. Der Klassen-Link (Join Link)
*   Diesen Link (z.B. `classly.site/join/ABCDE`) teilst du einmalig in der WhatsApp-Gruppe der Klasse.
*   Jeder, der drauf klickt, kann der Klasse beitreten.
*   **Smart Login:** Wenn jemand seinen Namen eingibt (z.B. "Laura"), prüft Classly, ob es "Laura" schon gibt.
    *   Falls ja: Automatische Anmeldung in ihren Account.
    *   Falls nein: Neuer Account wird erstellt.

### 2. Der Persönliche Login-Link
Wenn du den "offenen Beitritt" deaktivierst (für mehr Sicherheit), kannst du für einzelne Schüler **Login-Links** erstellen.
*   Gehe als Admin auf **Erweitert** -> **Links**.
*   Wähle einen Nutzer aus oder erstelle einen neuen Namen.
*   Du bekommst einen geheimen Link (`.../join/SECRET_TOKEN`).
*   Diesen Link schickst du dem Schüler privat (DM).
*   Damit ist er **sofort eingeloggt**, ohne Passwort.

---

## 🛡️ Datenschutz

Classly wurde mit deutschen Datenschutz-Standards im Hinterkopf entwickelt.

*   **Keine E-Mail-Pflicht:** Schüler müssen keine E-Mail-Adresse angeben. Ein Spitzname reicht.
*   **Datensparsamkeit:** Wir speichern nur das Nötigste (Name, Rolle, erstelle Einträge).
*   **Serverstandort:** Wenn du Classly selbst hostest, liegen die Daten auf **deinem** Server. Du hast die volle Kontrolle.

## Sicherheitstipps

1.  **Join deaktivieren:** Sobald alle Schüler in der Klasse sind, deaktiviere im Admin-Menü den Schalter "Beitritt erlauben". Dann kommt niemand Fremdes mehr rein.
2.  **Backups:** Mache regelmäßig Backups der Datenbank (als Admin unter "Erweitert").
