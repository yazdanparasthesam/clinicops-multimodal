---
title: "Deterministic validation engine R001–R008 + submit gates"
labels: [backend,validation]
milestone: "M2 — Domain"
state: closed
agent: "Arena Agent"
---

## Goal
8 validation rules — error blocks gates.

## Acceptance criteria
- [x] R001 allergy, R002 dose-range, R003 interaction, R004 duplicate, R005 image-consent, R006 transcript-confidence, R007 vitals-range, R008 missing-vitals
- [x] Gates block submit/approve/dispense → 422

## Agent evidence log
- Arena Agent — implemented validators + gates.
- Verified: pytest test_validators.py (6), test_workflow_gates (422→200)
