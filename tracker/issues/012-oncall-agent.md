---
title: "On-call responder: wakes on alert, allowlist fix"
labels: [oncall,agent]
milestone: "M7 — Ship"
state: closed
agent: "Arena Agent"
---

## Goal
Agent wakes and fixes.

## Acceptance criteria
- [x] allowlist docker restart/curl, incident markdown
- [x] Compose service 8090, drill

## Agent evidence log
- Verified: pytest test_oncall.py, alert-drill
