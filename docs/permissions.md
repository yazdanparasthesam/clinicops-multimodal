# Permissions

| Actor | May do | May NOT do | Approval |
|---|---|---|---|
| `nurse` | create visits, upload attachments, comment, submit | approve/dispense | self |
| `doctor` | all nurse + request_changes/approve/reject + trigger AI drafts | dispense | RBAC check |
| `pharmacist` | dispense after approved | create/approve | RBAC check |
| AI (via ai_service) | produce prose, call read-only tools, log | compute scores/mutate | human finalize |
| MCP server | read-only GETs (RBAC applies) | any write | token |
| oncall-agent | allowlisted commands only | prod secret read, arbitrary shell | runbook |

## Matrix (HTTP → role)

| Endpoint | nurse | doctor | pharmacist |
|---|---|---|---|
| POST /visits, attachments | ✓ | ✓ | ✗ |
| GET /visits/*, exports | ✓ | ✓ | ✓ |
| AI drafts/transcribe/chat | ✓ | ✓ | ✗ |
| submit | ✓ | ✓ | ✗ |
| approve/reject/request_changes | ✗ | ✓ | ✗ |
| dispense | ✗ | ✗ | ✓ |

