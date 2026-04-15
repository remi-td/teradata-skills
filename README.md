# Teradata Skills for Claude Code

A Claude Code plugin marketplace that aggregates Teradata-related skills maintained across multiple repositories.

## Installation

Add the marketplace in any Claude Code session:

```
/plugin marketplace add remi-td/teradata-skills
```

Then install the skills you want:

```
/plugin list
```

After installing, restart Claude Code to activate the skills.

## Available Skills

| Skill | Description | Source |
|-------|-------------|--------|
| `/teradata-query` | Install, configure, and use the [tq CLI](https://github.com/remi-td/tq) to run Teradata queries, explore schemas, monitor sessions, and manage database objects from the command line. | [remi-td/tq](https://github.com/remi-td/tq/tree/master/skills/teradata-query) |

## How it works

Skills are maintained alongside the projects they relate to. This marketplace repo acts as a single index — it references skills living in their respective repositories using the `git-subdir` source type, so you only need one marketplace entry to access all of them.
