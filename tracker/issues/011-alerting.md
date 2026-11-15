---
title: "User-impact alerts: 4 rules + Alertmanager"
labels: [alerting]
milestone: "M7 — Ship"
state: closed
agent: "Arena Agent"
---

## Goal
4 alerts not CPU.

## Acceptance criteria
- [x] alerts.yml: PrescriptionSaveFailing, ImageAnalysisFailing, HighLatencyVisit, TranscriptionStuck
- [x] Alertmanager webhook to oncall

## Agent evidence log
- Verified: promtool check rules
