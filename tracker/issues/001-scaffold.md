---
title: "Project scaffold, AGENTS.md context pack, product spec (ClinicOps Multimodal)"
labels: [scaffold,agent-context]
milestone: "M1 — Foundations"
state: closed
agent: "Arena Agent"
---

## Goal
Repo skeleton 1:1 clone of clinicops-multimodal, re-themed to ClinicOps Multimodal with .agents/skills, product-spec, AGENTS.md pointing at modular docs, Makefile, .env.example, LICENSE, seed data.

## Acceptance criteria
- [x] `product-spec.md` covers problem, users, journey, R001-R008, 72h deadline, multimodal context (CSV+image+audio+PDF)
- [x] `AGENTS.md` exists and points to `docs/*` modules (architecture, decisions, testing, security) + Law 9 (multimodal files never execute)
- [x] `make help` lists every workflow; `.env.example` documented with DATABASE_URL, JWT_SECRET, AI_PROVIDER, STORAGE_PATH
- [x] `seed/` contains multimodal CSVs (demo-intake.csv, patient_visit_*.csv) + `evidence/fixtures/` lesion-sample.jpg + memo-sample.webm

## Agent evidence log
- Arena Agent — scaffolded via git clone clinicops-multimodal sync + re-themed domain nouns; audited against full-mark layout.
- Verified: `make help`, `docker compose config --quiet`, `ls .agents/skills/neon`
