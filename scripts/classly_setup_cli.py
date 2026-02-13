#!/usr/bin/env python3
"""
Classly Setup CLI

Interactive configuration wizard for Docker-based Classly hosting.
Features:
- quick and advanced modes
- preview diff before write
- automatic backups
- restore from backup snapshot
"""

from __future__ import annotations

import argparse
import difflib
import json
import os
import shutil
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

try:
    import questionary
except Exception:  # pragma: no cover - optional import guard
    questionary = None

try:
    from ruamel.yaml import YAML
    from ruamel.yaml.comments import CommentedMap, CommentedSeq
except Exception:  # pragma: no cover - optional import guard
    YAML = None
    CommentedMap = dict  # type: ignore[assignment]
    CommentedSeq = list  # type: ignore[assignment]


DEFAULT_ENV_FILE = ".env"
DEFAULT_COMPOSE_FILE = "docker-compose.yml"
DEFAULT_COOLIFY_FILE = "docker-compose.coolify.yml"
BACKUP_ROOT = ".backups"


@dataclass
class WizardConfig:
    target: str  # normal | coolify
    port: int
    max_classes: str
    migrate_from_domain: str
    migrate_to_domain: str
    database_url: str
    appwrite: bool
    appwrite_endpoint: str
    appwrite_project_id: str
    appwrite_api_key: str
    appwrite_database_id: str
    automigrate_to: str
    secret_key: str
    timezone: str


def _die(message: str, code: int = 1) -> None:
    print(f"Error: {message}", file=sys.stderr)
    raise SystemExit(code)


def _require_ruamel() -> None:
    if YAML is None:
        _die("ruamel.yaml is required. Install dependencies: pip install -r requirements.txt")


def _load_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def _write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _parse_env_lines(content: str) -> Dict[str, str]:
    result: Dict[str, str] = {}
    for raw in content.splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, val = line.split("=", 1)
        result[key.strip()] = val.strip()
    return result


def _render_env_with_updates(content: str, updates: Dict[str, str]) -> str:
    lines = content.splitlines()
    key_seen: Dict[str, bool] = {k: False for k in updates}
    out_lines: List[str] = []

    for raw in lines:
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in raw:
            out_lines.append(raw)
            continue

        key, _ = raw.split("=", 1)
        key = key.strip()
        if key in updates:
            out_lines.append(f"{key}={updates[key]}")
            key_seen[key] = True
        else:
            out_lines.append(raw)

    if out_lines and out_lines[-1].strip() != "":
        out_lines.append("")

    missing = [k for k, seen in key_seen.items() if not seen]
    if missing:
        out_lines.append("# Added by classly_setup_cli.py")
        for k in missing:
            out_lines.append(f"{k}={updates[k]}")

    return "\n".join(out_lines).rstrip() + "\n"


def _normalize_target(target: str, compose_file: Path) -> str:
    if target:
        return target
    if "coolify" in compose_file.name.lower():
        return "coolify"
    return "normal"


def _yaml_load(path: Path) -> CommentedMap:
    _require_ruamel()
    if not path.exists():
        _die(f"Compose file not found: {path}")
    yaml = YAML()
    yaml.preserve_quotes = True
    with path.open("r", encoding="utf-8") as f:
        data = yaml.load(f)
    if not isinstance(data, CommentedMap):
        _die(f"Invalid YAML in {path}")
    return data


def _yaml_dump(data: CommentedMap) -> str:
    _require_ruamel()
    yaml = YAML()
    yaml.preserve_quotes = True
    yaml.indent(mapping=2, sequence=4, offset=2)
    from io import StringIO

    buf = StringIO()
    yaml.dump(data, buf)
    return buf.getvalue()


def _ensure_services_classly(data: CommentedMap) -> CommentedMap:
    services = data.get("services")
    if not isinstance(services, CommentedMap):
        _die("Compose file missing top-level 'services'.")
    classly = services.get("classly")
    if not isinstance(classly, CommentedMap):
        _die("Compose file missing 'services.classly'.")
    return classly


def _set_env_list(classly: CommentedMap, env_items: Iterable[str]) -> None:
    seq = CommentedSeq()
    for item in env_items:
        seq.append(item)
    classly["environment"] = seq


def _ensure_env_file(classly: CommentedMap, env_path: str) -> None:
    env_file = classly.get("env_file")
    if isinstance(env_file, CommentedSeq):
        if env_path not in env_file:
            env_file.append(env_path)
        return
    seq = CommentedSeq()
    seq.append(env_path)
    classly["env_file"] = seq


def patch_compose_content(
    compose_content: str, config: WizardConfig, target: str, env_rel_path: str
) -> str:
    _require_ruamel()
    yaml = YAML()
    yaml.preserve_quotes = True
    data = yaml.load(compose_content) if compose_content.strip() else CommentedMap()
    if not isinstance(data, CommentedMap):
        _die("Compose content is not a mapping.")

    classly = _ensure_services_classly(data)

    env_items = [
        "PORT=8000",
        "DATABASE_URL=${DATABASE_URL:-sqlite:////data/classly.db}",
        "MIGRATE_FROM_DOMAIN=${MIGRATE_FROM_DOMAIN}",
        "MIGRATE_TO_DOMAIN=${MIGRATE_TO_DOMAIN}",
        "APPWRITE=${APPWRITE:-false}",
        "APPWRITE_ENDPOINT=${APPWRITE_ENDPOINT}",
        "APPWRITE_PROJECT_ID=${APPWRITE_PROJECT_ID}",
        "APPWRITE_API_KEY=${APPWRITE_API_KEY}",
        "APPWRITE_DATABASE_ID=${APPWRITE_DATABASE_ID:-classly_db}",
        "AUTOMIGRATE_TO=${AUTOMIGRATE_TO}",
    ]

    _set_env_list(classly, env_items)
    _ensure_env_file(classly, env_rel_path)

    if target == "coolify":
        expose = CommentedSeq()
        expose.append("8000")
        classly["expose"] = expose
        if "ports" in classly:
            del classly["ports"]
    else:
        ports = CommentedSeq()
        ports.append("${PORT:-8000}:8000")
        classly["ports"] = ports

    return _yaml_dump(data)


def _compute_env_updates(config: WizardConfig) -> Dict[str, str]:
    updates = {
        "PORT": str(config.port),
        "MAX_CLASSES": config.max_classes,
        "MIGRATE_FROM_DOMAIN": config.migrate_from_domain,
        "MIGRATE_TO_DOMAIN": config.migrate_to_domain,
        "DATABASE_URL": config.database_url,
        "APPWRITE": "true" if config.appwrite else "false",
        "APPWRITE_ENDPOINT": config.appwrite_endpoint,
        "APPWRITE_PROJECT_ID": config.appwrite_project_id,
        "APPWRITE_API_KEY": config.appwrite_api_key,
        "APPWRITE_DATABASE_ID": config.appwrite_database_id,
        "AUTOMIGRATE_TO": config.automigrate_to,
        "SECRET_KEY": config.secret_key,
        "TZ": config.timezone,
    }
    return updates


def _preview_diff(path: Path, before: str, after: str) -> str:
    diff = difflib.unified_diff(
        before.splitlines(),
        after.splitlines(),
        fromfile=f"{path}.before",
        tofile=f"{path}.after",
        lineterm="",
    )
    return "\n".join(diff)


def _create_backup(paths: List[Path]) -> Path:
    stamp = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
    backup_dir = Path(BACKUP_ROOT) / stamp
    for path in paths:
        if not path.exists():
            continue
        target = backup_dir / path
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, target)

    meta = {
        "created_utc": datetime.utcnow().isoformat() + "Z",
        "files": [str(p) for p in paths],
    }
    backup_dir.mkdir(parents=True, exist_ok=True)
    (backup_dir / "meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    return backup_dir


def _restore_backup(backup_path: Path) -> None:
    if not backup_path.exists():
        _die(f"Backup path does not exist: {backup_path}")

    if backup_path.is_file():
        _die("Restore expects a backup directory created by this CLI.")

    meta = backup_path / "meta.json"
    if not meta.exists():
        _die("Backup directory missing meta.json.")

    payload = json.loads(meta.read_text(encoding="utf-8"))
    files = payload.get("files", [])
    for rel in files:
        src = backup_path / rel
        dst = Path(rel)
        if not src.exists():
            continue
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)

    print(f"Restored {len(files)} file(s) from {backup_path}")


def _validate_config(config: WizardConfig) -> List[str]:
    errs: List[str] = []
    if config.port < 1 or config.port > 65535:
        errs.append("PORT must be between 1 and 65535.")
    if config.appwrite:
        for key, val in [
            ("APPWRITE_ENDPOINT", config.appwrite_endpoint),
            ("APPWRITE_PROJECT_ID", config.appwrite_project_id),
            ("APPWRITE_API_KEY", config.appwrite_api_key),
        ]:
            if not val.strip():
                errs.append(f"{key} is required when APPWRITE=true.")
        if config.automigrate_to and config.automigrate_to != "appwrite":
            errs.append("AUTOMIGRATE_TO must be 'appwrite' or empty when APPWRITE=true.")
    return errs


def _ask_text(message: str, default: str = "") -> str:
    if questionary is None:
        _die("questionary is required for interactive mode. Install requirements.txt.")
    return questionary.text(message, default=default).ask() or ""


def _ask_int(message: str, default: int) -> int:
    while True:
        raw = questionary.text(message, default=str(default)).ask() or str(default)
        try:
            return int(raw)
        except ValueError:
            print("Please enter a valid integer.")


def _ask_select(message: str, choices: List[str], default: str) -> str:
    if questionary is None:
        _die("questionary is required for interactive mode. Install requirements.txt.")
    return questionary.select(message, choices=choices, default=default).ask() or default


def _ask_confirm(message: str, default: bool = True) -> bool:
    if questionary is None:
        _die("questionary is required for interactive mode. Install requirements.txt.")
    return bool(questionary.confirm(message, default=default).ask())


def collect_config(mode: str, target: str, env_current: Dict[str, str]) -> WizardConfig:
    is_advanced = mode == "advanced"

    port = _ask_int("Public HTTP port:", int(env_current.get("PORT", "8000") or "8000"))
    max_classes = _ask_text("MAX_CLASSES (empty = unlimited):", env_current.get("MAX_CLASSES", ""))
    migrate_from = _ask_text("MIGRATE_FROM_DOMAIN (optional):", env_current.get("MIGRATE_FROM_DOMAIN", ""))
    migrate_to = _ask_text("MIGRATE_TO_DOMAIN (optional):", env_current.get("MIGRATE_TO_DOMAIN", ""))

    database_url = env_current.get("DATABASE_URL", "sqlite:////data/classly.db")
    appwrite = (env_current.get("APPWRITE", "false").lower() == "true")
    appwrite_endpoint = env_current.get("APPWRITE_ENDPOINT", "https://cloud.appwrite.io/v1")
    appwrite_project_id = env_current.get("APPWRITE_PROJECT_ID", "")
    appwrite_api_key = env_current.get("APPWRITE_API_KEY", "")
    appwrite_database_id = env_current.get("APPWRITE_DATABASE_ID", "classly_db")
    automigrate_to = env_current.get("AUTOMIGRATE_TO", "")
    secret_key = env_current.get("SECRET_KEY", "")
    timezone = env_current.get("TZ", "Europe/Berlin")

    if is_advanced:
        appwrite = _ask_confirm("Use Appwrite backend?", default=appwrite)
        if appwrite:
            database_url = _ask_text("DATABASE_URL:", default=database_url)
            appwrite_endpoint = _ask_text("APPWRITE_ENDPOINT:", default=appwrite_endpoint)
            appwrite_project_id = _ask_text("APPWRITE_PROJECT_ID:", default=appwrite_project_id)
            appwrite_api_key = _ask_text("APPWRITE_API_KEY:", default=appwrite_api_key)
            appwrite_database_id = _ask_text("APPWRITE_DATABASE_ID:", default=appwrite_database_id)
            automigrate_to = _ask_select("AUTOMIGRATE_TO:", ["", "appwrite"], default=automigrate_to or "")
        else:
            database_url = _ask_text("DATABASE_URL:", default="sqlite:////data/classly.db")
            appwrite_endpoint = ""
            appwrite_project_id = ""
            appwrite_api_key = ""
            appwrite_database_id = "classly_db"
            automigrate_to = ""

        secret_key = _ask_text("SECRET_KEY (optional):", default=secret_key)
        timezone = _ask_text("TZ:", default=timezone)
    else:
        if appwrite:
            automigrate_to = "appwrite"

    return WizardConfig(
        target=target,
        port=port,
        max_classes=max_classes,
        migrate_from_domain=migrate_from,
        migrate_to_domain=migrate_to,
        database_url=database_url,
        appwrite=appwrite,
        appwrite_endpoint=appwrite_endpoint,
        appwrite_project_id=appwrite_project_id,
        appwrite_api_key=appwrite_api_key,
        appwrite_database_id=appwrite_database_id,
        automigrate_to=automigrate_to,
        secret_key=secret_key,
        timezone=timezone,
    )


def apply_plan(
    config: WizardConfig,
    compose_file: Path,
    env_file: Path,
    preview_only: bool,
    yes: bool,
) -> None:
    before_env = _load_text(env_file)
    before_compose = _load_text(compose_file)

    env_updates = _compute_env_updates(config)
    after_env = _render_env_with_updates(before_env, env_updates)

    target = _normalize_target(config.target, compose_file)
    after_compose = patch_compose_content(before_compose, config, target, env_file.as_posix())

    env_diff = _preview_diff(env_file, before_env, after_env)
    compose_diff = _preview_diff(compose_file, before_compose, after_compose)

    print("\n=== Preview ===")
    if env_diff.strip():
        print(env_diff)
    else:
        print(f"No changes for {env_file}")
    print("")
    if compose_diff.strip():
        print(compose_diff)
    else:
        print(f"No changes for {compose_file}")
    print("")

    if preview_only:
        return

    if not yes and not _ask_confirm("Apply these changes now?", default=True):
        print("Aborted. No files changed.")
        return

    backup_dir = _create_backup([env_file, compose_file])
    _write_text(env_file, after_env)
    _write_text(compose_file, after_compose)
    print(f"Changes applied. Backup stored at: {backup_dir}")


def command_wizard(args: argparse.Namespace, mode: str) -> None:
    compose_file = Path(args.compose_file)
    env_file = Path(args.env_file)
    target = _normalize_target(args.target, compose_file)

    if target not in {"normal", "coolify"}:
        _die("target must be 'normal' or 'coolify'")

    env_current = _parse_env_lines(_load_text(env_file))
    config = collect_config(mode=mode, target=target, env_current=env_current)
    errors = _validate_config(config)
    if errors:
        for err in errors:
            print(f"- {err}")
        _die("Configuration validation failed.")

    apply_plan(config, compose_file, env_file, preview_only=args.preview, yes=args.yes)


def command_validate(args: argparse.Namespace) -> None:
    compose_file = Path(args.compose_file)
    env_file = Path(args.env_file)
    target = _normalize_target(args.target, compose_file)

    env_current = _parse_env_lines(_load_text(env_file))
    config = WizardConfig(
        target=target,
        port=int(env_current.get("PORT", "8000") or "8000"),
        max_classes=env_current.get("MAX_CLASSES", ""),
        migrate_from_domain=env_current.get("MIGRATE_FROM_DOMAIN", ""),
        migrate_to_domain=env_current.get("MIGRATE_TO_DOMAIN", ""),
        database_url=env_current.get("DATABASE_URL", "sqlite:////data/classly.db"),
        appwrite=env_current.get("APPWRITE", "false").lower() == "true",
        appwrite_endpoint=env_current.get("APPWRITE_ENDPOINT", ""),
        appwrite_project_id=env_current.get("APPWRITE_PROJECT_ID", ""),
        appwrite_api_key=env_current.get("APPWRITE_API_KEY", ""),
        appwrite_database_id=env_current.get("APPWRITE_DATABASE_ID", "classly_db"),
        automigrate_to=env_current.get("AUTOMIGRATE_TO", ""),
        secret_key=env_current.get("SECRET_KEY", ""),
        timezone=env_current.get("TZ", "Europe/Berlin"),
    )
    errors = _validate_config(config)
    # Structural/dependency errors are printed and raised by patch_compose_content.
    patch_compose_content(_load_text(compose_file), config, target, env_file.as_posix())

    if errors:
        print("Validation failed:")
        for err in errors:
            print(f"- {err}")
        raise SystemExit(1)

    print("Validation OK.")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Classly interactive setup/configuration CLI for Docker hosting."
    )
    parser.add_argument("--compose-file", default=DEFAULT_COMPOSE_FILE)
    parser.add_argument("--env-file", default=DEFAULT_ENV_FILE)
    parser.add_argument("--target", default="", help="normal|coolify (auto if omitted)")
    parser.add_argument("--yes", action="store_true", help="Skip apply confirmation.")
    parser.add_argument("--preview", action="store_true", help="Show diff only.")

    sub = parser.add_subparsers(dest="command")

    sub.add_parser("wizard", help="Interactive wizard (asks mode first).")
    sub.add_parser("quick", help="Quick mode wizard.")
    sub.add_parser("advanced", help="Advanced mode wizard.")
    sub.add_parser("validate", help="Validate current env/compose config.")
    sub.add_parser("preview", help="Alias of quick with --preview.")

    restore = sub.add_parser("restore", help="Restore files from backup snapshot directory.")
    restore.add_argument("--backup", required=True, help="Backup directory path.")

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    cmd = args.command or "wizard"

    if cmd == "restore":
        _restore_backup(Path(args.backup))
        return

    if cmd == "validate":
        command_validate(args)
        return

    if cmd == "preview":
        args.preview = True
        command_wizard(args, mode="quick")
        return

    if cmd == "quick":
        command_wizard(args, mode="quick")
        return

    if cmd == "advanced":
        command_wizard(args, mode="advanced")
        return

    mode = _ask_select("Choose mode:", ["quick", "advanced"], default="quick")
    command_wizard(args, mode=mode)


if __name__ == "__main__":
    main()
