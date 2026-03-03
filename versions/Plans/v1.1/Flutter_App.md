<!--
Classly Flutter App Plan
Location: versions/Plans/v1.1/Flutter_App.md
Audience: Maintainer/Contributor team (Product + Engineering)
Updated: 2026-03-03
-->

# Classly Flutter App (v1.1) - Produkt- und Architekturplan

## Summary

Classly bekommt eine eigene Flutter-App fuer iOS und Android. Die App uebernimmt das **visuelle und UX-seitige Referenzbild** von `C:\Users\Marius\Projekte\Dev\MVPs\plane-mobile`, uebernimmt aber **keine fremde Business-Logik**. Alle produktiven Flows, Datenmodelle und Integrationen muessen aus Classly abgeleitet werden.

Kurzform:

- **UI/UX Referenz:** `plane-mobile`
- **Produktlogik und Features:** Classly
- **Technische Umsetzung:** neue Flutter-Codebasis unter `mobile/`

## Umsetzungsstand (2026-03-03)

Die Codebasis unter `mobile/` ist fuer den read-only MVP bereits angelegt und umfasst aktuell:

- Flutter-App-Shell mit Riverpod, GoRouter, Dio, Freezed/JSON und Secure Storage
- Instanz-Auswahl, Login-Shell und OAuth-Callback-Handling
- Event- und Subject-Mapping aus der Legacy API
- Read-only Sync-Pipeline mit stale-while-revalidate-Verhalten
- Kalender-, Event-, Fach-, Settings- und Diagnostics-Screens
- Filter-, Such- und Logout-/Switch-Instance-Logik

Wichtige Statushinweise:

- Die Session-Speicherung ist sicher umgesetzt, der Event-/Subject-Cache ist aktuell als austauschbare lokale Store-Abstraktion umgesetzt.
- Fuer produktiven OAuth-Login braucht das Backend weiterhin einen registrierten Mobile-Client und je nach Server-Config ein passendes `client_secret`.

---

## Zielbild

Eine native Mobile-App, die:

- sich gegen eine beliebige Classly-Instanz verbinden kann
- den read-only Event-Konsum fuer Schueler/Lehrkraefte schnell und offline-first macht
- sich optisch und in der Interaktion wie `plane-mobile` anfuehlt
- spaeter Push, Widgets und optional Write-Support erhaelt

Wichtige Produktregel:

- aus `plane-mobile` werden nur **relevante visuelle Muster und Interaktionsmuster** uebernommen
- nicht uebernommen werden Projekt-, Workspace-, Issue-, Dashboard- und andere Plane-spezifische Konzepte

---

## Design-Leitlinie

### Was genau aus `plane-mobile` uebernommen werden soll

- Screen-Rhythmus und Spacing
- Formular-Layout und CTA-Hierarchie
- Card-Stil fuer Listen und Detailcontainer
- Bottom-Navigation-Gefuehl
- Sheet-Muster fuer Filter und Aktionen
- Loading-, Empty- und Error-States
- Theme-Grundrichtung fuer helle/dunkle Oberflaechen

### Was explizit nicht uebernommen werden soll

- bestehende Provider-Architektur
- Service- und Repository-Implementierungen
- Auth-Flows ausser als visuelle Referenz
- Plane-Domainobjekte wie Projects, Issues, Workspaces, Cycles, Modules
- bestehende API-Client-Logik

### Design Translation fuer Classly

- `plane` Onboarding -> `Classly InstanceSelect + Login`
- `plane` Dashboard -> `Classly Kalender`
- `plane` Listen- und Card-Muster -> `Classly Event-Liste`
- `plane` Filter-Bottom-Sheets -> `Classly Event-Filter`
- `plane` Settings/Profile Patterns -> `Classly Einstellungen`

---

## Classly-Funktionsbasis

Aktueller Backend-Stand:

- **OAuth 2.0** ueber `/api/oauth/*` fuer Mobile Login
- **Legacy API** ueber `/api/*` fuer read-only Daten
- **API v1** ueber `/api/v1/*` fuer CRUD mit API-Key

Konsequenz fuer den Mobile Scope:

- MVP bleibt read-only
- Write wird spaeter entweder mit API-Key-Mode oder per Backend-Erweiterung gebaut

---

## Scope

### MVP / Phase 1

- Base-URL / Instanz-Auswahl
- OAuth Login im System-Browser
- Deep Link Callback
- Userinfo laden
- Event-Liste
- einfache Kalender-/Wochenansicht
- Filter nach Typ, Fach, Zeitraum
- Suche
- Pull-to-refresh
- Delta-Sync mit `updated_since`
- Session-Kontext persistent, Event-/Subject-Cache im MVP zunaechst als lokale Store-Abstraktion mit spaeterer Drift-Haertung
- Einstellungen: Logout, Instanz wechseln, Cache leeren, App-Version

### Phase 2

- lokale Benachrichtigungen auf Basis gecachter Daten
- Deep Links innerhalb der App
- Widgets fuer "Heute" und "Naechste Events"
- Accessibility Ausbau
- Mehrsprachigkeit de/en
- UI-Polish und Performance-Haertung

### Phase 3

- Write-Support per API-Key oder erweitertem OAuth
- Push-Registrierung
- Event CRUD
- spaetere Kollaborationsfunktionen

---

## Non-Goals

- 1:1 Port von `plane-mobile`
- Uebernahme fremder Business-Logik
- komplette Web-Feature-Paritaet in Phase 1
- Admin-Funktionen fuer User-/Klassenverwaltung im MVP
- komplexer Event-Editor im ersten Release

---

## Personas und Kernfluesse

### Persona A: Schueler/in

1. App oeffnen
2. Classly-Instanz eingeben oder waehlen
3. Login ueber Classly OAuth
4. Event-Liste oder Kalender sehen
5. Nach Fach/Typ filtern
6. Event-Details und Links aufrufen

### Persona B: Lehrkraft / Klassenverantwortliche

1. App oeffnen
2. Login
3. Tages- oder Wochenereignisse pruefen
4. Push/Reminder spaeter nutzen
5. optional spaeter Write-Funktionen nutzen

---

## Informationsarchitektur

### Onboarding

- `Splash`
- `InstanceSelect`
- `Login`
- `CallbackHandler`
- `SessionBootstrap`

### Hauptnavigation

- `Kalender`
- `Events`
- `Faecher`
- `Einstellungen`

### Utility / Detail

- `EventDetail`
- `FilterSheet`
- `Search`
- `Diagnostics` (optional, hidden)

---

## Screen-Mapping: Plane UI -> Classly UI

### 1. Onboarding und Login

Referenz aus `plane-mobile`:

- grosse, klare Formblocs
- starke CTA-Flaeche
- reduzierte, ruhige Anordnung
- deutliche Success/Error-Baender

Classly-Umsetzung:

- Instanz-Eingabe vor dem Login
- Login-CTA startet OAuth statt Plane-Auth
- optional sekundare Instanz-Historie / zuletzt verwendet
- Session-Context nach Login sichtbar machen

### 2. Home / Hauptscreen

Referenz aus `plane-mobile`:

- tab-basierte Primärnavigation
- klare Inhaltsblöcke
- Karten mit leichter Trennung und ruhiger Hierarchie

Classly-Umsetzung:

- Bottom Nav mit 4 Tabs statt Plane-5er-Navigation
- Standard-Einstieg in `Kalender`
- Events-Tab fuer dichte Liste

### 3. Listen und Detail

Referenz aus `plane-mobile`:

- kompakte Cards
- saubere Typografie
- klare Trennung von Meta-Daten und Hauptinhalt

Classly-Umsetzung:

- `EventCard` mit Typ-Badge, Fach, Datum, Kurztext
- `EventDetail` als Screen oder modal Sheet
- typfarbige visuelle Marker fuer KA/TEST/HA/INFO

### 4. Filter und Utility

Referenz aus `plane-mobile`:

- Bottom Sheets fuer Auswahl und Filter

Classly-Umsetzung:

- Filter-Sheet fuer Typ, Fach, Zeitraum
- spaeter Sortierung und gespeicherte Filter

---

## Datenmodell

### Domain Entities

- `UserSession`
  - `baseUrl`
  - `accessToken`
  - `scope`
  - `userInfo`
- `Event`
  - `id`
  - `type`
  - `date`
  - `title`
  - `subjectName`
  - `updatedAt`
  - `createdAt`
  - optional `priority`, `topics`, `links`
- `Subject`
  - `id`
  - `name`
  - `color`

### Lokale Persistenz

- Secure Storage:
  - Access Token
- lokale Datenbank:
  - Events
  - Subjects
- Shared Preferences / simple settings:
  - Base URL
  - letzte Sync-Zeit
  - UI-Preferences

---

## API-Integration

### OAuth Flow

1. App baut Authorize URL
2. App oeffnet System-Browser
3. Callback via Deep Link
4. Token Exchange
5. Access Token sicher speichern
6. `userinfo` laden
7. App bootstrappt Session

### Read-Only Sync

- Initial:
  - `GET /api/subjects`
  - `GET /api/events?limit=500`
- Delta:
  - `GET /api/events?updated_since=<iso>&limit=500`

### Spaeterer Write-Support

- Option A:
  - API-Key Mode fuer `/api/v1/events`
- Option B:
  - OAuth Scopes und Endpunkte erweitern

---

## App-Architektur

Empfehlung: neue Classly-Mobile-App unter `mobile/` mit klarer Feature-Trennung.

### Architekturprinzip

- visuelle Referenz von Plane
- technische Struktur neu
- keine Copy-Paste-Architektur aus der Referenz-App

### Layer

- `presentation`
  - Screens, Widgets, State Binding
- `application`
  - Use Cases wie `login`, `syncEvents`, `logout`
- `domain`
  - Entities, Repository Interfaces
- `infrastructure`
  - Dio Client, DTOs, Mappers, Storage, Deep Links

### State Management

- `flutter_riverpod`
- `AsyncValue`
- Feature-spezifische Provider statt globalem Provider-Monolith

### Routing

- `go_router`
- Route Guards fuer Session
- Deep Link Handling von Anfang an mitdenken

### Networking

- `dio`
- Interceptors fuer:
  - Auth Header
  - Retry / Backoff
  - Session Invalidierung bei 401

### Modellierung

- `freezed`
- `json_serializable`

---

## Projektstruktur

```text
mobile/
  pubspec.yaml
  lib/
    main.dart
    app/
      bootstrap/
      config/
      routing/
      theme/
      l10n/
    features/
      auth/
        data/
        domain/
        presentation/
      events/
        data/
        domain/
        presentation/
      subjects/
        data/
        domain/
        presentation/
      settings/
        data/
        domain/
        presentation/
    shared/
      http/
      storage/
      widgets/
      utils/
  test/
  integration_test/
```

---

## Design System fuer die neue App

### Grundrichtung

- visuell nah an `plane-mobile`
- inhaltlich klar auf Schule, Termine, Hausaufgaben und Klassenkontext ausgerichtet

### Komponenten

- `PrimaryButton`
- `SecondaryButton`
- `AppTextField`
- `EventCard`
- `SubjectChip`
- `WeekStrip`
- `SectionHeader`
- `EmptyState`
- `ErrorState`
- `LoadingSkeleton`
- `BottomFilterSheet`

### UI-Regeln

- starke Lesbarkeit
- wenig visuelles Rauschen
- grosse Touch-Ziele
- konsistente Abstaende
- farbliche Event-Typ-Unterscheidung

### Event-Type Farben

- `KA`
- `TEST`
- `HA`
- `INFO`

Die finalen Farben sollen aus dem Plane-Look abgeleitet werden, aber fuer Bildungs- und Kalenderkontext besser differenzierbar sein.

---

## Offline-Strategie

- Stale-while-revalidate
- Cache zuerst anzeigen
- Hintergrundsync beim Screen-Start und Pull-to-refresh
- Upsert ueber Event-ID
- periodischer Full-Refresh gegen fehlende Delete-Tombstones

---

## Qualitaet und Beobachtbarkeit

### Tests

- Unit:
  - DTO Parsing
  - Mappers
  - Sync-Logik
  - Filterlogik
  - Date Grouping
- Widget:
  - Loading
  - Empty
  - Error
  - EventCard Rendering
  - Login Flow UI
- Integration:
  - Deep Link Parsing
  - Session Bootstrap
  - Event-Listenaufbau aus Cache

### CI

- `flutter analyze`
- `flutter test`
- spaeter Build Checks fuer Android/iOS

---

## Risiken

- zu starke visuelle Naehe zu Plane kann fachlich falsche Erwartungen erzeugen
- OAuth ohne PKCE ist nur eine Zwischenloesung
- fehlende Delete-Tombstones erschweren perfekten Delta-Sync
- Write-Support ist ohne Backend-Arbeit oder API-Key-UX nicht sauber loesbar

---

## Entscheidungen fuer die Umsetzung

### Festgelegt

- neue Flutter-App statt Fork oder Port
- Plane nur als UI/UX-Referenz
- MVP read-only
- Self-hosted Instanzen bleiben first-class citizen
- `drift` ist als Persistenz-Basis in der Mobile-App vorgesehen; die aktuelle MVP-Implementierung nutzt davor noch austauschbare In-Memory-Stores fuer Events und Subjects

### Noch offen

- genaue Farbpalette und Font-Setup fuer den finalen Mobile Design System Layer
- ob API-Key-Mode ueberhaupt in Phase 3 gewollt ist
- welche Reminder-Regeln produktseitig sinnvoll sind

---

## Naechste sinnvolle Umsetzungsreihenfolge

1. neues `mobile/` Projekt anlegen
2. Theme- und Design-System aus Plane-Look nachbauen, aber technisch sauber neu strukturieren
3. Routing und Session-Guard aufsetzen
4. `InstanceSelect` und OAuth Login umsetzen
5. Legacy read-only Sync fuer Events und Subjects aufbauen
6. Event-Liste und Kalender-UI auf MVP-Level liefern
7. Offline-Cache und Delta-Sync haerten
8. Filter, Suche, Settings und Diagnostics abschliessen
