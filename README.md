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

**Update Config (eg. `~/.codex/config.toml`):**

Add:

```toml
[marketplaces.teradata-skills]
source_type = "git"
source = "https://github.com/remi-td/teradata-skills.git"
```
Restart Codex after editing the config.

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
4. VS Code will discover the `.codex-plugin/marketplace.json` manifest and list the available skills.
5. Toggle on the skills you want and reload the Copilot agent.

> **Caveat — skills loaded from this repo only.**
> The VS Code GUI reads the `.codex-plugin/` manifest in *this* repository. It will only load the skills **directly maintained here**:
> - `/teradata-react`
> - `/teradata-sql-jupyter`
> - `/teradata-mcp-customisation`
>
> The other skills in the table below (`/teradata-query`, `/teradata-sql-analytics`, `/teradata-visual-explain`) live in separate source repositories. To load those, navigate to the **Available Skills** table, follow each **Source** link, and add that repository as an additional extension source using the same steps above.

## Available Skills

| Skill | Description | Source | Claude Code | Codex | GitHub Copilot | Cursor |
|-------|-------------|--------|:-----------:|:-----:|:--------------:|:------:|
| `teradata-query` | Install, configure, and use the [tq CLI](https://github.com/remi-td/tq) to run Teradata queries, explore schemas, monitor sessions, and manage database objects from the command line. | [remi-td/tq](https://github.com/remi-td/tq/tree/master/agentic) | ✅ | ✅ | ✅ | ✅ |
| `teradata-sql-analytics` | Teradata native function guidelines and syntax — load at the start of any Teradata analytics session. | [remi-td/teradata-sql-analytics](https://github.com/remi-td/teradata-sql-analytics) | ✅ | ✅ | ✅ | ✅ |
| `teradata-visual-explain` | Decode and visualise Teradata EXPLAIN output. | [Pibbers/teradata-visual-explain-skill](https://github.com/Pibbers/teradata-visual-explain-skill) | ✅ | ✅ | ✅ | ⚠️ |
| `teradata-react` | Scaffold, develop, and deploy a production-shaped React + FastAPI web application backed by Teradata Vantage. Covers project layout, connection pooling, query patterns, theming/branding, security, and deployment. | [skills/teradata-react](skills/teradata-react) *(this repo)* | ✅ | ✅ | ✅ | ✅ |
| `teradata-sql-jupyter` | Author Teradata SQL Jupyter notebooks for exploratory data analytics, teaching, demos, and interactive SQL user guides. Also assists with installing and running the Teradata Jupyter SQL extensions. | [skills/teradata-sql-jupyter](skills/teradata-sql-jupyter) *(this repo)* | ✅ | ✅ | ✅ | ✅ |
| `teradata-mcp-customisation` | Build, edit, and debug a semantic layer for the Teradata MCP server — custom tools, cubes, prompts, and glossary entries declared in YAML, plus the `profiles.yml` that exposes them. | [Teradata/teradata-mcp-server](https://github.com/Teradata/teradata-mcp-server/tree/main/agentic) | ✅ | ✅ | ✅ | ✅ |

> ⚠️ = skill lives in a subdirectory of an external repo with no root-level `plugin.json` — Cursor cannot reference it from this marketplace. Install by adding [Pibbers/teradata-visual-explain-skill](https://github.com/Pibbers/teradata-visual-explain-skill) as a separate Cursor marketplace source.

## How it works

Skills are maintained alongside the projects they relate to. This repo acts as a single index — it references skills in their respective repositories using the `git-subdir` source type, so you only need one marketplace entry to access all of them.
