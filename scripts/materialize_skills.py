#!/usr/bin/env python3
"""Materialize marketplace skills into a flat SKILL.md directory tree.

This script reads the repository's canonical marketplace manifest, resolves each
skill source, clones or updates external repositories, and writes a clean
`skills/<skill-name>/` tree that runtimes such as Hermes can load directly.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

DEFAULT_MANIFEST = ".claude-plugin/marketplace.json"
DEFAULT_OUT_DIR = "~/.local/share/teradata-skills/hermes/skills"
DEFAULT_CACHE_DIR = "~/.cache/teradata-skills/repos"
SKIP_DIR_NAMES = {
    ".git",
    ".hg",
    ".svn",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    "__pycache__",
    "node_modules",
}


@dataclass
class MaterializedSkill:
    name: str
    description: str
    source_type: str
    source_url: str
    source_ref: str
    source_commit: str
    source_path: str
    skill_path: str
    output_path: str
    mode: str


def eprint(*args: object) -> None:
    print(*args, file=sys.stderr)


def run(cmd: list[str], cwd: Path | None = None, quiet: bool = False) -> str:
    proc = subprocess.run(
        cmd,
        cwd=str(cwd) if cwd else None,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if proc.returncode != 0:
        raise RuntimeError(
            f"Command failed ({proc.returncode}): {' '.join(cmd)}\n"
            f"cwd={cwd or Path.cwd()}\nstdout={proc.stdout}\nstderr={proc.stderr}"
        )
    if not quiet and proc.stderr.strip():
        eprint(proc.stderr.rstrip())
    return proc.stdout.strip()


def expand_path(value: str, base: Path | None = None) -> Path:
    expanded = os.path.expandvars(os.path.expanduser(value))
    path = Path(expanded)
    if not path.is_absolute() and base is not None:
        path = base / path
    return path.resolve()


def slugify_repo(url_or_repo: str) -> str:
    raw = url_or_repo.strip()
    if raw.endswith(".git"):
        raw = raw[:-4]
    if raw.startswith("git@"):
        raw = raw.split(":", 1)[-1]
    elif raw.startswith(("http://", "https://")):
        parsed = urlparse(raw)
        raw = parsed.path.strip("/")
    raw = raw.strip("/")
    return re.sub(r"[^A-Za-z0-9_.-]+", "__", raw)


def repo_url_from_source(source: dict[str, Any], repo_root: Path) -> tuple[str | None, str | None, str, str]:
    """Return (clone_url, repo_label, source_type, ref)."""
    source_type = str(source.get("source") or source.get("type") or "").strip()
    ref = str(source.get("ref") or "").strip()

    if source_type == "local":
        return None, str(repo_root), source_type, ref

    if source_type == "github":
        repo = source.get("repo")
        if not isinstance(repo, str) or "/" not in repo:
            raise ValueError(f"github source requires repo owner/name: {source}")
        return f"https://github.com/{repo}.git", repo, source_type, ref

    if source_type in {"git-subdir", "url"}:
        url = source.get("url")
        if not isinstance(url, str) or not url:
            raise ValueError(f"{source_type} source requires url: {source}")
        return url, slugify_repo(url).replace("__", "/", 1), source_type, ref

    raise ValueError(f"Unsupported source type {source_type!r}: {source}")


def is_current_repo(clone_url: str, repo_root: Path) -> bool:
    if not (repo_root / ".git").is_dir():
        return False
    try:
        origin = run(["git", "config", "--get", "remote.origin.url"], cwd=repo_root, quiet=True)
    except Exception:
        return False
    return bool(origin) and slugify_repo(origin).lower() == slugify_repo(clone_url).lower()


def checkout_repo(clone_url: str, cache_dir: Path, ref: str, update: bool) -> tuple[Path, str]:
    repo_dir = cache_dir / slugify_repo(clone_url)
    cache_dir.mkdir(parents=True, exist_ok=True)

    if repo_dir.exists() and not (repo_dir / ".git").is_dir():
        raise RuntimeError(f"Cache path exists but is not a git repo: {repo_dir}")

    if not repo_dir.exists():
        eprint(f"clone {clone_url}")
        run(["git", "clone", clone_url, str(repo_dir)], quiet=True)
    elif update:
        eprint(f"update {clone_url}")
        run(["git", "fetch", "--all", "--tags", "--prune"], cwd=repo_dir, quiet=True)

    if ref:
        # Prefer the remote branch when it exists, otherwise allow tags/SHAs.
        remote_ref = run(["git", "rev-parse", "--verify", f"origin/{ref}"], cwd=repo_dir, quiet=True) if ref_exists(repo_dir, f"origin/{ref}") else ""
        if remote_ref:
            run(["git", "checkout", "-B", ref, f"origin/{ref}"], cwd=repo_dir, quiet=True)
            if update:
                run(["git", "pull", "--ff-only", "origin", ref], cwd=repo_dir, quiet=True)
        else:
            run(["git", "checkout", ref], cwd=repo_dir, quiet=True)
    elif update:
        # Stay on the current default branch and fast-forward when possible.
        branch = run(["git", "branch", "--show-current"], cwd=repo_dir, quiet=True)
        if branch:
            run(["git", "pull", "--ff-only"], cwd=repo_dir, quiet=True)

    commit = run(["git", "rev-parse", "HEAD"], cwd=repo_dir, quiet=True)
    return repo_dir, commit


def ref_exists(repo_dir: Path, ref: str) -> bool:
    proc = subprocess.run(["git", "rev-parse", "--verify", ref], cwd=repo_dir, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return proc.returncode == 0


def parse_frontmatter_name(skill_md: Path) -> str | None:
    try:
        text = skill_md.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None
    if not text.startswith("---"):
        return None
    end = re.search(r"\n---\s*\n", text[3:])
    if not end:
        return None
    yaml_text = text[3 : end.start() + 3]
    for line in yaml_text.splitlines():
        match = re.match(r"\s*name\s*:\s*['\"]?([^'\"#]+)", line)
        if match:
            return match.group(1).strip()
    return None


def candidate_skill_dirs(plugin: dict[str, Any], source_root: Path, repo_root: Path) -> list[Path]:
    name = str(plugin.get("name") or "").strip()
    candidates: list[Path] = []

    # Optional future-proof metadata for this materializer. It is ignored by
    # Claude/Codex/Cursor, but lets this script avoid recursive discovery.
    for key in ("skill", "hermes"):
        value = plugin.get(key)
        if isinstance(value, dict) and isinstance(value.get("path"), str):
            p = value["path"]
            candidates.append(expand_path(p, repo_root if not Path(p).is_absolute() else None))
            candidates.append(source_root / p)

    skills_value = plugin.get("skills")
    if isinstance(skills_value, str):
        p = skills_value.strip()
        candidates.append(source_root / p / name)
        candidates.append(source_root / p)

    candidates.extend([
        source_root,
        source_root / "skills" / name,
        source_root / name,
    ])

    # Preserve order and remove duplicates.
    out: list[Path] = []
    seen: set[Path] = set()
    for c in candidates:
        try:
            resolved = c.resolve()
        except OSError:
            resolved = c
        if resolved not in seen:
            seen.add(resolved)
            out.append(resolved)
    return out


def find_skill_dir(plugin: dict[str, Any], source_root: Path, repo_root: Path) -> Path:
    name = str(plugin.get("name") or "").strip()
    if not name:
        raise ValueError(f"Plugin missing name: {plugin}")

    for candidate in candidate_skill_dirs(plugin, source_root, repo_root):
        if (candidate / "SKILL.md").is_file():
            return candidate

    matches: list[Path] = []
    for skill_md in source_root.rglob("SKILL.md"):
        if any(part in SKIP_DIR_NAMES for part in skill_md.parts):
            continue
        parent = skill_md.parent
        fm_name = parse_frontmatter_name(skill_md)
        if parent.name == name or fm_name == name:
            matches.append(parent)

    if len(matches) == 1:
        return matches[0]
    if len(matches) > 1:
        match_list = "\n  ".join(str(m) for m in matches)
        raise RuntimeError(f"Multiple SKILL.md directories match {name}; add skill.path metadata:\n  {match_list}")

    raise FileNotFoundError(f"Could not find SKILL.md for {name} under {source_root}")


def ignore_for_copy(_dir: str, names: list[str]) -> set[str]:
    ignored = {n for n in names if n in SKIP_DIR_NAMES}
    ignored.update(n for n in names if n.endswith((".pyc", ".pyo")))
    return ignored


def copy_or_link_skill(skill_dir: Path, dest: Path, mode: str) -> None:
    if dest.exists() or dest.is_symlink():
        if dest.is_symlink() or dest.is_file():
            dest.unlink()
        else:
            shutil.rmtree(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    if mode == "symlink":
        dest.symlink_to(skill_dir, target_is_directory=True)
    else:
        shutil.copytree(skill_dir, dest, ignore=ignore_for_copy, symlinks=False)


def load_manifest(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    plugins = data.get("plugins")
    if not isinstance(plugins, list):
        raise ValueError(f"Manifest must contain a plugins array: {path}")
    return data


def source_root_for_plugin(
    plugin: dict[str, Any], repo_root: Path, cache_dir: Path, update: bool
) -> tuple[Path, str, str, str, str]:
    source = plugin.get("source")
    if not isinstance(source, dict):
        raise ValueError(f"Plugin source must be an object: {plugin.get('name')}")

    clone_url, repo_label, source_type, ref = repo_url_from_source(source, repo_root)
    source_path = str(source.get("path") or "").strip().lstrip("./")

    if clone_url is None:
        base = repo_root
        commit = run(["git", "rev-parse", "HEAD"], cwd=repo_root, quiet=True) if (repo_root / ".git").is_dir() else ""
        source_url = str(repo_root)
    elif is_current_repo(clone_url, repo_root):
        # When developing this marketplace locally, self-referential manifest
        # entries should use the checkout under test rather than recloning the
        # default branch from GitHub.
        base = repo_root
        commit = run(["git", "rev-parse", "HEAD"], cwd=repo_root, quiet=True)
        source_url = clone_url
    else:
        base, commit = checkout_repo(clone_url, cache_dir, ref, update=update)
        source_url = clone_url

    root = (base / source_path).resolve() if source_path else base.resolve()
    if not root.exists():
        raise FileNotFoundError(f"Source path does not exist for {plugin.get('name')}: {root}")
    return root, source_type, source_url, ref, commit


def materialize(args: argparse.Namespace) -> list[MaterializedSkill]:
    repo_root = expand_path(args.repo_root)
    manifest_path = expand_path(args.manifest, repo_root)
    cache_dir = expand_path(args.cache_dir)
    out_dir = expand_path(args.out_dir)
    mode = args.mode

    manifest = load_manifest(manifest_path)
    plugins = manifest["plugins"]
    if args.only:
        wanted = {p.strip() for p in args.only.split(",") if p.strip()}
        plugins = [p for p in plugins if p.get("name") in wanted]

    tmp_parent = out_dir.parent
    tmp_parent.mkdir(parents=True, exist_ok=True)
    tmp_dir = Path(tempfile.mkdtemp(prefix=f".{out_dir.name}.tmp-", dir=str(tmp_parent)))
    lock_entries: list[MaterializedSkill] = []

    try:
        for plugin in plugins:
            name = str(plugin.get("name") or "").strip()
            if not name:
                raise ValueError(f"Plugin missing name: {plugin}")
            if args.exclude_mcp and "mcpServers" in json.dumps(plugin):
                eprint(f"skip {name}: MCP server plugin")
                continue

            source_root, source_type, source_url, source_ref, source_commit = source_root_for_plugin(
                plugin, repo_root=repo_root, cache_dir=cache_dir, update=args.update
            )
            skill_dir = find_skill_dir(plugin, source_root=source_root, repo_root=repo_root)
            dest = tmp_dir / name
            eprint(f"materialize {name}: {skill_dir} -> {dest}")
            copy_or_link_skill(skill_dir, dest, mode=mode)
            if not (dest / "SKILL.md").is_file():
                raise RuntimeError(f"Materialized skill is missing SKILL.md: {dest}")

            lock_entries.append(MaterializedSkill(
                name=name,
                description=str(plugin.get("description") or ""),
                source_type=source_type,
                source_url=source_url,
                source_ref=source_ref,
                source_commit=source_commit,
                source_path=str(source_root),
                skill_path=str(skill_dir),
                output_path=str((out_dir / name).resolve()),
                mode=mode,
            ))

        lock = {
            "version": 1,
            "manifest": str(manifest_path),
            "marketplace": manifest.get("name"),
            "mode": mode,
            "skills": [asdict(entry) for entry in lock_entries],
        }
        (tmp_dir / ".teradata-skills.lock.json").write_text(json.dumps(lock, indent=2) + "\n", encoding="utf-8")

        backup_dir = None
        if out_dir.exists() or out_dir.is_symlink():
            backup_dir = out_dir.with_name(f".{out_dir.name}.prev")
            if backup_dir.exists() or backup_dir.is_symlink():
                if backup_dir.is_symlink() or backup_dir.is_file():
                    backup_dir.unlink()
                else:
                    shutil.rmtree(backup_dir)
            out_dir.rename(backup_dir)
        try:
            tmp_dir.rename(out_dir)
        except Exception:
            if backup_dir and backup_dir.exists() and not out_dir.exists():
                backup_dir.rename(out_dir)
            raise
        if backup_dir and backup_dir.exists():
            shutil.rmtree(backup_dir)
    except Exception:
        if tmp_dir.exists():
            shutil.rmtree(tmp_dir)
        raise

    return lock_entries


def print_status(out_dir: Path) -> int:
    lock_path = out_dir / ".teradata-skills.lock.json"
    if not lock_path.is_file():
        print(f"No materialized skill tree found at {out_dir}")
        return 1
    data = json.loads(lock_path.read_text(encoding="utf-8"))
    print(f"Materialized skills at: {out_dir}")
    for skill in data.get("skills", []):
        print(f"- {skill.get('name')} ({skill.get('source_commit', '')[:12]}) -> {skill.get('output_path')}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", nargs="?", choices=["install", "update", "status", "list"], default="install")
    parser.add_argument("--repo-root", default=str(Path(__file__).resolve().parents[1]), help="Path to this marketplace checkout")
    parser.add_argument("--manifest", default=DEFAULT_MANIFEST, help="Marketplace manifest to read")
    parser.add_argument("--cache-dir", default=DEFAULT_CACHE_DIR, help="Directory for cloned source repositories")
    parser.add_argument("--out-dir", default=DEFAULT_OUT_DIR, help="Output directory containing flat skills/<name>/ folders")
    parser.add_argument("--mode", choices=["copy", "symlink"], default="copy", help="Copy skills or symlink to source directories")
    parser.add_argument("--only", default="", help="Comma-separated skill names to materialize")
    parser.add_argument("--exclude-mcp", action="store_true", default=True, help="Skip MCP-only plugins if present")
    parser.add_argument("--no-exclude-mcp", action="store_false", dest="exclude_mcp", help="Do not skip MCP-only plugins")
    parser.add_argument("--update", action="store_true", help="Fetch/pull existing cloned repositories before materializing")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON summary")
    args = parser.parse_args(argv)

    out_dir = expand_path(args.out_dir)
    if args.command == "status":
        return print_status(out_dir)
    if args.command == "list":
        manifest_path = expand_path(args.manifest, expand_path(args.repo_root))
        data = load_manifest(manifest_path)
        for plugin in data["plugins"]:
            print(plugin.get("name"))
        return 0
    if args.command == "update":
        args.update = True

    entries = materialize(args)
    if args.json:
        print(json.dumps([asdict(e) for e in entries], indent=2))
    else:
        print(f"Materialized {len(entries)} skill(s) into {out_dir}")
        for entry in entries:
            print(f"- {entry.name}: {entry.output_path}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        eprint(f"error: {exc}")
        raise SystemExit(1)
