## Classly v1.0.1

Release date: 2026-02-13

## Changelog

### Security hardening update (2026-02-13)

#### Added

- CSRF protection (double-submit token) with middleware and frontend integration.
- New CSRF utility module: `app/core/csrf.py`.
- Security headers middleware (CSP, X-Frame-Options, X-Content-Type-Options, Referrer-Policy, optional HSTS).

#### Changed

- OAuth flow hardened:
  - strict client/redirect validation (feature-flagged),
  - optional enforced `client_secret`,
  - scope allowlist validation.
- Session cookie security hardened:
  - `secure` now environment-driven (`COOKIE_SECURE`, default `true`),
  - logout switched to `POST /auth/logout` (legacy GET behind env flag).
- CORS hardened to explicit allowlist via `CORS_ALLOW_ORIGINS` (no wildcard origins).
- Cross-domain migration redirect no longer leaks session token in query string.
- Admin backup error response no longer leaks internal exception details.
- Public feed endpoints (`/feed/rss`, `/feed/xml`) can require token (`PUBLIC_FEED_TOKEN_REQUIRED=true`).
- Frontend XSS hardening in event detail scripts:
  - escaped user-controlled content before HTML interpolation,
  - safe URL handling and `rel="noopener noreferrer"` for external links.

#### Files touched

- `app/main.py`
- `app/core/csrf.py`
- `app/routers/auth.py`
- `app/routers/oauth.py`
- `app/routers/admin.py`
- `app/routers/events.py`
- `app/routers/i18n_router.py`
- `app/templates/base.html`
- `app/templates/dashboard.html`
- `app/templates/partials/_scripts.html`

### Added

- Setup Mini CLI for Docker hosting: interactive `quick` and `advanced` modes.
- Safe config workflow with diff preview, confirmation, and automatic backups.
- Backup restore command for config snapshots.
- Coolify-aware target mode for compose handling.
- Dedicated docs page: `docs/setup/mini-cli.md`.
- `pnpm` script entrypoints for setup CLI workflows.

### Changed

- `scripts/setup.sh` now starts the new setup CLI by default.
- `scripts/setup.sh` keeps backwards compatibility for legacy class bootstrap args (`--class-name`, `--user-name`).
- Setup docs and sidebar now link to the new Setup Mini CLI guide.

### i18n integration update (2026-02-13)

#### Added

- Full timetable translation keysets for German and English with consistent structure.
- Public timetable translation keys for shared/read-only timetable views.
- JS-side i18n payload for dynamic UI messages and labels in timetable views.

#### Changed

- Replaced hardcoded timetable UI labels/messages with `request.state.t(...)` keys.
- Replaced hardcoded public timetable labels/messages with `request.state.t(...)` keys.
- Dynamic lesson labels now use locale key (`slot_unit`) instead of static text.

#### Files touched

- `app/locales/de.json`
- `app/locales/en.json`
- `app/templates/timetable.html`
- `app/templates/timetable_public.html`

### Previous v1.0.1 updates (Timetable)

- Timetable is available for all logged-in class members (no email/password registration required).
- Admin/Class-Admin timetable editing improved (inline edit + quick edit by click).
- Bulk slot creation for multiple lesson numbers in one action.
- Public timetable share link with short URL code (read-only).
- Timetable UI improvements (sticky headers, better slot picker, better editor layout).

## Technical notes

- New Python dependencies in `requirements.txt`:
  - `questionary`
  - `ruamel.yaml`
  - `rich`
- New test file: `tests/test_setup_cli.py`.
