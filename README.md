# Teradata Skills

A multi-framework skill marketplace aggregating Teradata-related skills maintained across multiple repositories. Install once, get all skills — in Claude Code or Codex.

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

**GUI:** Settings → Plugins → Add More → enter `remi-td/teradata-skills` in the Source field → select the skills you want to install.

**Config (`~/.codex/config.toml`):**

```toml
[marketplaces.teradata-skills]
source_type = "git"
source = "https://github.com/remi-td/teradata-skills.git"
```

Restart Codex after editing the config.

## Available Skills

| Skill | Description | Source |
|-------|-------------|--------|
| `teradata-query` | Install, configure, and use the [tq CLI](https://github.com/remi-td/tq) to run Teradata queries, explore schemas, monitor sessions, and manage database objects from the command line. | [remi-td/tq](https://github.com/remi-td/tq/tree/master/agentic) |
| `teradata-sql-analytics` | Teradata native function guidelines and syntax — load at the start of any Teradata analytics session. | [remi-td/teradata-sql-analytics](https://github.com/remi-td/teradata-sql-analytics) |
| `teradata-visual-explain` | Decode and visualise Teradata EXPLAIN output. | [Pibbers/teradata-visual-explain-skill](https://github.com/Pibbers/teradata-visual-explain-skill) |
| `teradata-react` | Scaffold, develop, and deploy a production-shaped React + FastAPI web application backed by Teradata Vantage. Covers project layout, connection pooling, query patterns, theming/branding, security, and deployment. | [skills/teradata-react](skills/teradata-react) *(this repo)* |
| `teradata-sql-jupyter` | Author Teradata SQL Jupyter notebooks for exploratory data analytics, teaching, demos, and interactive SQL user guides. Also assists with installing and running the Teradata Jupyter SQL extensions. | [skills/teradata-sql-jupyter](skills/teradata-sql-jupyter) *(this repo)* |
| `teradata-mcp-customisation` | Build, edit, and debug a semantic layer for the Teradata MCP server — custom tools, cubes, prompts, and glossary entries declared in YAML, plus the `profiles.yml` that exposes them. | [skills/teradata-mcp-customisation](skills/teradata-mcp-customisation) *(this repo)* |

## How it works

Skills are maintained alongside the projects they relate to. This repo acts as a single index — it references skills in their respective repositories using the `git-subdir` source type, so you only need one marketplace entry to access all of them.
