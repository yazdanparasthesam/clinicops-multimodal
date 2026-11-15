# Operations

## Runbooks

- **Health:** `curl /healthz` → `{"status":"ok"}`. Check `docker compose ps` health.
- **Smoke:** `bash ops/smoke.sh $BASE` — 28 checks including multimodal uploads + AI drafts + workflow gates.
- **Logs:** `docker compose logs backend --tail=200` or Grafana/Loki.
- **Metrics:** `/metrics` or Grafana.
- **Alert drill:** `bash ops/alert-drill.sh --simulate` (local) + real drill against running stack.

## On-Call

`oncall-agent/agent.py` deterministic responder. Allowlist: `docker restart backend`, `python scripts/requeue_attachments.py`, `curl /healthz`, `docker compose ps`. Any other command → rc=126 + escalate. Writes `ops/incidents/<timestamp>-<alert>.md`.

## Diagnostics

- DB: `psql $DATABASE_URL -c "select status,count(*) from visits group by status;"`
- Attachments: `ls -lh /data/attachments` (compose volume)
- Seed reset: `make seed` (idempotent)

