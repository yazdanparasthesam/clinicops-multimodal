# Observability

## Signals

- **Metrics:** Prometheus scrapes `backend:/metrics` (Instrumentator). Key: `http_requests_total`, `visit_attachments_total{modality}`, `vision_latency_ms`, `transcription_duration_ms`, `workflow_transitions_total`.
- **Traces:** OTel SDK → `otel-collector:4317` → Tempo. `X-Trace-Id` propagated.
- **Logs:** JSON structured via `infra/telemetry/logging.py` — whitelisted fields only (`method,route,status,duration_ms,step,rule_id,modality`). No PII. OTLP → Loki.

All share `trace_id`.

## Dashboard

`observability/grafana/dashboards/clinicops-journey.json` — panels: request rate, p95 latency, attachment throughput by modality, workflow funnel, error rate. View at `http://localhost:3001` (admin/admin) when `make obs-up`.

## Alerts (user-impact)

In `observability/prometheus/alerts.yml` (validated by `promtool check rules`):

- `PrescriptionSaveFailing` — 5xx on prescriptions >2/5m
- `ImageAnalysisFailing` — vision 5xx >1/5m
- `TranscriptionStuck` — queue depth >5 (if async)
- `HighLatencyVisit` — p95 >800ms for 5m

Alertmanager routes to `oncall-agent:8090/webhook`.

## Runbook

`ops/alert-drill.sh` fires a synthetic alert, hits responder, verifies recovery. See `docs/operations.md`.
