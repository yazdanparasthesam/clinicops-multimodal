# MCP Server

Read-only MCP server over live ClinicOps API.

Tools: list_visits, get_visit, get_validations, get_scores, get_attachments, get_checklist

Run: `python mcp-server/server.py --token $FS_TOKEN`

All tools enforce RBAC of the token owner; never mutate.
