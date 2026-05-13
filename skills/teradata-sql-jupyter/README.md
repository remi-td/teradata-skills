# teradata-sql-jupyter

A Claude Code skill for authoring **Teradata SQL Jupyter notebooks** — exploratory data analyses, product demos, interactive user guides, and runnable tutorials that use the [Teradata Jupyter SQL extensions](https://github.com/Teradata/jupyterextensions).

## What this skill does

When the user asks Claude to build or modify a Teradata SQL notebook — or to help install the Teradata Jupyter SQL extensions — this skill loads and instructs Claude to:

- Emit valid `.ipynb` files with the correct `teradatasql` kernel spec (via a helper script, not hand-rolled JSON).
- Start each notebook with a connection block (`%var` → `%addconnect` → `%connect` → `DATABASE ${db}`) with placeholders, never hardcoded credentials.
- Alternate markdown narrative and SQL/magic cells — one concept per cell.
- Prefer magics (`%dataload`, `%chart`, `%table`, `%history`) over hand-coded equivalents.
- Produce idempotent, tearable-down notebooks for demos and teaching.
- Walk users through installing the extensions (Docker or pip) and verifying the first connection.

## Layout

```
.claude-plugin/plugin.json          # plugin manifest
skills/teradata-sql-jupyter/
  SKILL.md                          # entry point loaded by Claude
  reference/                        # on-demand docs (magics, notebook JSON, connections, install, patterns)
  templates/                        # eda / teaching / demo / user-guide starter .ipynb files
  scripts/
    build_notebook.py               # emit a valid Teradata SQL .ipynb from a cell spec
    _build_templates.py             # regenerates the templates/ folder
```

## Using the skill

Claude invokes it automatically when a task matches the trigger conditions in `skills/teradata-sql-jupyter/SKILL.md`.

To build a notebook manually with the helper:

```bash
python3 skills/teradata-sql-jupyter/scripts/build_notebook.py \
    --spec my-spec.json --out my-notebook.ipynb
```

where `my-spec.json` is:

```json
{
  "cells": [
    {"type": "md",  "source": "# Title"},
    {"type": "sql", "source": "%var db=mydb\nSELECT TOP 5 * FROM ${db}.orders;"}
  ]
}
```

To regenerate the shipped templates:

```bash
python3 skills/teradata-sql-jupyter/scripts/_build_templates.py
```

## Running the notebooks this skill produces

Install the [Teradata Jupyter SQL extensions](https://teradata.github.io/jupyterextensions/), open the generated `.ipynb` in JupyterLab, and run the cells. See `skills/teradata-sql-jupyter/reference/installation.md` for full install instructions and troubleshooting.

## License

See the upstream Teradata extensions repo for third-party license terms:
https://github.com/Teradata/jupyterextensions/tree/master/licensefiles
