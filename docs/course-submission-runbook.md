# Course Submission Runbook — ClinicOps Multimodal

Status snapshot: dev + prod Live, CI green, prod dispatched, 28/28 smoke, observability + alerts + on-call verified.

## Steps (like financial-statement but prod dispatched)

1. **Verify local tooling:** Project root + `docker compose v2.x` (evidence 00).
2. **App-only compose:** `docker compose up --build -d` → `db healthy, backend healthy, frontend up` (evidence step2).
3. **Health checks:** `curl /healthz` + `curl -I frontend` (evidence 01-02).
4. **Frontend login + multimodal:** Nurse login → create visit → upload CSV+JPG+WAV+PDF → scores/validations appear (evidence 03-06).
5. **AI drafts:** Trigger vision draft + transcribe → structured SOAP (evidence 07-08).
6. **Workflow gates:** Submit blocked by error-rule → fix → submit → approve → dispense (evidence 09-10).
7. **Exports:** PDF Rx + XLSX (evidence 11).
8. **Local tests:** `make test` + `make frontend-test` green (evidence 12).
9. **Smoke:** `bash ops/smoke.sh http://localhost:8000` 28/28 (evidence 13).
10. **Observability:** `make obs-up` → Grafana dashboard with trace_id (evidence 14).
11. **Alert drill:** `bash ops/alert-drill.sh --simulate` + real (evidence 15-16).
12. **Deploy dev:** Push main → CI ✅ → Deploy Dev ✅ → `curl prod` + Vercel 200 (evidence 05-07).
13. **Dispatch prod:** `gh workflow run promote-prod.yml` → `production` approval → Deploy Prod ✅ → prod URLs Live (evidence 08) — **the fix vs Project1**.
14. **Peer reviews:** 3 on course platform (mandatory).

Peer-review completion mandatory to pass.
