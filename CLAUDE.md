# Repo guide for Claude

This repo is a **Claude Code plugin marketplace** (`.claude-plugin/marketplace.json`). It indexes Teradata-related skills — some live in their own repos, two live here under `skills/`.

## Adding a new local skill

A local skill is a **self-contained directory** that gets exposed as its own marketplace entry via `git-subdir`. Layout:

```
skills/<name>/                           ← git-subdir plugin root
├── .claude-plugin/
│   └── plugin.json                      ← at the plugin root
├── README.md                            ← optional plugin-level intro
└── skills/
    └── <name>/                          ← the skill PACKAGE — everything in here ships together
        ├── SKILL.md                     ← frontmatter declares the skill
        ├── references/                  ← whatever the skill needs at runtime
        ├── templates/                   ← lives with SKILL.md, not above it
        ├── scripts/
        └── ...
```

**Key principle**: `SKILL.md` and every file the skill loads at runtime (references, templates, scripts, assets, demos) MUST be siblings inside `skills/<name>/`. The skill package = that directory. Don't put content next to `.claude-plugin/` at the plugin root — the runtime can't reach it from `SKILL.md`'s relative paths and it's not part of the published skill.

Then add a marketplace entry to `.claude-plugin/marketplace.json`:

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

And add a row to `README.md`'s Available Skills table.

## Why the double `<name>`

- `git-subdir` resolves `skills/<name>` as the plugin root.
- Inside the plugin root, the loader expects `.claude-plugin/plugin.json` and walks `skills/<skill-name>/SKILL.md` (same convention as the standalone repo `remi-td/teradata-sql-analytics`).
- So the on-disk path is `skills/<name>/skills/<name>/SKILL.md`. The outer `<name>` is the plugin directory; the inner `<name>` is the skill name inside that plugin.
- This is the **only** layout we've found that registers the skill. SKILL.md at the plugin root alone, or `plugin.json` one level above the git-subdir path, both silently produce `0 skills` on reload.

## Reference: `remi-td/teradata-sql-analytics`

The canonical working example (standalone repo, not git-subdir):

```
teradata-sql-analytics/                   ← repo root = plugin root
├── .claude-plugin/plugin.json
└── skills/
    └── teradata-sql-analytics/           ← skill package
        ├── SKILL.md
        ├── README.md
        └── syntax/                       ← skill content, alongside SKILL.md
```

Our git-subdir skills mirror this — the only difference is that the plugin root is a subdirectory of this repo instead of a repo root.

## Verifying a new skill before declaring victory

1. **Confirm everything is staged.** Untracked subdirectories are easy to miss with `git add <file>` — use `git status` and `git ls-files skills/<name>/` to confirm `SKILL.md` and all content files are tracked.
2. **Push, then check the GitHub web UI.** Confirm `skills/<name>/.claude-plugin/plugin.json` and `skills/<name>/skills/<name>/SKILL.md` exist at those exact paths on the remote.
3. **In a fresh session**: install via `/plugin`, then `/reload-plugins`. The reload line must say `N plugins · N skills` with skill count incremented. `0 skills` = layout still wrong.
4. The skill should appear in the system-reminder skills list as `<name>:<name>`.

## Don'ts

- **Don't put content (references/, templates/, etc.) at the plugin root** — they belong inside `skills/<name>/` next to SKILL.md so they're part of the published skill package.
- **Don't bundle multiple skills under one marketplace entry** — even with a working `plugin.json` at the repo root, they appear as a single installable item in the marketplace. Use one git-subdir entry per skill.
- **Don't trust `ls` alone** — `git ls-files` is what gets pushed.
