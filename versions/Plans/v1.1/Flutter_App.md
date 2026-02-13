<!--
Classly Flutter App Plan
Location: versions/v1.1/Flutter_App.md
Audience: Maintainer/Contributor team (Product + Engineering)
-->

# Classly Flutter App (v1.1) - Komplettplan

## Zielbild

Eine native Mobile-App (iOS/Android) für Classly, die:

- sich gegen eine beliebige Classly-Instanz (Self-Hosted oder classly.site) verbinden kann
- Events (KA/TEST/HA/INFO) schnell und offline-first konsumierbar macht
- Push-Notifications, Widgets und System-Integrationen (Kalender, Share) bereitstellt

Wichtig: Der aktuelle Backend-Stand (FastAPI) hat zwei relevante Schnittstellen:

- **OAuth 2.0** (`/api/oauth/*`) für Mobile-Login, Scope aktuell effektiv **read-only** (`read:events`). Siehe `docs/development/api-oauth.md`.
- **Legacy API** (`/api/*`) für Mobile/Integrationen, aktuell **read-only**: `GET /api/events`, `GET /api/subjects`. Siehe `docs/development/api-legacy.md`.
- **API v1** (`/api/v1/*`) für CRUD (inkl. `events:write`), aber Auth über **API-Key** (Bearer) statt End-User OAuth. Siehe `docs/development/api-v1.md`.

Konsequenz: Eine vollwertige Mobile-App (mit Event-Erstellen/Bearbeiten) braucht entweder:

1. einen **API-Key Mode** (User erzeugt API-Key in Classly und traegt ihn in der App ein), oder
2. Backend-Erweiterungen: **OAuth Scopes + Write-Endpunkte** für Integration Tokens (empfohlen, wenn End-User UX wichtiger ist).

---

## Scope

### MVP (Phase 1, read-only, realistisch ohne Backend-Änderungen)

- Instanz-Auswahl (Base URL)
- OAuth Login (External Browser + Deep Link Callback)
- Event-Liste + Tages-/Wochenansicht
- Filter (Typ/Fach/Zeitraum), Suche
- Pull-to-refresh + Delta Sync über `updated_since`
- Offline Cache (Events/Subjects/UserInfo)
- Settings: Logout, Instanz wechseln, Cache Löschen, About/Version

### V1 (Phase 2, "produktreif")

- Push Notifications Registrierung über `/api/push/register` (benoetigt Integration Token)
- Lokale Benachrichtigungen (z.B. "morgen Hausaufgaben") auf Basis gecachter Daten
- Deep Links (z.B. `classly://event/<id>` innerhalb App)
- Home Screen Widgets (iOS/Android): naechste 3 Events, heute
- Accessibility (Screenreader, Dynamic Type, Kontrast)
- Mehrsprachigkeit (de/en, vorbereitet für weitere)

### V2 (Phase 3, write & collaboration)

Option A (ohne Backend-Aenderung):

- API-Key Mode für API v1: CRUD für Events, Anzeigen von Users, Timetable

Option B (mit Backend-Aenderung, bessere UX):

- OAuth Scopes erweitern (`events:read`, `events:write`, `subjects:read`, `timetable:read` etc.)
- API v1 für OAuth Tokens freischalten oder parallele "mobile v1" Endpunkte anbieten
- PKCE im OAuth Flow (Security)

---

## Nicht-Ziele (bewusst raus)

- Vollstaendige Feature-Paritaet mit Web UI in Phase 1
- Admin-UI für Klassen-/User-Verwaltung (erst Phase 3+)
- Complex Editor für Topics/Links an Events (erst wenn API dafür stabil ist)

---

## Personas & Kern-User-Flows

### Persona A: Schueler/in (read-first)

1. App oeffnen -> Instanz eingeben/waehlen
2. Login -> Kalenderansicht -> Events für naechste Tage sehen
3. Filter nach Fach/Typ -> Event Details -> Link oeffnen/teilen

### Persona B: Klassen-Admin (write)

1. Login -> Events erstellen/bearbeiten -> Push/Reminder relevant
2. (API-Key Mode) Key generieren -> in App hinterlegen -> CRUD

---

## Informationsarchitektur (Screens)

### Onboarding

- `InstanceSelect`: Base URL eingeben (z.B. `https://classly.site` oder eigene Domain)
- `Login`: "Mit Classly anmelden" (oeffnet Browser zu `/api/oauth/authorize`)
- `CallbackHandler`: nimmt `code` entgegen, tauscht gegen `access_token`

### Hauptnavigation (Bottom Nav)

- `Kalender`
- `Events` (Liste, sortiert nach Datum, sticky "Heute")
- `Faecher` (read-only; für Filter)
- `Einstellungen`

### Detail/Utility

- `EventDetail`
- `FilterSheet`
- `Debug/Diagnostics` (optional, hidden: Logs, letzte Sync-Zeit, Token Status)

---

## Datenmodell (App-intern)

### Entities (Domain)

- `UserSession`
  - `baseUrl`
  - `accessToken` (Integration Token aus OAuth)
  - `classId`
  - `scope`
  - `userInfo` (aus `/api/oauth/userinfo`)
- `Event`
  - `id`, `type`, `date`, `subjectName`, `title`, `updatedAt`, `createdAt`
  - optional: `priority`, `topics`, `links` (Legacy `/api/events` liefert bereits `topics`/`links` in diesem Repo-Stand)
- `Subject`
  - `id`, `name`, `color`

### Storage (Offline)

- Secure: `accessToken` in `flutter_secure_storage`
- Cache/DB: Events/Subjects in lokaler DB (Drift/Isar)
- Preferences: Base URL, UI Settings, letzte Sync Timestamp

---

## API-Integration (konkret)

### Base URL

- Nutzer-configured, z.B. `https://classly.site`
- Alle Requests relativ dazu, Pfade:
  - OAuth: `/api/oauth/authorize`, `/api/oauth/token`, `/api/oauth/userinfo`
  - Daten (read-only): `/api/events`, `/api/subjects`
  - Push (spaeter): `/api/push/register`, `/api/push/unregister`

### Auth Flow (Phase 1)

1. App baut authorize URL:
   - `GET {baseUrl}/api/oauth/authorize?client_id=classly-flutter&redirect_uri=classly://auth/callback&scope=read:events&response_type=code`
2. App oeffnet System-Browser (kein WebView, damit Login/Magic Link sauber funktioniert).
3. OS deep-linkt zur App: `classly://auth/callback?code=...`
4. App tauscht Code:
   - `POST {baseUrl}/api/oauth/token` (x-www-form-urlencoded)
5. App speichert `access_token` (secure storage).
6. App laedt `GET {baseUrl}/api/oauth/userinfo` und zeigt Class/User Context.

Hinweis Security:

- Der aktuelle Backend-Token-Exchange kennt **kein PKCE**. für Phase 1 ok, aber Phase 2/3 sollte PKCE im Backend nachgeruestet werden.

### Data Sync (Phase 1)

- Initial:
  - `GET /api/subjects`
  - `GET /api/events?limit=500`
- Delta:
  - `GET /api/events?updated_since=<lastSyncIso>&limit=500`
- Konflikte: read-only -> keine

### Write Support (Phase 3 Optionen)

- API-Key Mode:
  - `Authorization: Bearer cl_live_...`
  - `GET/POST/PUT/DELETE /api/v1/events`
- OAuth Write:
  - Backend muss Scopes/Autorisierung und Endpunkte bereitstellen (siehe Abschnitt "Backend Roadmap")

---

## App-Architektur (Flutter)

Empfehlung: Clean-ish Architecture, pragmatisch, testbar.

- Presentation: Flutter UI + State (Riverpod)
- Application: UseCases (FetchEvents, SyncEvents, Login, Logout)
- Domain: Entities + Repositories (Interfaces)
- Infrastructure: API Client (Dio), DTOs, Storage (Drift/Isar), Auth/Deep Links

### State Management

- `flutter_riverpod` + `riverpod_generator`
- Async loading states über `AsyncValue`

### Routing

- `go_router` (Deep Link Support, Guard für Auth)

### Networking

- `dio` + Interceptors:
  - Auth header injection
  - Retry bei transient errors (mit Backoff)
  - 401 -> Session invalid -> Logout/Relogin Flow

### Serialization

- `freezed` + `json_serializable`
- DateTime: strikt ISO 8601, server sends z.T. `Z` -> `DateTime.parse`

---

## Projektstruktur (Vorschlag)

Repo-Scope: eigener Flutter Ordner im Repo (z.B. `mobile/`), damit Backend/Web nicht vermischt wird.

```
mobile/
  pubspec.yaml
  lib/
    main.dart
    app/
      config/            # env, baseUrl handling
      routing/
      theme/
      l10n/
    features/
      auth/
        data/
        domain/
        presentation/
      events/
      subjects/
      settings/
    shared/
      http/
      storage/
      widgets/
      utils/
  test/
  integration_test/
```

---

## UI/Design System

Ziel: schnell, klar, "schul-kompatibel".

- Farb-Codierung für Event Types (KA/TEST/HA/INFO)
- Typography: gut lesbar, Large Text support
- Komponenten:
  - EventCard, SubjectChip, EmptyState, ErrorState, Skeletons
- Kalender:
  - Phase 1: Liste + einfache Week Strip (Custom)
  - Phase 2: optional Paket wie `table_calendar` (mit Design Anpassung)

---

## Push & Notifications (Phase 2)

### Remote Push (Backend -> Device)

- Android: FCM
- iOS: APNs (meist via FCM Bridge)
- App registriert Device Token nach Login:
  - `POST /api/push/register` (platform: `fcm` oder `apns`)
- App deregistriert beim Logout:
  - `DELETE /api/push/unregister`

### Lokale Reminder (On-device)

- Regel: "Morgen" oder "naechste Woche" Zusammenfassung
- Engine: Background fetch (platform-limited), ansonsten beim App-open neu planen

---

## Offline-Strategie

- "Stale-while-revalidate":
  - UI zeigt Cache sofort
  - Sync im Hintergrund
- Datenintegritaet:
  - Events nach `id` upserten
  - Deleted Events: Backend liefert aktuell keine Tombstones im read-only Flow
    - Phase 1: kompletter Refetch 1x/Tag oder bei "Force Refresh"
    - Phase 2: Backend-Delta mit Deleted IDs (Empfehlung)

---

## Observability & Qualitaet

- Logging:
  - minimaler client-side log (debug screen)
- Crash Reporting:
  - optional Sentry (konfigurierbar, für self-hosting sensibel)
- Analytics:
  - default off, opt-in

### Tests

- Unit: parsing, sync logic, date grouping, filtering
- Widget tests: states (loading/empty/error)
- Integration tests: login callback parsing, list rendering

### CI

- `flutter analyze`
- `flutter test`
- Build check Android/iOS (signing optional)

---

## Backend Roadmap (damit Mobile wirklich "voll")

Wenn die App Events erstellen/bearbeiten soll ohne API-Key UX:

1. OAuth PKCE:
   - `/api/oauth/token` akzeptiert `code_verifier`
   - `/api/oauth/authorize` erzeugt code_challenge binding
2. Scope System:
   - statt `read:events` -> `events:read`/`events:write` analog API v1
3. Write Endpoints für Integration Token:
   - entweder API v1 für OAuth Tokens freischalten
   - oder neue Endpoints `/api/mobile/v1/events` mit identischen DTOs
4. Delta Sync inkl. Deletes:
   - `GET /api/events?updated_since=...` liefert `deleted_event_ids: []`

---

## Meilensteine (konkret)

### M0: Repo/Tooling (0.5-1 Tag)

- Flutter Projekt anlegen (`mobile/`)
- Flavor/Config: Dev/Prod, BaseUrl-Override
- Lints + formatter + CI skeleton

### M1: Auth + Read-Only Data (2-4 Tage)

- Deep Link Setup (iOS + Android)
- OAuth Flow (authorize -> callback -> token)
- `userinfo` anzeigen
- Events/Subjects laden + Cache + UI

### M2: UX Polish (2-4 Tage)

- Filter/Search
- Empty/Error states
- Performance (list virtualization, memoization)
- i18n (de/en)

### M3: Notifications + Widgets (3-6 Tage)

- Push registration + permission flows
- Local reminders
- Widgets

### M4: Write Support (nach Strategie)

- API-Key Mode (schnell) oder OAuth+Backend (sauber)

---

## Offene Entscheidungen (bitte als Issue-Liste tracken)

- Soll die App **nur** Classly Cloud (classly.site) targeten oder explizit Self-Hosted Instanzen als 1st-class citizen?
- Welche Strategie für Write:
  - API-Key Mode (sofort möglich, UX weniger gut)
  - OAuth erweitern (Backend Arbeit, beste UX)
- Push: welche Events triggern Notifications (nur neue? auch Updates/Deletes?)
- Datenschutz: Default-off Telemetrie, Crash reporting opt-in?
