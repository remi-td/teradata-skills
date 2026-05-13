# Repo guide for Claude

This repo is a **Claude Code plugin marketplace** (`.claude-plugin/marketplace.json`). It indexes Teradata-related skills — some live in their own repos, two live here under `skills/`.

## Adding a new local skill (the only structure that works)

A local skill must look exactly like this. The nesting is mandatory — see "Why the nesting" below.

```
skills/<name>/                           ← git-subdir plugin root
├── .claude-plugin/
│   └── plugin.json                      ← REQUIRED at plugin root
├── skills/
│   └── <name>/
│       └── SKILL.md                     ← REQUIRED at skills/<name>/SKILL.md
├── references/                          ← optional content
├── templates/
└── ...
```

Then add a marketplace entry in `.claude-plugin/marketplace.json`:

```json
{
  "name": "<name>",
  "description": "...",
  "source": {
    "source": "git-subdir",
    "url": "https://github.com/remi-td/teradata-skills.git",
    "path": "skills/<name>"
  },
  "category": "development"
}
```

And add a row in `README.md`'s Available Skills table.

## Why the nesting (`skills/<name>/skills/<name>/SKILL.md`)

- The plugin system resolves the `git-subdir` path as the **plugin root**.
- Inside the plugin root, it looks for `.claude-plugin/plugin.json` AND skills at `skills/<skill-name>/SKILL.md` (mirroring the layout in `remi-td/teradata-sql-analytics`).
- Our git-subdir path is `skills/<name>` (so each skill is its own installable marketplace entry). That makes `skills/<name>/` the plugin root, hence skills must live at `skills/<name>/skills/<name>/SKILL.md`.
- Putting SKILL.md at the plugin root, or putting plugin.json one level up from the git-subdir path, **silently fails** — the plugin loads but skill count stays at 0.

## Alternative: bundle multiple skills under one marketplace entry

Don't, unless you actually want a single installable item. We tried it (one `plugin.json` at repo root + one self-referencing marketplace entry) — it works mechanically but appears as one entry in the marketplace UI, not two. Users couldn't install/uninstall them independently.

## Verifying a new skill before declaring victory

1. `git status` and confirm **every file under `skills/<name>/`** is staged (untracked dirs are easy to miss).
2. After `git push`, check the GitHub web UI that `skills/<name>/.claude-plugin/plugin.json` and `skills/<name>/skills/<name>/SKILL.md` both exist at those exact paths.
3. In a fresh Claude Code session: `/plugin` → install `<name>` → `/reload-plugins`. The reload output must say **`N plugins · N skills`** with skill count > previous. "0 skills" means the layout is still wrong.
4. The skill should appear in the system-reminder skills list as `<name>:<name>`.

## Common failure modes we hit (don't repeat)

| Symptom | Cause |
|---|---|
| `Subdirectory 'X' not found in repository` on install | The `path` in marketplace.json exists locally but wasn't actually committed/pushed. Check `git ls-files`, not just `ls`. |
| `Reloaded: N plugins · 0 skills` | `plugin.json` is not at the plugin-root `.claude-plugin/plugin.json`, OR `SKILL.md` is not at `skills/<name>/SKILL.md` from the plugin root. |
| Two skills appear as one entry | Marketplace has one entry covering both. Use two `git-subdir` entries instead. |

## Layout reference (working examples in this repo)

- `skills/teradata-react/` and `skills/teradata-sql-jupyter/` — copy this exact structure.
- External working reference: `https://github.com/remi-td/teradata-sql-analytics` — same `skills/<name>/SKILL.md` convention, but as a standalone repo (no nesting because its plugin root IS the repo root).
