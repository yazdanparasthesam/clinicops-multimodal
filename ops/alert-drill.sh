#!/usr/bin/env bash
set -euo pipefail
SIM="false"
if [[ "${1:-}" == "--simulate" ]]; then SIM="true"; fi
echo "Alert drill (simulate=$SIM)"
# In simulate mode, we hit oncall-agent directly
if [[ "$SIM" == "true" ]]; then
  curl -sf -X POST http://localhost:8090/webhook -H 'Content-Type: application/json' -d '{"alerts":[{"labels":{"alertname":"PrescriptionSaveFailing","severity":"critical"}}]}' && echo "→ alert delivered to oncall-agent"
  sleep 2
  ls -lt ops/incidents/ | head
else
  # Real drill: make backend temporarily fail, promoter will catch via Prometheus, but for local we simulate same
  curl -sf -X POST http://localhost:8090/webhook -H 'Content-Type: application/json' -d '{"alerts":[{"labels":{"alertname":"HighLatencyVisit","severity":"warning"}}]}' && echo "→ real alert path"
fi
echo "Drill done. See ops/incidents/*.md and Grafana."
