---
title: "Multimodal intake + 10 clinical scores engine (BMI, eGFR, MAP, BSA, CCI, Wells, Dose/kg, Adherence, APGAR, Risk)"
labels: [backend,domain]
milestone: "M2 — Domain"
state: closed
agent: "Arena Agent + Copilot CLI"
---

## Goal
Deterministic clinical-score computation from CSV/visits — AI never computes. All pure functions in domain/scores.py.

## Acceptance criteria
- [x] `POST /visits/{id}/attachments` accepts CSV/XLSX → intake parsed; PATCH maps vitals
- [x] `domain/scores.py`: BMI, MAP, BSA, eGFR, CCI, Wells, Dose/kg, Adherence, APGAR, Risk — pure
- [x] Scores via `recompute_visit` with intake_override + flag_modified; stored in scores_json
- [x] Seed patient_visit_clean.csv → BMI 22.9, MAP 93.3 demo

## Agent evidence log
- **Arena Agent** — designed scores.py (10 formulas) + pipeline recompute; Copilot batch tests.
- Verified: `pytest tests/unit/test_scores.py` (7), `curl PATCH + GET scores` shows BMI 22.9
- Evidence: evidence/curated/04-scores.png
