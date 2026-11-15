---
title: "Visit workflow: states, roles, comments, audit trail"
labels: [backend,workflow]
milestone: "M3 — Workflow"
state: closed
agent: "Arena Agent"
---

## Goal
State machine draft→submitted→in_review→approved→dispensed with RBAC.

## Acceptance criteria
- [x] ALLOWED transitions + ROLE_TRANSITIONS pure
- [x] POST /workflow/{action} — 403/409/422 as appropriate
- [x] AuditLog every transition + Comments

## Agent evidence log
- Arena Agent — built workflow; Copilot RBAC tests.
- Verified: test_auth_rbac (pharmacist 403, doctor 200)
