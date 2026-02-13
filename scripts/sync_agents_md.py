from __future__ import annotations

from pathlib import Path


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]

    agents_path = repo_root / "AGENTS.md"
    if not agents_path.exists():
        raise FileNotFoundError(f"Missing {agents_path}")

    agents_bytes = agents_path.read_bytes()

    targets = [
        repo_root / "Claude.md",
        repo_root / "Gemini.md",
    ]

    changed = False
    for target in targets:
        before = target.read_bytes() if target.exists() else None
        if before != agents_bytes:
            target.write_bytes(agents_bytes)
            changed = True
            print(f"wrote: {target}")
        else:
            print(f"ok:    {target}")

    return 0 if changed else 0


if __name__ == "__main__":
    raise SystemExit(main())

