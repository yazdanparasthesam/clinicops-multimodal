---
title: "Containerization: one-command full stack incl. DB"
labels: [docker,infra]
milestone: "M5 — Ship"
state: closed
agent: "Arena Agent"
---

## Goal
Full system via Docker Compose single command.

## Acceptance criteria
- [x] db postgres:16 + backend healthcheck + frontend nginx proxy
- [x] Volume attachments:/data/attachments, obs profile

## Agent evidence log
- Verified: docker compose up --build
