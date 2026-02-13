---
name: versioning
description: Enforce Classly versioning workflow under `versions/` (plans/notes/changelogs). Use when the user asks for a new version, says "-p" (create a plan), references a version number (e.g. v1.0.1), or wants to update `Commit.md` / `Readme.md` as described in `AGENTS.md`.
---

# Versioning Workflow (Classly)

## Source Of Truth

- Follow `AGENTS.md` (repo root) for versioning rules.
- Keep all version artifacts under `versions/` (not runtime code).

## Paths And Conventions

- Version folder: `versions/<version>/` (example `versions/v1.0.1/`)
- Commit message file: `versions/<version>/Commit.md`
- Changelog file: `versions/<version>/Readme.md`
- Plan root (pick existing convention):
  - If `versions/plan/` exists, use `versions/plan/<version>/`.
  - Else if `versions/Plans/` exists, use `versions/Plans/<version>/`.
  - Else create and use `versions/plan/<version>/` (matches `AGENTS.md`).

## When The User Says "-p"

1. Extract the version number from the user message.
2. If no version number is provided, ask for one or propose one (do not guess silently).
3. Create the plan folder under the plan root for that version.
4. Write a markdown plan file in that folder (pick a clear name like `Plan.md` unless the user requests a specific filename).
5. Ask up to the minimum necessary questions if requirements are ambiguous.

### Plan Template (Markdown)

Use this structure and keep it concrete:

- **Summary**
- **Goals**
- **Non-Goals**
- **Scope / Changes**
- **Files / Modules**
- **Data / Migrations** (if applicable)
- **API / UI Impact** (if applicable)
- **Risks**
- **Test Plan** (include at least `python tests/verify_repo.py` when repository code changes)
- **Open Questions**

## When Creating Or Updating A Version

1. Ensure the version folder exists: `versions/<version>/`.
2. Ensure `versions/<version>/Commit.md` exists (write intended Conventional Commit style message content there).
3. Ensure `versions/<version>/Readme.md` exists (write changelog content there).
4. If the user asks for a plan, follow the "-p" section and put the plan under the plan root.

## Guardrails

- Do not put secrets into `versions/*`.
- Do not move runtime code into `versions/`.
- Prefer exact file paths and explicit version strings (e.g. `v1.0.1`) in responses and artifacts.
