# The agent team — who does what, and how they hand off

This project is built and operated by a **team of agents** around one human owner. The team is defined by *artifacts*, not by chat: every handoff is a file in the repo, which keeps the process reproducible and auditable.

## Roster

| Agent | Role | Where it lives | Scope of power |
|---|---|---|---|
| **Arena Agent** | Architect & reviewer — spec, design, rubric audits, complex implementations, review passes | this conversation + commits authored by the owner | full repo (human-in-the-loop per step) |
| **GitHub Copilot CLI** | Designated headless implementer — invoke for batch code generation from AGENTS.md | `custom-agent/`, invoked via `gh copilot` / CLI | repo files; guarded by `agent-hooks/guard.sh` |
| **CI scanners** | Automated reviewer — ruff, pytest, vitest, gitleaks, bandit, pip-audit, semgrep, trivy, contract-drift gate | `.github/workflows/ci.yml` | read + block merge |
| **MCP server** | Read-only data plane for any external agent (list/get visits & scores) | `mcp-server/` | GET-equivalent only, user-scoped token |
| **On-call responder** | Runtime operator — wakes on Alertmanager webhooks, runs allow-listed runbook commands, writes incident reports | `oncall-agent/` | exact runbook command grammar ONLY (rc=126 otherwise) |
| **Human owner** | Decisions, secrets, deploys to prod, escalations | — | everything |

## The working process (spec → ship → respond)

```
 product-spec.md ──► tracker/issues/*.md ──► implementation ──► verification
   (Arena Agent)          (acceptance criteria)    (Copilot CLI /     (pytest, ruff,
                        ▲   │                  Arena Agent)            vitest, smoke)
                        │   ▼                                        │
                   evidence log  ◄──── review (Arena Agent + CI scanners) ◄┘
                        │                                            │
                        ▼                                            ▼
                 gh issue close ──────────────────────► CI green ──► deploy dev (auto)
                                                                     deploy prod (manual)
                                                                            │
                     ┌──────────────────────────────────────────────────────┘
                     ▼
   runtime: metrics/traces/logs ──► Prometheus rules ──► Alertmanager ──► ON-CALL AGENT
                     ▲                                                       │
                     └──── Grafana dashboard ◄── ops/incidents/*.md ◄────────┘
                                              (fix + verify, or escalate to human)
```

**Handoff contracts** (files as the interface between agents):

1. `AGENTS.md` — the constitution every coding agent reads first.
2. `tracker/issues/*.md` — acceptance criteria + per-issue **agent evidence log**.
3. `docs/*` + `security/*` — modular deep docs AGENTS.md points to.
4. `ops/incidents/*.md` — responder output.
5. `agent-capabilities/prompts/*` — exact prompts used.

## Auto-close behavior

Commits that contain `Closes #N` (e.g. `feat: scores engine (Closes #2)`) are auto-closed by `.github/workflows/auto-close-issues.yml` via `actions/github-script`. This mirrors the manual `gh issue close N` workflow from financial-statement but is auditable in CI logs. Agent commits should always reference the tracker issue number.

## Evidence the team was actually used

- Per-issue agent logs in `tracker/issues/` (14 issues).
- `ops/incidents/` + `oncall-agent/example-incident.md`.
- CI runs exercising scanner + on-call test jobs.

