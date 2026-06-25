#!/usr/bin/env python3
"""Add a materialized skills directory to Hermes `skills.external_dirs`.

The script is intentionally conservative: it only edits config.yaml through
PyYAML. If PyYAML is not available, it prints the exact snippet to add instead
of trying to hand-edit arbitrary YAML.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
from typing import Any


def default_config_path() -> Path:
    hermes_home = os.environ.get("HERMES_HOME")
    if hermes_home:
        return Path(hermes_home).expanduser() / "config.yaml"
    return Path.home() / ".hermes" / "config.yaml"


def load_yaml_module():
    try:
        import yaml  # type: ignore
    except Exception:
        return None
    return yaml


def configure(config_path: Path, skills_dir: Path) -> bool:
    yaml = load_yaml_module()
    if yaml is None:
        print(
            "PyYAML is not available; add this to Hermes config manually:\n\n"
            "skills:\n"
            "  external_dirs:\n"
            f"    - {skills_dir}\n",
            file=sys.stderr,
        )
        return False

    config_path.parent.mkdir(parents=True, exist_ok=True)
    if config_path.exists():
        with config_path.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
    else:
        data = {}

    if not isinstance(data, dict):
        raise ValueError(f"Hermes config must be a YAML mapping: {config_path}")

    skills_cfg: dict[str, Any]
    raw_skills = data.get("skills")
    if isinstance(raw_skills, dict):
        skills_cfg = raw_skills
    elif raw_skills is None:
        skills_cfg = {}
        data["skills"] = skills_cfg
    else:
        raise ValueError("Existing `skills` config is not a mapping; refusing to edit")

    raw_dirs = skills_cfg.get("external_dirs")
    if raw_dirs is None:
        external_dirs: list[str] = []
    elif isinstance(raw_dirs, list):
        external_dirs = [str(p) for p in raw_dirs]
    elif isinstance(raw_dirs, str):
        external_dirs = [raw_dirs]
    else:
        raise ValueError("Existing `skills.external_dirs` is not a list or string; refusing to edit")

    skills_dir_str = str(skills_dir)
    normalized_existing = {str(Path(os.path.expanduser(os.path.expandvars(p))).resolve()) for p in external_dirs}
    if str(skills_dir.resolve()) not in normalized_existing:
        external_dirs.append(skills_dir_str)
        skills_cfg["external_dirs"] = external_dirs
        with config_path.open("w", encoding="utf-8") as f:
            yaml.safe_dump(data, f, sort_keys=False)
        return True
    return False


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("skills_dir", help="Materialized flat skills directory")
    parser.add_argument("--config", default=str(default_config_path()), help="Hermes config.yaml path")
    args = parser.parse_args(argv)

    skills_dir = Path(args.skills_dir).expanduser().resolve()
    config_path = Path(args.config).expanduser().resolve()
    changed = configure(config_path, skills_dir)
    if changed:
        print(f"Added {skills_dir} to {config_path}")
    else:
        print(f"Hermes config already includes {skills_dir} or manual update is required")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(1)
