# Classly v1.0.1

Release date: 2026-02-13

## Highlights

- New Setup Mini CLI for Docker config with quick and advanced wizard modes.
- Safe config changes with preview, confirmation, backup, and restore.
- Setup docs now include a dedicated CLI guide.
- Timetable upgrades: broader access, better admin editing, bulk creation, and public sharing.

## Changelog

### Setup and DevOps

- Added `scripts/classly_setup_cli.py` with commands:
  - `wizard`
  - `quick`
  - `advanced`
  - `validate`
  - `preview`
  - `restore --backup <dir>`
- Updated `scripts/setup.sh`:
  - default path now uses Setup Mini CLI
  - legacy class bootstrap args remain supported
- Added pnpm command integration:
  - `pnpm run setup:cli`
  - `pnpm run setup:quick`
  - `pnpm run setup:advanced`
  - `pnpm run setup:preview`
  - `pnpm run setup:validate`

### Documentation

- Added `docs/setup/mini-cli.md`.
- Linked Setup Mini CLI from:
  - `docs/setup/installation.md`
  - `docs/setup/configuration.md`
  - setup sidebar in `docs/.vitepress/config.mts`

### Timetable

- Timetable available for all logged-in members.
- Admin editing improved with inline and quick edit flows.
- Multi-slot creation for timetable entries.
- Public read-only timetable share links.
- UI improvements for timetable table and editor.

## Notes

- New Python dependencies:
  - `questionary`
  - `ruamel.yaml`
  - `rich`

