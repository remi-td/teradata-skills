# Teradata Skills

A multi-framework skill marketplace aggregating Teradata-related skills maintained across multiple repositories. Install once, get all skills — in Claude Code, Codex, GitHub Copilot, or Cursor.

## Installation

### Claude Code

Add the marketplace in any Claude Code session:

```
/plugin marketplace add remi-td/teradata-skills
```

Then pick the skills you want:

```
/plugin list
```

Restart Claude Code to activate.

### Codex

Add this marketplace from the Codex CLI:

```
codex plugin marketplace add remi-td/teradata-skills
```

For a local checkout while developing this repository:

```
codex plugin marketplace add ./local/path/to/teradata-skills
```

Then list and install the available plugins:

```
codex plugin list --available
codex plugin add teradata-sql-jupyter@teradata-skills
```

Restart Codex or start a new thread after installing a plugin.

**From VS Code GUI:** Settings → Plugins → Add More → enter `remi-td/teradata-skills` in the Source field → select the skills you want to install.

### Cursor

Add the marketplace in Cursor settings (**Settings → Plugins → Add marketplace**) and enter:

```
https://github.com/remi-td/teradata-skills
```

Cursor will discover the `.cursor-plugin/marketplace.json` manifest and list the available skills. Toggle on the skills you want and reload the agent.

### GitHub Copilot — VS Code GUI

1. Open VS Code and press `Ctrl+Shift+P` (macOS: `Cmd+Shift+P`) to open the Command Palette.
2. Run **"GitHub Copilot: Manage Extensions"** (or open the **Extensions** view and search for *Copilot Extensions*).
3. Click **Add extension source** and enter this repository URL:
   ```
   https://github.com/remi-td/teradata-skills
   ```
4. VS Code will discover the marketplace manifest and list the available skills.
5. Toggle on the skills you want and reload the Copilot agent.

> **Codex note.**
> Codex uses `.agents/plugins/marketplace.json`.
> External skill code is not copied into this repository. Root-level external repositories use Codex's `url` source, while external plugin subdirectories use `git-subdir`.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for the full workflow to add or update skills and MCP server plugins across Claude Code, Codex, Cursor, and VS Code agent surfaces.

## Available Skills

| Skill | Description | Source | Claude Code | Codex | GitHub Copilot | Cursor |
|-------|-------------|--------|:-----------:|:-----:|:--------------:|:------:|
| `teradata-query` | Install, configure, and use the [tq CLI](https://github.com/remi-td/tq) to run Teradata queries, explore schemas, monitor sessions, and manage database objects from the command line. | [remi-td/tq](https://github.com/remi-td/tq/tree/master/agentic) | ✅ | ✅ | ✅ | ✅ |
| `teradata-sql-analytics` | Teradata native function guidelines and syntax — load at the start of any Teradata analytics session. | [ksturgeon-td/tdsql-mcp](https://github.com/ksturgeon-td/tdsql-mcp) | ✅ | ✅ | ✅ | ✅ |
| `teradata-visual-explain` | Decode and visualise Teradata EXPLAIN output. | [Pibbers/teradata-visual-explain-skill](https://github.com/Pibbers/teradata-visual-explain-skill) | ✅ | ✅ | ✅ | ⚠️ |
| `teradata-react` | Scaffold, develop, and deploy a production-shaped React + FastAPI web application backed by Teradata Vantage. Covers project layout, connection pooling, query patterns, theming/branding, security, and deployment. | [skills/teradata-react](skills/teradata-react) *(this repo)* | ✅ | ✅ | ✅ | ✅ |
| `teradata-sql-jupyter` | Author Teradata SQL Jupyter notebooks for exploratory data analytics, teaching, demos, and interactive SQL user guides. Also assists with installing and running the Teradata Jupyter SQL extensions. | [skills/teradata-sql-jupyter](skills/teradata-sql-jupyter) *(this repo)* | ✅ | ✅ | ✅ | ✅ |
| `teradata-mcp-customisation` | Build, edit, and debug a semantic layer for the Teradata MCP server — custom tools, cubes, prompts, and glossary entries declared in YAML, plus the `profiles.yml` that exposes them. | [Teradata/teradata-mcp-server](https://github.com/Teradata/teradata-mcp-server/tree/main/agentic) | ✅ | ✅ | ✅ | ✅ |
| `teradata-trial-data-loading` | Discover and load demo or sample datasets into a Teradata Trial environment. | [ksturgeon-td/teradata-trial-data-loading](https://github.com/ksturgeon-td/teradata-trial-data-loading) | ✅ | ✅ | ✅ | ✅ |

> ⚠️ for Cursor = skill lives in a subdirectory of an external repo with no root-level `plugin.json`; install by adding [Pibbers/teradata-visual-explain-skill](https://github.com/Pibbers/teradata-visual-explain-skill) as a separate Cursor marketplace source.

## Available MCP Server Plugins

| Plugin | Description | Source | Codex |
|--------|-------------|--------|:-----:|
| `teradata-mcp-server` | Connect Codex to Teradata Vantage through the Teradata MCP server. Requires `uvx` and a local `DATABASE_URI` environment variable. | [Teradata/teradata-mcp-server](https://github.com/Teradata/teradata-mcp-server) | ✅ |

Install it from Codex after adding this marketplace:

```bash
codex plugin add teradata-mcp-server@teradata-skills
```

Then set `DATABASE_URI` in the environment where Codex runs:

```bash
export DATABASE_URI="teradata://USERNAME:PASSWORD@HOST:1025/DATABASE"
```

## How it works

Skills and MCP servers are maintained alongside the projects they relate to. This repo acts as a marketplace index and does not copy external code into the Codex marketplace.

- `.agents/plugins/marketplace.json` is the Codex marketplace manifest.
- Local Codex plugins point to `skills/<name>` in this repo and include `skills/<name>/.codex-plugin/plugin.json`.
- External Codex plugins use `url` entries for root-level source repositories or `git-subdir` entries when the source repository exposes an installable plugin root below the repo root.
- Codex MCP server plugins can use a tiny local plugin bundle with `.codex-plugin/plugin.json`. If the server is launched with a package runner such as `uvx`, the bundle stores install metadata and links to the official source, while runtime code stays in the server package/source repository.

For root-level external repositories that do not carry `.codex-plugin/plugin.json`, the marketplace entry provides enough metadata for Codex to generate the install manifest while keeping the skill files in the source repository.
