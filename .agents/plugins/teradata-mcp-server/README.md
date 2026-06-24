# Teradata MCP Server Codex Plugin

Metadata-only Codex plugin bundle for the Teradata MCP Server.

The MCP server itself is not vendored here. Codex runs it with:

```bash
uvx teradata-mcp-server
```

Set `DATABASE_URI` in the environment where Codex runs.
`DATABASE_URI` format: `teradata://<USERNAME>:<PASSWORD>@<HOST_URL>:1025/<USERNAME>`

Official server source:

- https://github.com/Teradata/teradata-mcp-server
