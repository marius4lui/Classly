# Repository Guidelines

## Project Structure

- `app/`: FastAPI backend (entrypoint `app/main.py`), routers in `app/routers/`, models in `app/models.py`, HTML in `app/templates/`, static assets in `app/static/`.
- `docs/`: VitePress documentation site.
- `scripts/`: Maintenance and migration utilities (for example `scripts/classly_client.py`).
- `tests/`: Lightweight verification scripts (currently `tests/verify_repo.py`).
- `versions/`: Versioned planning/notes/changelogs (not runtime code).

## Build, Test, and Development Commands

- Local dev (no Docker):
  - `python -m venv venv` then `.\venv\Scripts\activate` (Windows)
  - `pip install -r requirements.txt`
  - `uvicorn app.main:app --reload` (serves `http://localhost:8000`)
- Docker (prod-ish):
  - `docker compose up -d --build`
- Docker (dev hot-reload):
  - `docker compose -f docker-compose.dev.yml up --build`
- Docs:
  - `pnpm install`
  - `pnpm docs:dev` (dev server), `pnpm docs:build`, `pnpm docs:preview`
- Repo sanity checks:
  - `python tests/verify_repo.py` (checks repository factory + interface coverage)

## Coding Style & Naming Conventions

- Python: 4-space indentation, prefer type hints for public functions, keep modules cohesive (router logic in `app/routers/*`, persistence in `app/repository/*`).
- Naming: `snake_case` for functions/vars, `PascalCase` for classes, router modules named by domain (`events.py`, `oauth.py`).

## Testing Guidelines

- There is no full unit/integration test suite yet. If you add tests, prefer `pytest` and keep them under `tests/` with names like `test_<area>.py`.
- At minimum, ensure `python tests/verify_repo.py` still passes when touching repository code.

## Commit & Pull Request Guidelines

- Commit messages generally follow a Conventional Commits style seen in history: `feat: ...`, `fix: ...`, `docs: ...`, `style: ...`, `license: ...`.
- PRs should include:
  - A clear description of behavior changes and manual test steps.
  - Linked issue (if applicable).
  - Screenshots for UI/admin/docs changes (where relevant).

## Security & Configuration Tips

- Do not commit secrets. Use `.env` (see `.env.example`) and keep tokens (API keys, OAuth tokens) out of logs and issues.
- When changing auth/API behavior, validate against the documented endpoints in `docs/development/api*.md`.

## Versioning

- Use `versions/` directory to store versioned planning/notes.
- Use `Commit.md` to store commit messages.
- Use `Readme.md` to store Changelog information.
- If I say -p you shpuld create a plan about what the changes and ask questions if needed.
  - The plan should be in `versions/` directory.
  - I always say an version number like "v1.0.1" so you should create a folder with that version number.
  - If i dont say a version number you should ask me for one or suggest one.
  - The plan should be in markdown format.
  - The plan should be in `versions/plan/<version_number>/` directory.
