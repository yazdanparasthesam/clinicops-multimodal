# Agent Extension Pack

Components: `agent-capabilities/`, `agent-hooks/`, `mcp-server/`, `custom-agent/`.

## Composition

```
coding agent → reads AGENTS.md + openapi.yaml → guarded by agent-hooks
MCP client ──stdio──► mcp-server/server.py ──JWT──► FastAPI (RBAC)
custom-agent/validator-auditor uses workflows/clinical-audit.md
```

## Running

- MCP: `mcp-server/README.md`
- Hooks: `agent-hooks/README.md`
- Subagent: `custom-agent/validator-auditor.md`

Permission matrix: `docs/permissions.md`; threat model: `security/agent-security.md`.
