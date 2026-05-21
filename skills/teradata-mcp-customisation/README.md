# teradata-mcp-customisation

A Claude Code skill for building, editing, and debugging a **semantic layer for the [Teradata MCP server](https://github.com/Teradata/teradata-mcp-server)** — custom tools, cubes, prompts, and glossary entries declared in YAML, plus the `profiles.yml` that exposes them.

## What this skill does

When the user asks Claude to extend a Teradata MCP server with custom objects, this skill loads and instructs Claude to:

- Pick the right `type:` for what they're building (`tool`, `cube`, `prompt`, `glossary`) and understand what each becomes at runtime (tool, tool, prompt, resource).
- Author flat denormalised base SQL for cubes, with public-named dimension aliases and `_v`-suffixed value columns, so the auto-generated `dim_filters` / `meas_filters` / `order_by` / `top` wrapping works as the LLM expects.
- Use parameter substitution correctly: `:name` for value binds, `{name}` for identifier interpolation (database / table names), with the synthetic `{table_ref}` shortcut.
- Write `profiles.yml` regex selectors that route each object to the right MCP registry (tools vs prompts vs resources), without conflating glossary (resources) with tools.
- Smoke-test a running server with the streamable-HTTP curl handshake (`initialize` → `notifications/initialized` → `tools/list` / `prompts/list` / `resources/list`).

## Layout

```
.claude-plugin/plugin.json                    # plugin manifest
skills/teradata-mcp-customisation/
├── SKILL.md                                  # frontmatter + entry point
├── reference/
│   ├── object-types.md                       # full YAML schemas for tool / cube / prompt / glossary
│   ├── cube-mechanics.md                     # exact SELECT the server wraps around base SQL
│   ├── parameter-substitution.md             # :name vs {name}, type_hint, persist
│   ├── profiles.md                           # layering, regex selectors, run: block
│   └── deployment.md                         # config_dir, launch, curl smoke-test
└── examples/
    ├── example_tool.yml                      # parameterised tool on DBC.AllSpaceV
    ├── example_cube.yml                      # database-space cube on DBC.AllSpaceV
    ├── example_prompt.yml                    # DBA persona with focus_area parameter
    ├── example_glossary.yml                  # permspace / spool / skew_factor terms
    └── example_profiles.yml                  # paired curated + super profiles
```

All examples target the `DBC` system catalogue so anyone with a Teradata instance can reproduce them without provisioning sample data.
