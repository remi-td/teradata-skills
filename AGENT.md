# Agent Context

This repository is a marketplace index for Teradata skills across Claude Code, Codex, Cursor, and VS Code agent surfaces. It also carries Codex MCP server plugin entries.

Use [CONTRIBUTING.md](CONTRIBUTING.md) as the source of truth for adding or changing skills and MCP server plugins. It contains the required manifest shapes, examples, and validation commands.

## Repository Rules

- Keep external skill and server code in the source repository. Do not copy external skill packages or MCP server code into this repo.
- Only skills maintained here belong under `skills/`.
- Runtime files used by a skill must live beside that skill's `SKILL.md`.
- Update every relevant marketplace manifest when adding a skill:
  - `.claude-plugin/marketplace.json`
  - `.agents/plugins/marketplace.json`
  - `.cursor-plugin/marketplace.json`
  - `README.md`
- For local skills, also maintain:
  - `skills/<name>/.claude-plugin/plugin.json`
  - `skills/<name>/.codex-plugin/plugin.json`
  - `skills/<name>/plugin.json`
- Codex MCP server plugins should use a tiny local plugin bundle with `.codex-plugin/plugin.json`; do not add upstream plugin files unless the source repository maintainers want them. If the server runs through `uvx` or another package runner, keep runtime code out of this repo and link to the official source from the bundle README.

## Codex Source Rules

- Local skills use `"source": "local"` with `"path": "./skills/<name>"`.
- External root repositories use `"source": "url"` with a Git URL and `ref`.
- External subdirectory plugins use `"source": "git-subdir"` with a Git URL, subdirectory `path`, and `ref`.
- MCP server plugins use an `mcpServers` object in the plugin manifest. Use `env_vars` for credentials and local configuration such as `DATABASE_URI`. A marketplace `source` is still required by Codex; it can point to the local metadata-only plugin bundle when runtime code is supplied by the command.
- Do not use Codex `"source": "github"`.
- Do not use Codex `git-subdir` with `"path": "."`.

## Validation Checklist

Run JSON validation after manifest edits:

```bash
python3 -m json.tool .agents/plugins/marketplace.json >/dev/null
python3 -m json.tool .claude-plugin/marketplace.json >/dev/null
python3 -m json.tool .cursor-plugin/marketplace.json >/dev/null
```

Run a clean Codex install test before declaring success:

```bash
tmp_home=$(mktemp -d)
CODEX_HOME="$tmp_home" codex plugin marketplace add ./ >/dev/null
CODEX_HOME="$tmp_home" codex plugin list --available --json
```

When changing existing Codex entries, install the affected plugins in the same temporary `CODEX_HOME`. For MCP server plugins, also run `CODEX_HOME="$tmp_home" codex mcp list --json`.

## Existing Skill Inventory

- `teradata-query`: external subdirectory plugin from `remi-td/tq`, path `agentic`.
- `teradata-sql-analytics`: external root repository from `ksturgeon-td/tdsql-mcp`.
- `teradata-visual-explain`: external root repository from `Pibbers/teradata-visual-explain-skill`.
- `teradata-react`: local skill under `skills/teradata-react`.
- `teradata-sql-jupyter`: local skill under `skills/teradata-sql-jupyter`.
- `teradata-mcp-customisation`: external subdirectory plugin from `Teradata/teradata-mcp-server`, path `agentic`.
- `teradata-mcp-server`: Codex MCP server plugin from `Teradata/teradata-mcp-server`, configured as `uvx teradata-mcp-server` and requiring `DATABASE_URI`.
- `teradata-trial-data-loading`: external root repository from `ksturgeon-td/teradata-trial-data-loading`.

## Practical Notes

- Prefer `rg` and `rg --files` for repository inspection.
- Use `python3 -m json.tool` for JSON validation.
- Use a temporary `CODEX_HOME` for plugin install tests so user-level Codex config and installed plugins do not affect results.
- The README skill table should match the marketplace entries unless a framework-specific caveat is documented.
