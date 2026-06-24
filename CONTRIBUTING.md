# Contributing Skills And MCP Plugins

This repository is a multi-framework marketplace index for Teradata agent skills and Codex MCP server plugins. It supports Claude Code, Codex, Cursor, and the VS Code agent surfaces that consume these marketplace manifests.

The main rule is simple: keep skill and server code in its source repository. Only skills maintained by this repository should live under `skills/`. External skills and MCP servers must be referenced by marketplace metadata, not copied here.

## Files To Update

When adding or changing a skill, update the files for every framework that should expose it:

| Framework | Marketplace file | Source style |
| --- | --- | --- |
| Claude Code | `.claude-plugin/marketplace.json` | `github` for repo roots, `git-subdir` for subdirectories |
| Codex | `.agents/plugins/marketplace.json` | `url` for repo roots, `git-subdir` for subdirectories, `local` for skills in this repo |
| Cursor | `.cursor-plugin/marketplace.json` | string paths or repository URLs |
| README | `README.md` | user-facing skill table and caveats |

Codex MCP server plugins are currently defined in `.agents/plugins/marketplace.json` and documented in `README.md`. Add Claude Code, Cursor, or VS Code entries only after verifying those frameworks support the same server configuration shape.

Local skills also need per-plugin manifests:

| Framework | Local manifest |
| --- | --- |
| Claude Code | `skills/<name>/.claude-plugin/plugin.json` |
| Codex | `skills/<name>/.codex-plugin/plugin.json` |
| Legacy/shared local manifest | `skills/<name>/plugin.json` |

## Skill Package Layout

Every skill package should keep `SKILL.md` and all files it reads at runtime together:

```text
skills/<plugin-name>/
├── .claude-plugin/
│   └── plugin.json
├── .codex-plugin/
│   └── plugin.json
├── plugin.json
└── skills/
    └── <skill-name>/
        ├── SKILL.md
        ├── references/
        ├── templates/
        ├── scripts/
        └── assets/
```

Do not place runtime references, templates, or scripts at the plugin root. Put them next to `SKILL.md` so relative paths work after installation.

## Add A Local Skill

Use this path when the skill is maintained in this repository.

1. Create the skill package:

```text
skills/teradata-example/
├── .claude-plugin/
│   └── plugin.json
├── .codex-plugin/
│   └── plugin.json
├── plugin.json
└── skills/
    └── teradata-example/
        └── SKILL.md
```

2. Add `skills/teradata-example/skills/teradata-example/SKILL.md`:

```markdown
---
name: teradata-example
description: Use when creating example Teradata workflows.
---

Follow this workflow when the user asks for an example Teradata task.
```

3. Add the Claude local plugin manifest at `skills/teradata-example/.claude-plugin/plugin.json`:

```json
{
  "name": "teradata-example",
  "description": "Create example Teradata workflows.",
  "version": "1.0.0"
}
```

4. Add the Codex local plugin manifest at `skills/teradata-example/.codex-plugin/plugin.json`:

```json
{
  "name": "teradata-example",
  "version": "1.0.0",
  "description": "Create example Teradata workflows.",
  "skills": "./skills/"
}
```

5. Add or update `skills/teradata-example/plugin.json`:

```json
{
  "name": "teradata-example",
  "version": "1.0.0",
  "description": "Create example Teradata workflows.",
  "skills": "./skills/"
}
```

6. Add a Claude Code marketplace entry in `.claude-plugin/marketplace.json`:

```json
{
  "name": "teradata-example",
  "description": "Create example Teradata workflows.",
  "source": {
    "source": "git-subdir",
    "url": "https://github.com/remi-td/teradata-skills.git",
    "path": "skills/teradata-example",
    "ref": "main"
  },
  "category": "development"
}
```

7. Add a Codex marketplace entry in `.agents/plugins/marketplace.json`:

```json
{
  "name": "teradata-example",
  "description": "Create example Teradata workflows.",
  "version": "1.0.0",
  "source": {
    "source": "local",
    "path": "./skills/teradata-example"
  },
  "policy": {
    "installation": "AVAILABLE",
    "authentication": "ON_INSTALL"
  },
  "interface": {
    "displayName": "Teradata Example"
  },
  "category": "Development"
}
```

8. Add a Cursor marketplace entry in `.cursor-plugin/marketplace.json`:

```json
{
  "name": "teradata-example",
  "description": "Create example Teradata workflows.",
  "source": "skills/teradata-example",
  "category": "development"
}
```

9. Add the skill to the table in `README.md`.

## Add An External Root Repository Skill

Use this path when the source repository root is the plugin root and contains `skills/<name>/SKILL.md`.

Example source layout:

```text
external-repo/
├── .claude-plugin/
│   └── plugin.json
└── skills/
    └── teradata-example/
        └── SKILL.md
```

Claude Code entry:

```json
{
  "name": "teradata-example",
  "description": "Create example Teradata workflows.",
  "source": {
    "source": "github",
    "repo": "example-org/teradata-example",
    "ref": "main"
  },
  "category": "development"
}
```

Codex entry:

```json
{
  "name": "teradata-example",
  "description": "Create example Teradata workflows.",
  "version": "1.0.0",
  "source": {
    "source": "url",
    "url": "https://github.com/example-org/teradata-example.git",
    "ref": "main"
  },
  "skills": "./skills/",
  "policy": {
    "installation": "AVAILABLE",
    "authentication": "ON_INSTALL"
  },
  "interface": {
    "displayName": "Teradata Example"
  },
  "category": "Development"
}
```

Cursor entry:

```json
{
  "name": "teradata-example",
  "description": "Create example Teradata workflows.",
  "source": "https://github.com/example-org/teradata-example",
  "category": "development"
}
```

Do not add a copy of the external skill under this repository's `skills/` directory.

## Add An External Subdirectory Skill

Use this path when the source repository stores the plugin under a subdirectory such as `agentic/`.

Example source layout:

```text
external-repo/
└── agentic/
    ├── .claude-plugin/
    │   └── plugin.json
    ├── .codex-plugin/
    │   └── plugin.json
    └── skills/
        └── teradata-example/
            └── SKILL.md
```

Claude Code entry:

```json
{
  "name": "teradata-example",
  "description": "Create example Teradata workflows.",
  "source": {
    "source": "git-subdir",
    "url": "https://github.com/example-org/example-project.git",
    "path": "agentic",
    "ref": "main"
  },
  "category": "development"
}
```

Codex entry:

```json
{
  "name": "teradata-example",
  "description": "Create example Teradata workflows.",
  "version": "1.0.0",
  "source": {
    "source": "git-subdir",
    "url": "https://github.com/example-org/example-project.git",
    "path": "agentic",
    "ref": "main"
  },
  "policy": {
    "installation": "AVAILABLE",
    "authentication": "ON_INSTALL"
  },
  "interface": {
    "displayName": "Teradata Example"
  },
  "category": "Development"
}
```

Cursor entry:

```json
{
  "name": "teradata-example",
  "description": "Create example Teradata workflows.",
  "source": "https://github.com/example-org/example-project",
  "category": "development"
}
```

If Cursor cannot resolve a subdirectory in the external repository, mark the README table with a caveat and document the separate install path.

## Add A Codex MCP Server Plugin

Use this path when a plugin exposes an MCP server, not just agent instructions. Do not copy the server code into this repository.

For servers launched through a package runner such as `uvx`, the marketplace `source` is still required by Codex, but it does not need to be the server source repository. Prefer a tiny local plugin bundle with a `.codex-plugin/plugin.json` manifest. That keeps the installable plugin metadata in this marketplace and the runtime server code in the package/source repository.

Create a tracked bundle such as:

```text
.agents/plugins/teradata-mcp-server/
├── .codex-plugin/
│   └── plugin.json
└── README.md
```

Marketplace entry:

```json
{
  "name": "teradata-mcp-server",
  "description": "Connect Codex to Teradata Vantage using the Teradata MCP server.",
  "version": "0.2.3",
  "source": {
    "source": "local",
    "path": "./.agents/plugins/teradata-mcp-server"
  },
  "policy": {
    "installation": "AVAILABLE",
    "authentication": "ON_USE"
  },
  "interface": {
    "displayName": "Teradata MCP Server",
    "shortDescription": "Connect Codex to Teradata Vantage through MCP.",
    "developerName": "Teradata",
    "category": "Development"
  },
  "category": "Development"
}
```

Plugin manifest at `.agents/plugins/teradata-mcp-server/.codex-plugin/plugin.json`:

```json
{
  "name": "teradata-mcp-server",
  "version": "0.2.3",
  "description": "Connect Codex to Teradata Vantage using the Teradata MCP server.",
  "mcpServers": {
    "teradataMCP": {
      "command": "uvx",
      "args": [
        "teradata-mcp-server"
      ],
      "env_vars": [
        "DATABASE_URI"
      ]
    }
  },
  "interface": {
    "displayName": "Teradata MCP Server",
    "shortDescription": "Connect Codex to Teradata Vantage through MCP.",
    "developerName": "Teradata",
    "category": "Development"
  },
  "category": "Development"
}
```

Use `env_vars` for values that must come from the user's local environment, especially credentials such as `DATABASE_URI`. Do not hard-code secrets or example credentials in the marketplace entry or plugin manifest.

After installation, verify Codex sees the server:

```bash
tmp_home=$(mktemp -d)
CODEX_HOME="$tmp_home" codex plugin marketplace add ./ >/dev/null
CODEX_HOME="$tmp_home" codex plugin add teradata-mcp-server@teradata-skills --json >/dev/null
CODEX_HOME="$tmp_home" codex mcp list --json
```

## Validation

Run these checks before opening a PR.

1. Validate JSON:

```bash
python3 -m json.tool .agents/plugins/marketplace.json >/dev/null
python3 -m json.tool .claude-plugin/marketplace.json >/dev/null
python3 -m json.tool .cursor-plugin/marketplace.json >/dev/null
find skills -path '*/.codex-plugin/plugin.json' -print0 | xargs -0 -n1 python3 -m json.tool >/dev/null
find skills -path '*/.claude-plugin/plugin.json' -print0 | xargs -0 -n1 python3 -m json.tool >/dev/null
find skills -maxdepth 2 -name plugin.json -print0 | xargs -0 -n1 python3 -m json.tool >/dev/null
```

2. Verify Codex marketplace listing and install in a clean temporary home:

```bash
tmp_home=$(mktemp -d)
CODEX_HOME="$tmp_home" codex plugin marketplace add ./
CODEX_HOME="$tmp_home" codex plugin list --available --json
CODEX_HOME="$tmp_home" codex plugin add teradata-example@teradata-skills --json
```

For an existing marketplace-wide check, install each plugin:

```bash
tmp_home=$(mktemp -d)
CODEX_HOME="$tmp_home" codex plugin marketplace add ./ >/dev/null
for plugin in teradata-query teradata-sql-analytics teradata-visual-explain teradata-react teradata-sql-jupyter teradata-mcp-customisation teradata-mcp-server teradata-trial-data-loading; do
  CODEX_HOME="$tmp_home" codex plugin add "$plugin@teradata-skills" --json >/dev/null
  echo "installed $plugin"
done
```

For MCP server plugins, also confirm the server registration appears:

```bash
CODEX_HOME="$tmp_home" codex mcp list --json
```

3. Confirm local files are tracked:

```bash
git status --short
git ls-files skills/teradata-example
```

4. For Claude Code and Cursor, verify in a fresh session after the branch is available remotely. These tools generally validate marketplace behavior after fetching from GitHub, so local-only checks are weaker than Codex's local marketplace install test.

## Common Mistakes

- Do not copy external skill code into this repository.
- Do not use Codex `"source": "github"`; use `"source": "url"` for repo roots.
- Do not use Codex `git-subdir` with `"path": "."`; root repositories use `url`.
- Do not put `references/`, `templates/`, `scripts/`, or `assets/` outside the skill package directory.
- Do not forget to update `README.md`; the table is the user-facing source of truth.
- Do not leave a marketplace entry that lists but fails to install in Codex.
- Do not put credentials in `mcpServers`; use `env_vars` so Codex reads them from the user's environment.
