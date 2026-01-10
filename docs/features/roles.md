# 👥 Rollen & Rechte

Classly nutzt ein einfaches aber mächtiges Rechtesystem, um deine Klasse sicher zu halten.

## Die Rollen im Überblick

| Rolle | Beschreibung | Rechte |
| :--- | :--- | :--- |
| **👑 Owner** (Besitzer) | Erstellt die Klasse. Hat alle Rechte. | Alles + Klasse löschen + Admins ernennen. |
| **🛡️ Admin** | Stellvertreter des Owners. | Benutzer verwalten, Links erstellen, Einträge verwalten. |
| **🛠️ Verwalter** (Class Admin) | Vertrauenswürdige Schüler. | Fächer anlegen, Termine verwalten. **Kein** Zugriff auf Nutzerverwaltung. |
| **👤 Mitglied** (Member) | Der Standard-Schüler. | Termine anlegen & bearbeiten. Kann **nichts** löschen oder kaputt machen. |
| **👀 Gast** (Guest) | Nur gucken, nicht anfassen. | Nur Lesezugriff. Keine Bearbeitung möglich. |

---

## Detaillierte Rechte

### Owner & Admin
*   Können Benutzer kicken oder bannen.
*   Können **Login-Links** erstellen (siehe [Zugang](/features/access)).
*   Können Backups der Datenbank herunterladen.

### Verwalter (Class Admin)
Diese Rolle ist perfekt für **Klassensprecher**.
*   Sie können Fächer anlegen (z.B. wenn ein neues Fach dazu kommt).
*   Sie können Termine pflegen.
*   Sie können aber **nicht** andere User rauswerfen oder Passwörter ändern.

### Mitglied (Member)
Das Prinzip von Classly ist **Crowdsourcing**: Jeder hilft mit.
*   Deshalb darf jedes Mitglied Hausaufgaben eintragen.
*   Aber: Um Vandalismus zu verhindern, können Mitglieder **keine Fächer löschen** oder **fremde Accounts bearbeiten**.

## Rolle ändern

Nur der **Owner** oder ein **Admin** kann Rollen ändern:
1.  Gehe im Menü auf **Erweitert** -> **Benutzer**.
2.  Wähle den Nutzer aus.
3.  Ändere die Rolle im Dropdown.
