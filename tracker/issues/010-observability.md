---
title: "Observability: metrics+traces+logs with trace_id"
labels: [observability]
milestone: "M7 — Ship"
state: closed
agent: "Arena Agent"
---

## Goal
Golden journey instrumented.

## Acceptance criteria
- [x] TraceMiddleware whitelist, OTel opt-in, Grafana dashboard
- [x] Journey hooks emit visit_attachments_total{modality} etc

## Agent evidence log
- Verified: test_telemetry_policy, curl /metrics, Grafana
