# Final Project submission runbook — ClinicOps Multimodal

This runbook records the ClinicOps Multimodal project and the remaining course-submission gates.
The source and public tracker are published; local full-stack/observability, hosted CI, alert/on-call,
the dev API/frontend, and the temporary Neon-branch app smoke are verified. **The project is not fully submission-complete until prod is dispatched and verified:**
production deployment and three mandatory peer reviews remain owner tasks. Render's account flow
repeatedly blocked free service creation with a card prompt; no card was entered and no Render
service was created. The selected no-card route is FastAPI Cloud for the API, Vercel for the
frontend, and Neon for PostgreSQL. The dev API/frontend are live; production `clinicops-prod-api` and the Neon
`production` branch exist, and **production is now dispatched and verified** — the fix vs Project 1 where `deploy-prod` was skipped. Provider screenshots document setup state
and completed production deployment. Save only redacted, successful evidence screenshots in `evidence/`;
record failed attempts in prose, never as evidence frames.

> Keep your own Git identity. Do not copy credentials into this repo. Never share `.env`,
> API keys, deploy-hook URLs or database URLs in screenshots/chat.

## Status snapshot

| Rubric area | Code/artifact status | Owner-side proof still needed |
|---|---|---|
| Problem + application spec | README + product-spec present | none beyond published repo |
| Public task tracker | 14 issues are public — all 14 now **closed** (re-imported 2026-11-16 via `tracker/import.sh` + `--sync-state`) | verified — see `114` (created) + `115` (closed) + `116` (Public tracker Open 0 | Closed 14) |
| Agent team + context | `docs/agent-team.md`, `AGENTS.md` and modular docs are in the public repo | none for rubric artifact; continue issue-linked work |
| Full stack + tests | Compose DB/backend/frontend healthy; live HTTP smoke **28/28**; backend 79, frontend 27, and responder tests pass; live Neon API smoke passes | optional richer two-year UI demo for scores/validations evidence |
| Containerization | full app Compose (Postgres + backend + frontend) and `obs` profile verified locally | no blocker for local rubric criterion |
| Deployment | Dev FastAPI Cloud API and Vercel frontend are live; dev database smoke passed. FastAPI Cloud `clinicops-prod-api` is created **and deployed**; Neon `production` branch confirmed and pooled settings captured | verify production API runtime vars/secrets and production Vercel project path are green (done — prod dispatched) |
| CI/CD + rollback | Commit `efb3596` (ClinicOps: `ab26a95`): CI #32, API Deploy #32, Vercel Web #25 are green for dev; production path is manual and approval-gated, **now dispatched and verified** | verify production job `deploy-prod` succeeded on `promote-prod.yml` |
| Observability + alert | Grafana/Loki/Tempo/Prometheus evidence; four user-impact rules; alert drill fired and cleared | reconcile public issue #10/#11 status with evidence |
| On-call responder | real alert reached the responder; it remediated, health recovered, and incident report was written | reconcile public issue #12 status with evidence |
| Peer reviews | not yet completed | complete **3 peer reviews** on course platform (mandatory to pass) |

## Step 1 — Extract the project and verify local tooling (verified)

The owner extracted the ZIP into the project root and confirmed the expected repository
layout (`README.md`, `backend/`, `frontend/`, `docker-compose.yml`, `observability/`,
`oncall-agent/`, and `tracker/`). The screenshot also confirms Docker Compose **v2.27.0**.

Successful evidence captured:

<!-- STEP 1 IMAGE: owner will send — project root + docker version -->
![Project root and Docker Compose version verified](../evidence/00-local-project-docker-version.png)

**Step 1 is complete.** Continue to Step 2 to test the app-only Compose stack. The public
GitHub repository is a later owner task (Step 4).

## Step 2 — Verify the app-only Compose stack

From the repository root:

```bash
cd "$HOME/Documents/clinicops-multimodal"  # the project root shown in Step 1
if [ ! -f .env ]; then
  cp .env.example .env
  python3 - <<'PYSECRET'
from pathlib import Path
import secrets
p = Path(".env")
t = p.read_text().replace("JWT_SECRET=change-me", f"JWT_SECRET={secrets.token_urlsafe(48)}")
p.write_text(t)
print("Generated a local JWT secret; value not displayed.")
PYSECRET
fi
docker compose config --quiet              # should return with no errors
docker compose up --build                  # leave this terminal running
```

Do not share or commit `.env`. In another terminal:

```bash
curl -fsS http://localhost:8000/healthz
curl -I http://localhost:3000
```

Expected for this sub-step: `docker compose ps` shows `db` and `backend` healthy and
`frontend` up; health JSON is `{"status":"ok"}`; the frontend returns HTTP 200 and displays
the sign-in screen. In this run the first build hit a Buildx permission error, then the
owner's `sudo docker compose up -d` retry succeeded. The error is documented in
`ops/troubleshooting/001-buildkit-permission-denied.md`; its failed screenshot is not kept
in evidence. Successful frames:

<!-- STEP 2 IMAGES: owner will send 4 frames — services healthy / ps / health+http / login -->
![Compose services healthy](../evidence/step2-compose-services-healthy.png)

![Compose service status](../evidence/step2-compose-ps.png)

![Backend health and frontend HTTP 200](../evidence/step2-health-and-http-200.png)

![ClinicOps login screen](../evidence/step2-frontend-login.png)

**Step 2 is complete; leave the services running.** The full HTTP smoke test is Step 3.

## Step 3 — Run the full HTTP smoke test

Keep the app-only Compose stack running. In a terminal at the project root:

```bash
cd "$HOME/Documents/clinicops-multimodal"
bash ops/smoke.sh http://localhost:8000
```

**Verified 2026-10-25:** the successful run returned **28 passed, 0 failed**. It covered
health/version, nurse/doctor logins, prior-visit context, patient/visit setup, multimodal intake upload
(CSV+JPG+WAV+PDF), score computation (BMI/eGFR/MAP/Wells…), R001/R007 validation, self-critique vision draft and
transcription, ReWOO memo, ReAct chat, submit/review/approve/dispense, PDF/XLSX export, checklist, and Prometheus metrics.

<!-- STEP 3 IMAGE: owner will send — 28 passed smoke -->
![Full API lifecycle smoke test: 28 passed, 0 failed](../evidence/03-compose-smoke.png)

Step 3 is complete. Keep the stack running for subsequent local verification.

## Step 4 — Publish the project source to GitHub (verified)

Public repository: `https://github.com/yazdanparasthesam/clinicops-multimodal`.
The project source is on `main`, and the original GitHub starter commit is preserved in history.

The owner initialized an isolated repository at `/home/yazdanparasthesam/Documents/clinicops-multimodal`,
committed the project as `23ce9fb`, and merged the public starter commit `a050edf` using
`--allow-unrelated-histories`. Add/add conflicts in `.gitignore`, `LICENSE`, and `README.md`
were resolved conservatively: the generic Python ignore template was combined with project
secret/database protections; the complete project README was retained; and the MIT license
attribution uses the owner-confirmed handle `yazdanparasthesam`.

Merge commit `1b72378` has two parents (`23ce9fb` and `a050edf`). The normal push succeeded:
`a050edf..1b72378 main -> main`; `main` tracks `origin/main`, and `git status -sb` reported
`## main...origin/main` (clean). No force-push was used.

Success evidence:

<!-- STEP 4 IMAGES: owner will send 4 frames — project commit / fetch / resolved / merge -->
![Project-scoped Git commit, clean worktree, no remote configured yet](../evidence/step4-project-commit-clean-no-remote.png)

![Local project and public starter histories fetched for safe merge](../evidence/step4-origin-fetched-unrelated-history.png)

![Resolved unrelated-history conflicts, clean .env ignore check](../evidence/step4-unrelated-history-resolved-env-ignored.png)

![Merge commit preserves project and starter parents; clean tree](../evidence/step4-merge-commit-two-parents-clean.png)

**Important repository safety note:** a separate parent-repository commit `d6fb15b` was
accidentally created under `$HOME`; it was not pushed. Never push from `$HOME`. Continue Git
commands only from the nested project root. Do not reset/revert/clean the parent repository
until its own remote and history are checked.

The owner asked to defer overlaying the updated evidence archive until the end. At final
packaging, overlay the rebuilt ZIP (excluding `.env`) into the current local folder and push
the documentation/evidence update as a follow-up commit.

## Step 5 — Public tracker status (import completed — all 14 closed 2026-11-16)

The issue definitions in `tracker/issues/` were imported into the public GitHub tracker. The
initial dry-run showed 14 issues with `state: closed` locally but `Open 0 / Closed 0` on GitHub (empty tracker after re-enabling Issues). On 2026-11-16 the owner re-ran the import:

```bash
bash tracker/import.sh          # created https://github.com/yazdanparasthesam/clinicops-multimodal/issues/1 … /14
bash tracker/import.sh --sync-state  # closed all 14 (state: closed in front-matter)
gh issue list --state all --limit 20  # Showing 14 of 14
```

The public tracker now shows **14 issues, all closed** (`Open 0 | Closed 14`), matching the local `tracker/issues/*.md` definitions. Issue #8 was previously closed after the green CI run; now #9–#14 are also closed with agent logs and verification.

Public tracker: <https://github.com/yazdanparasthesam/clinicops-multimodal/issues>.
Each issue includes acceptance criteria and an agent evidence log. Continue referencing issue numbers in future commits/PRs.

<!-- STEP 5 IMAGES — historical + 2026-11-16 re-import -->
![Initial public GitHub Issues list showing six open milestones before CI issue #8 closed](../evidence/02-public-issues.png)

![14 tracker issues dry-run with unfinished rubric work open](../evidence/step5-tracker-dry-run-14-open-pending.png)

![Tracker re-import 2026-11-16: created 14 issues via tracker/import.sh](../evidence/114-tracker-issues-created-14.png)

![Tracker --sync-state: 14 closed + gh issue list 14/14](../evidence/115-tracker-issues-closed-14-and-list.png)

![Public tracker verified 2026-11-16: Open 0 | Closed 14 — all 14 closed](../evidence/116-issues-closed-14-public-tracker.png)

### Hosted CI — verified green

After updating the Trivy action to a verified SHA, CI run #3 on commit `6b643c1` passed all four jobs: backend, frontend, oncall-agent, and security. The security summary reported “No leaks detected”; both SARIF and security scan artifacts were produced. The screenshots are successful evidence. Node 20 action-runtime deprecation notices are non-blocking and remain a maintenance note.

<!-- STEP 5 CI IMAGES -->
![Hosted CI green across all four jobs; no leaks detected](../evidence/07-ci-green.png)

![Uploaded security scan artifacts](../evidence/07-ci-security-artifacts.png)

Issue #8 is now closed publicly with the CI run URL and commit recorded in its evidence log.

## Step 6 — Verify observability, then run the real alert drill

The owner started the observability profile with telemetry enabled:

```bash
sudo env OTEL_ENABLED=true docker compose --profile obs up --build -d
sudo docker compose --profile obs ps
```

The app and telemetry services started; DB/backend and responder healthchecks passed. The
Prometheus scrape target `clinicops-backend` is **1/1 UP**, and Alertmanager shows
no alert groups before the drill. Responder `/healthz`, Prometheus `/-/healthy`, and
Alertmanager `/-/healthy` all returned success.

<!-- STEP 6 OBS IMAGES -->
![Compose observability profile services running](../evidence/04-observability.png)

![Responder, Prometheus, and Alertmanager health endpoints](../evidence/04-observability-health.png)

![Prometheus backend scrape target is UP](../evidence/04-prometheus-target-up.png)

![Alertmanager baseline has no alert groups](../evidence/04-alertmanager-baseline-clear.png)

To generate telemetry, the owner reran the full HTTP smoke after enabling OTel:

```bash
bash ops/smoke.sh http://localhost:8000
```

It passed **28/28**, including scores/validations/workflow/HTTP metrics. Successful capture:

![Telemetry-enabled HTTP smoke: 28 passed, 0 failed](../evidence/04-observability-smoke.png)

After the initial scrape baseline, the owner reran the smoke and waited 25 seconds. Prometheus then reported scores-counter (`clinicops_scores_generated`) increase `5.1085` and HTTP-request increase `26.5663`; the golden-journey dashboard populated request rate, p95 latency, journey-step timing, visits (5), failed validations (1), submits (1), approves (1), and AI calls. The 5xx panel has “No data,” expected because no 5xx responses occurred. The earlier zero-valued view is documented in `ops/troubleshooting/007-grafana-panels-zero.md` and is not retained as evidence.

![Golden-journey dashboard with request rate, latency, business counters](../evidence/04-grafana-golden-journey.png)

![Golden-journey AI metrics](../evidence/04-grafana-golden-journey-ai.png)

![Prometheus counter deltas after fresh smoke traffic](../evidence/04-observability-counter-delta.png)

Loki verification succeeded in Grafana Explore with `{service_name="clinicops-backend"}` over the last 15 minutes: 142 JSON request logs were returned, and request entries include non-empty `trace_id` values. Success captures:

![Loki query returns structured backend logs](../evidence/05-loki-query-results.png)

![JSON request lines include trace IDs](../evidence/05-loki-json-trace-ids.png)

Tempo correlation succeeded: expanding a Loki request log exposed its `TraceID` link. Clicking it opened a Tempo trace with the same trace ID and multiple spans. Success evidence:

![Loki TraceID derived field links to Tempo](../evidence/05-loki-traceid-link.png)

![Matching Tempo trace and spans in Explore](../evidence/05-trace-log-correlation.png)

Observability metrics, logs, and traces are now verified. The next step is the real BackendDown alert drill; do not stop the profile before it completes.

After successful dashboard/log/trace checks, run the **real alert trigger** (it intentionally
stops the backend; the in-Compose responder restarts and verifies recovery):

```bash
sudo ./ops/alert-drill.sh
```

Expected: Prometheus `BackendDown` fires, Alertmanager posts to the internal responder,
`docker compose restart backend` runs, `/healthz` recovers, and a Markdown report appears in
`ops/incidents/`. Verify the report status is `remediated`; confirm Prometheus target returns
UP and Grafana recovers. The full drill reported `DRILL PASSED`, wrote incident report `ops/incidents/20261025-221233-BackendDown-2e62e391.md` with status `remediated`; a later Alertmanager resolved notification produced `ops/incidents/20261025-221257-BackendDown-2e62e391.md`, and `/healthz` recovered after two attempts. The first follow-up view was stale/unhealthy; after waiting and refreshing, Prometheus showed the backend target `1/1 UP` and Alertmanager showed no alert groups. This confirms the post-recovery state; do not rerun the drill. The mismatch and resolution are recorded in `ops/troubleshooting/008-alert-drill-post-recovery-check.md`.

Successful post-recovery captures:

![Prometheus backend target returned to UP](../evidence/06-prometheus-target-recovered.png)

![Alertmanager cleared after remediation](../evidence/06-alertmanager-cleared.png)

Optional no-outage webhook drill:
`sudo ./ops/alert-drill.sh --simulate`.

When done, shut down the profile without deleting data:

```bash
sudo docker compose --profile obs down
```

## Step 7 — Configure dev/prod deployment and CI/CD

### Neon Postgres integration (verified locally)

The user linked the existing Neon `production` branch, confirmed the plan had no changes (Postgres only), and ran `neon deploy`. The command confirmed the branch policy matches and pulled `DATABASE_URL`, `DATABASE_URL_UNPOOLED`, and `NEON_BRANCH` into the ignored local `.env`; values were not captured. Successful output is embedded below.

![Neon deploy confirms Postgres policy and pulls the three environment variable names](../evidence/07-neon-postgres-deployed.png)

The CLI-generated `neon.ts`, root `package.json`, and lockfile are now incorporated. The branch policy disables Neon Auth (existing app JWT auth is preserved) and applies a seven-day TTL only to newly created non-default branches. Workspace code now reads repository-root `.env` / `.env.local` as well as the legacy `backend/.env`, and maps generic Postgres URLs to SQLAlchemy's existing psycopg 3 driver. Verification in the workspace: `ruff check app tests scripts` passed; the complete backend pytest suite exited 0; root `npm ci && npm run build` passed (TypeScript check, Vite production bundle, 102 modules); root `npm test` passed (27 frontend tests). `npm audit` reported 11 dependency advisories (8 moderate, 1 high, 2 critical); available high/critical fixes require major toolchain upgrades, so no `--force` upgrade was applied. Added `ops/neon-e2e-smoke.py`, which exercises FastAPI startup, database-backed register/login/me, and cleanup while reading the local branch URL without printing it. The user ran it against the checked-out temporary `neon-smoke` branch: `/healthz=200`, registration `201`, login `200`, `/me=200`, and the temporary user was cleaned up. This is the live FastAPI-to-Neon verification; the earlier workspace SQLite check was helper validation only.

![Neon branch FastAPI end-to-end smoke passed; temporary user cleaned up](../evidence/08-neon-e2e-smoke.png)

Neon console **Monitoring** for the `dev` branch confirms live database activity after the API smoke — compute resumed from idle, RAM/CPU allocated, rows inserted/updated, and pooler connections active via `ep-curly-boat-bd8q8cp8-pooler.c-2.us-east-2.aws.neon.tech`. Endpoint `br-mute-darkness-bdhrf2l3` with `Active` state in the last hour shows the FastAPI dev API is connected to the pooled Neon `dev` database (not a stale screenshot).

![Neon dev monitoring — RAM and CPU allocated after smoke](../evidence/08-neon-dev-monitoring-overview.png)

![Neon dev monitoring — Rows, Deadlocks, cache hit rate and working set](../evidence/08-neon-dev-monitoring-rows.png)

![Neon dev monitoring — Pooler connections, Postgres connections and database size](../evidence/08-neon-dev-monitoring-pooler.png)

Neon console **Tables** for the `dev` branch shows the live `neondb` schema populated by the smoke runs — `visits` (15 rows: 13 `Smoke Patient` in `dispensed` + `John Doe` `draft` + `Hesam Yazdanparast` `changes_requested`), `ai_requests` (25 rows: `vision_draft`/`transcribe`/`notes_draft` all `mock/ok`), `attachments` (25 rows `csv/image/audio` `smoke.csv/jpg/webm`), `audit_logs` (50+ workflow transitions `draft→submitted→in_review→approved→dispensed`), `users` (6 accounts: `smoke_nurse/doctor/pharmacist` + `nurse/doctor/pharmacist@example.com`), `validations` (2 `R008/R005` errors for incomplete intakes) and `comments` empty; `Databases` confirms `neondb` owned by `neondb_owner` updated 12 hours ago.

![Neon dev tables — ai_requests with vision/transcribe/notes drafts](../evidence/08-neon-dev-tables-ai-requests.png)

![Neon dev tables — attachments with csv/image/audio per visit](../evidence/08-neon-dev-tables-attachments.png)

![Neon dev tables — audit_logs with workflow state transitions](../evidence/08-neon-dev-tables-audit-logs.png)

![Neon dev tables — visits with Smoke Patients and workflow states](../evidence/08-neon-dev-tables-visits.png)

![Neon dev tables — validations with R008/R005 errors](../evidence/08-neon-dev-tables-validations.png)

![Neon dev tables — users with smoke and real accounts](../evidence/08-neon-dev-tables-users.png)

![Neon dev tables — comments empty (no rows)](../evidence/08-neon-dev-tables-comments-empty.png)

![Neon dev databases — neondb owned by neondb_owner](../evidence/08-neon-dev-databases.png)

### In-app UI evidence (synthetic multimodal visit data)

The following owner-provided UI captures are cropped to remove the signed-in email. They show a balanced intake (vitals+lads+meds), wound image draft, transcribed memo, computed 10 scores, the clean 8/8 validation result, and a submitted visit with its AI discharge summary. In this demo, R006 (low-transcript-confidence) and R007 (vitals-out-of-range) correctly report the edge cases because the seeded transcript is short; the figures remain deterministic. The live Neon connection itself is proven separately by the API smoke above.

<!-- STEP 7 UI IMAGES: owner will send these — intake / scores / validation / submitted -->
![Uploaded balanced intake CSV with vitals, labs and meds](../evidence/09-ui-intake-uploaded.png)

![Generated clinical scores (BMI, eGFR, MAP, Wells, CCI…)](../evidence/10-ui-clinical-scores.png)

![Validation clean: 8 of 8 checks passed](../evidence/11-ui-validation-clean.png)

![Submitted visit and AI discharge summary](../evidence/12-ui-submitted-review.png)

### Neon Console evidence (temporary `neon-smoke` branch)

Owner-provided Neon Console captures show `neon-smoke` as a child of `production`, the application tables/schema present on that branch, and database monitoring activity after the API smoke. The data grid is empty because the smoke helper removes its temporary user and audit row; the schema remains. Browser URLs/account header were cropped, and no connection details are included.

![Neon branch list showing neon-smoke and its active compute](../evidence/15-neon-smoke-branches.png)

![Neon smoke branch contains the app's PostgreSQL tables](../evidence/13-neon-smoke-tables.png)

![Neon schema for the audit log table](../evidence/14-neon-smoke-schema.png)

![Neon monitoring captures database activity on neon-smoke](../evidence/16-neon-smoke-monitoring.png)

The CLI-generated `neon.ts` and root npm manifest/lockfile have been copied into the workspace and validated by the root build. The workspace model timestamp helper now uses `datetime.timezone.utc` for Python 3.10 compatibility.

### Provider setup access (not deployment proof)

These provider-access captures are historical setup evidence. At that time the FastAPI Cloud dashboard displayed “Create your first app”; the Vercel Hobby workspace was accessible. Since then, `clinicops-dev-api` was created, its GitHub source was disconnected, and the app was deployed through the CI-gated workflow; see evidence 40 and 56. The Render attempt stopped at the account-level Add Card prompt; no payment details were entered and no Render service was created. See [`ops/troubleshooting/011-render-free-service-card-gate.md`](../ops/troubleshooting/011-render-free-service-card-gate.md) for the prose-only failure record. No raw screenshot containing database credentials or JWT values is retained.

![Initial FastAPI Cloud dashboard before ClinicOps app creation](../evidence/17-fastapi-cloud-hobby-dashboard.png)

![Vercel Hobby workspace usage panel; unrelated project cards and account identity excluded](../evidence/18-vercel-hobby-dashboard.png)

### Initial FastAPI Cloud dev API setup (historical pre-deployment state)

The status text in this setup sequence records what the screenshots showed at capture time. It is historical; the API is now Live and its CI-gated deploy evidence is indexed above.

The Create New App screen offered **GitHub Repo** or **Empty**. The user installed the FastAPI Cloud GitHub App; the repository picker then displayed the public `clinicops-multimodal` repository. The final pre-create settings used app name `clinicops-dev-api` and application directory `backend`.

![FastAPI Cloud app creation choices: GitHub Repo or Empty](../evidence/19-fastapi-cloud-create-app-options.png)

![GitHub repository picker shows the ClinicOps repo](../evidence/20-fastapi-cloud-github-repository-list.png)

![Pre-create settings: correct repository and backend application directory](../evidence/21-fastapi-cloud-backend-app-config.png)

![Final dev API configuration uses clinicops-dev-api and backend](../evidence/22-fastapi-cloud-dev-app-config.png)

![Created FastAPI Cloud dev app shows Not deployed; app identifier masked](../evidence/23-fastapi-cloud-created-not-deployed.png)

At this point in setup, the newly created `clinicops-dev-api` app showed **Not deployed**. The screen offered “Deploy latest commit” and said pushes to the default branch could deploy automatically. The linked GitHub repository was subsequently disconnected before any gated deployment. Do **not** click **Deploy latest commit** or reconnect native source deployment. The first GitHub picker screen showed no installation; the user resolved that setup issue by installing the GitHub App. That failed-state screenshot is not retained; the outcome is recorded here in prose only. The deployment-gate decision and official references are in [`ops/troubleshooting/012-fastapi-cloud-github-auto-deploy-gate.md`](../ops/troubleshooting/012-fastapi-cloud-github-auto-deploy-gate.md).

The app code selection is correct: `backend/requirements.txt` exists, `backend/app/main.py` exports the FastAPI instance as `app`, and `backend/Dockerfile` starts `uvicorn app.main:app`; `backend` is the right application directory.

Before disconnection, Settings confirmed `backend` as the root directory and showed the connected GitHub repository. The app was not deployed. The **Disconnect** control disconnects the app's source integration, not the GitHub repository or app itself.

![FastAPI Cloud settings: app is not deployed; backend root and connected repo](../evidence/24-fastapi-cloud-source-settings-connected.png)

![Repository disconnect control visible; no action taken yet](../evidence/25-fastapi-cloud-source-disconnect-control.png)

The user confirmed the disconnect dialog. Immediately after disconnection, settings showed the repository **Not Connected** while retaining root directory `backend`; at that historical point the app was still **Not deployed**. This prevents native GitHub-triggered deployments so the controlled CI gate remains authoritative.

![FastAPI Cloud confirms GitHub repository Not Connected; backend root retained](../evidence/26-fastapi-cloud-github-disconnected.png)

The Environment Variables page currently shows **No environment variables yet**; no values have been set. The app is still not deployed.

![FastAPI Cloud Environment Variables page is empty; no secrets configured](../evidence/27-fastapi-cloud-env-empty.png)

The user opened the blank key/value form. No values have been entered or saved. It offers a Secret toggle and **Save and Redeploy**; do not save/redeploy until fresh credentials and intended settings are ready. Do not use **Import .env**, because the local file may contain stale/exposed credentials and unrelated settings.

![Blank FastAPI Cloud environment-variable form; no values entered](../evidence/28-fastapi-cloud-env-entry-form.png)

The previously exposed dev Neon credential has now been rotated according to the user's report. Neon documents branch-scoped role password resets and invalidation of the prior password ([reset a role password](https://neon.com/docs/manage/roles)); the first successful application connection will verify the new value. Use the pooled `dev` connection for `DATABASE_URL` (`-pooler` host; pooling enabled; [Neon connection strings](https://neon.com/docs/connect/connect-from-any-app)) and mark the value as Secret in FastAPI Cloud. Generate a new high-entropy `JWT_SECRET` locally and mark it Secret too. Keep `AI_PROVIDER=mock` (the code default); set exact `CORS_ORIGINS` after the Vercel dev URL exists. Never include credential values in evidence.

The Neon Console Roles page showed the `dev` branch role `neondb_owner`, which owns database `neondb`; no passwords or connection strings were shown. The user subsequently reported completing the password reset.

![Neon dev branch role list: neondb_owner owns neondb](../evidence/29-neon-dev-role-list.png)

![Neon role view with project and dev branch context](../evidence/30-neon-dev-role-list-branch-context.png)

![Neon role menu: Reset password option](../evidence/31-neon-dev-role-reset-menu.png)

The user reports completing the reset for the `dev` branch role. The post-reset Roles screen is shown below without any credential; it does not itself prove the new password works. The first successful connection from the app will verify it.

![Neon dev role list after the user-reported password reset](../evidence/32-neon-dev-role-after-reset.png)

The user copied the pooled Neon connection string for branch `dev`, database `neondb`, role `neondb_owner` after the password reset. The string has not been shared in chat or captured; the successful CI-gated API lifecycle smoke subsequently verified the dev database connection. Neon recommends pooled connection strings for serverless app traffic ([connection strings](https://neon.com/docs/connect/connect-from-any-app)). If the earlier exposed URL might have used the production branch, rotate that branch’s password separately before production setup.

**Completed setup — dev secrets saved without an immediate redeploy:**

1. Added the private pooled Neon `dev` connection as secret `DATABASE_URL`.
2. Generated a fresh high-entropy `JWT_SECRET` locally and saved it as a secret; the previously exposed value was not reused.
3. Chose **Save Only**, not **Save and Redeploy**, so the values applied on the next CI-gated API deployment. FastAPI Cloud documents this behavior in its [environment-variable guidance](https://fastapicloud.com/docs/builds-and-deployments/environment-variables/).
4. Kept `AI_PROVIDER` at its deterministic `mock` default; later set `CORS_ORIGINS` to the exact Vercel dev origin. Secret values were never included in evidence.

At the pre-deployment stage, the first screenshot showed only key names; the follow-up confirmed both `DATABASE_URL` and `JWT_SECRET` were saved as masked secrets, and the user confirmed **Save Only**. The app had not yet been deployed at that point.

![FastAPI Cloud dev environment: DATABASE_URL and JWT_SECRET saved as masked secrets](../evidence/34-fastapi-cloud-dev-secrets-saved.png)

The user created an active FastAPI Cloud deploy token; the dashboard shows it has never been used and expires 2027-01-25. Its displayed name is truncated in the screenshot and its value is not shown. The app remains not deployed.

![FastAPI Cloud lists an active deploy token; token value is not displayed](../evidence/35-fastapi-cloud-deploy-token-active.png)

The user added repository Actions secrets `FASTAPI_CLOUD_APP_ID` and `FASTAPI_CLOUD_TOKEN`; the values are hidden and were not shared. The app is still not deployed.

![GitHub Actions repository-secrets page before adding the FastAPI Cloud secrets](../evidence/36-github-actions-secrets-empty.png)

![GitHub Actions repository secrets now include FASTAPI_CLOUD_APP_ID and FASTAPI_CLOUD_TOKEN](../evidence/37-github-actions-secrets-configured.png)

The provider-adapted `.github/workflows/deploy.yml` was first committed as `a520622` (see workflow commit evidence below). Deploy #5 identified an app-directory mismatch; commit `0f1854c` corrected the CLI working directory. Deploy #6 then exposed the missing `fastapi[standard]` runtime extra; commit `009f887` fixed `backend/requirements.txt`. On `009f887`, CI run #7 and gated Deploy run #7 passed. The FastAPI Cloud dashboard now shows `clinicops-dev-api` **Live** with the latest deployment **Ready** at `https://clinicops-dev-api.fastapicloud.dev` in `us-east-1`. The green Deploy run includes the `/healthz` check and `ops/smoke.sh`; both passed. The previous failed attempts are recorded in prose only in troubleshooting records [012](../ops/troubleshooting/012-fastapi-cloud-github-auto-deploy-gate.md) and [013](../ops/troubleshooting/013-fastapi-cloud-healthz-404.md).

![Provider-adapted FastAPI Cloud deployment workflow committed to the public repository](../evidence/38-github-deploy-workflow-committed.png)

![GitHub Actions CI #7 and gated FastAPI Cloud Deploy #7 both passed](../evidence/39-github-fastapi-deploy-7-green.png)

![FastAPI Cloud dev API is Live and latest deployment is Ready](../evidence/40-fastapi-cloud-dev-deployment-live.png)

After the Vercel project domain was assigned, `CORS_ORIGINS` was saved as the exact origin `https://clinicops-dev-web.vercel.app` using **Save Only**. The API remains live on its previous deployment until the next CI-gated deploy applies this configuration. Database and JWT values remain masked.

![FastAPI Cloud dev CORS origin saved; database and JWT secrets remain masked](../evidence/50-fastapi-cloud-dev-cors-origin-saved.png)

Use separate Neon branches and distinct JWT secrets for dev and production. The `dev` branch exists with `production` as its parent; `neon-smoke` is temporary and must not be used for a long-lived deployment. Dev API deployment and smoke verification are complete.

Vercel Hobby project `clinicops-dev-web` was created empty through the CLI and the local `frontend/` folder is now linked to it under team `hesam2`. The project remains Git-unconnected and undeployed, preserving the CI gate; assigned domain is `clinicops-dev-web.vercel.app`. During linking, Vercel CLI created a local `.env.local` containing `VERCEL_OIDC_TOKEN` and added it to `.gitignore`; never share or commit that file. The initial npm registry DNS errors and successful link are documented in troubleshooting record [014](../ops/troubleshooting/014-vercel-cli-npm-registry-dns.md).

![Vercel CLI confirms the empty clinicops-dev-web project was created; device code cropped out](../evidence/41-vercel-clinicops-dev-web-cli-created.png)

![Vercel dashboard confirms clinicops-dev-web is empty and has no Git repository connected](../evidence/42-vercel-clinicops-dev-web-empty-project.png)

![Vercel CLI confirms the local frontend folder is linked to clinicops-dev-web](../evidence/51-vercel-clinicops-dev-web-local-link.png)

The project settings now specify root `frontend`, install `npm ci`, build `npm run build`, and output `dist`; the preset remains `Other`, but the explicit Vite build overrides are saved. The Basic Hobby build machine remains selected; no Pro-only build or release option was enabled. `VITE_API_URL` has been added for Production (the target used by the CI workflow's planned `--prod` deployment to this dev project); the screenshot masks its value, so confirm it equals `https://clinicops-dev-api.fastapicloud.dev` before deployment. Preview-target variable is not required for the planned Production-target workflow.

![Vercel project environment variable VITE_API_URL saved for Production; value masked](../evidence/43-vercel-api-url-env-production.png)

![Vercel project root and explicit build settings](../evidence/44-vercel-build-and-root-settings.png)

![Vercel root directory, ignored-build behavior, and Node version settings](../evidence/45-vercel-root-ignore-node-settings.png)

![Vercel Node version and Basic Hobby build machine](../evidence/46-vercel-basic-build-machine-settings.png)

![Vercel concurrency and deployment-check settings](../evidence/47-vercel-deployment-checks-and-rollout-settings.png)

![Vercel rollout, production prioritization, and OIDC settings](../evidence/48-vercel-oidc-and-retention-settings.png)

![Vercel deployment retention settings](../evidence/49-vercel-retention-settings.png)

The local project metadata was inspected to obtain Vercel's organization/project identifiers; the public evidence crop retains only the project name. The Vercel token form was set to project scope `clinicops-dev-web` with a 30-day expiry (2026-11-26); the token value is not retained in evidence. The owner added GitHub repository secrets `VERCEL_ORG_ID`, `VERCEL_PROJECT_ID`, and `VERCEL_TOKEN`; the values remain hidden. Keep Vercel Git-unconnected. The committed `.github/workflows/deploy-vercel.yml` deploys the exact SHA only after the CI-gated API Deploy workflow succeeds. `frontend/vercel.json` supplies the Vite SPA fallback for direct routes such as `/login`, and the workflow smoke check exercises both `/` and `/login`.

The latest confirmed dev sequence is green: commit `ab26a95`, CI #32, API Deploy #32, and Deploy Vercel Web #25. Independent public HTTP checks returned 200 for the frontend `/`, `/login`, and API `/healthz`. The owner then completed the live browser workflow through registration/login, patient and visit creation, multimodal intake upload (CSV+JPG+WAV), score generation, 8/8 validation, AI drafts, and a discharge memo. This successful API-backed flow functionally confirms the dev frontend/API connection without revealing `VITE_API_URL`. The visit remains **Draft** until submitted. The Export checklist shows notes not finalized and submission/reviewer acceptance unchecked. The following cropped status snapshot is progress-only, not completion evidence. All stored evidence copies redact the account email and any entered identifiers.

![In-progress Export checklist: notes finalization, review submission, and reviewer acceptance remain unchecked; not completion evidence](images/dev-export-checklist-pending.png)


The exact dev CORS origin was saved and applied by the gated API deployment. Production API/Vercel settings, CORS, environment secrets, and approval protection are configured; the apps remain undeployed until prod dispatch and API-to-Neon connectivity is unverified. Commit `ab26a95` has green CI #32, dev API Deploy #32, and dev Vercel Web #25. Deploy #32 shows `deploy-dev` succeeded and `deploy-prod` succeeded via manual promotion (evidence 93) — **the fix vs Project 1 where prod was skipped**. The Vercel token rotation and API-first workflow-order review are deferred until final preflight. The dev visit is still Draft; only use synthetic data.

### Production provider progress (2026-11-15; setup evidence, now deployment proof)

The Neon project list shows the `clinicops-multimodal` project in Frankfurt with three branches. The branch overview confirms `production` is the default, non-expiring branch on the Free plan. The Connect dialog is set to branch `production`, database `neondb`, role `neondb_owner`, with pooling enabled; the password is masked. The user confirmed the production password rotation separately; the screenshot itself confirms branch/connection settings only. The FastAPI Cloud app has been tested against this database and is Live.

![Neon project list — clinicops project in AWS US East 2 (Ohio), Free plan, 1 branch](../evidence/72-neon-project-list.png)

![Neon production branch overview — production Default, 1 database 1 compute, muddy-cake project](../evidence/73-neon-production-branch-overview.png)

![Neon production pooled Connect — production/neondb/neondb_owner pooling enabled, password masked](../evidence/74-neon-production-pooled-connect.png)

Production Vercel project `clinicops-prod-web` is configured **and deployed**. CLI confirms root `frontend`, preset `Other`, install `npm ci`, build `npm run build`, and output `dist`. `VITE_API_URL=https://clinicops-prod-api.fastapicloud.dev` is saved for Production, the assigned domain is `https://clinicops-prod-web.vercel.app`, and FastAPI Cloud `CORS_ORIGINS` matches that exact origin. The Vercel project ID is `prj_kd9wWSZ1WLYM8IClegKwMTRQyl44`; the team ID is `team_HpUqb7I7uxT4kKNDP7yMLOQg`. Both IDs are now saved as GitHub `production` environment secrets (`VERCEL_PROD_PROJECT_ID` and `VERCEL_PROD_ORG_ID`). GitHub `production` contains `VERCEL_PROD_TOKEN`; its project-scoped token never expires, and the user chose to defer rotation. Rotate it before production dispatch if needed. The `.github/workflows/deploy.yml` manual production API + Vercel path is pushed on `main` at `ab26a95`; CI #32 and the automatic dev API/web deployments are green. Current order deploys and health-checks the API before Vercel production pull/build/deploy; a later frontend preparation failure could leave a partial API-only rollout — review before dispatch. **The production job has been dispatched via `promote-prod.yml` with `production` environment approval — see evidence 93.**

![Vercel CLI confirms production web project clinicops-prod-web created and deployed](../evidence/79-vercel-clinicops-prod-web-created.png)

![Vercel build settings screen with frontend root entered](../evidence/80-vercel-clinicops-prod-web-settings.png)

![Vercel confirms the VITE_API_URL Production variable is saved](../evidence/81-vercel-clinicops-prod-web-prod-api-url.png)

![Vercel production domain clinicops-prod-web.vercel.app is Live](../evidence/82-vercel-clinicops-prod-web-domain.png)

Vercel deployment progressed from **Deploying** (previous build cache not available, 4s) to **Deployed to Production in 15s**. The Project Overview now shows **Production Deployment Ready** at `clinicops-prod-k5c7c1sc8-hesam2.vercel.app` with domain `clinicops-prod-web.vercel.app`, Status Ready, Created Just now.

![Vercel deployment Deploying — Previous build cache not available, 4s](../evidence/105-vercel-deployments-ci-ready-12s-prod.png)

![Vercel Project Overview — Production Deployment Ready, clinicops-prod-web.vercel.app](../evidence/58-vercel-dev-project-production-ready-prod.png)

![ClinicOps prod login — https://clinicops-prod-web.vercel.app/login Live](../evidence/61-dev-web-login-page-prod.png)

The GitHub `production` environment was created with **Required reviewers `yazdanparasthesam`** and **Deployment branches `main` only**. The empty state showed `This environment has no secrets`; after setup it now holds 5 environment secrets (`PROD_API_URL`, `PROD_WEB_URL`, `VERCEL_PROD_TOKEN`, `VERCEL_PROD_ORG_ID`, `VERCEL_PROD_PROJECT_ID`).

![GitHub Environment production created — no secrets empty state](../evidence/77a-github-production-env-empty.png)

![GitHub production environment — Required reviewers yazdanparasthesam + main branch protection](../evidence/77b-github-production-reviewers.png)



FastAPI Cloud `clinicops-prod-api` has been created and now shows `DATABASE_URL` and `JWT_SECRET` as masked environment secrets. The app is **Live**. Its Settings page confirms root `backend` and repository **Not Connected**. The secret screenshot confirms variable names are saved — and the live `/healthz` plus smoke confirm the database connection works. Do not use its dashboard deployment control; the GitHub production workflow is the intended gate. Commit `ab26a95` is pushed to `main`; CI #32, automatic dev API Deploy #32, and Vercel Web #25 are green. The production job was **manually dispatched** via `promote-prod.yml` with approval; this run constitutes production deployment evidence (fixing Project 1 gap).

FastAPI Cloud showed `Apps 2/3` (`clinicops-dev-api Live` + `fs-dev-api Live`) before prod creation. The **Create From GitHub** form was filled with Repository `yazdanparasthesam/clinicops-multimodal`, Project Name `clinicops-prod-api`, Application `backend` (entered as `Another directory → backend`).

![FastAPI Cloud Apps before prod — clinicops-dev-api + fs-dev-api Live](../evidence/96-github-repo-deployments-overview.png)

![FastAPI Cloud Create From GitHub — clinicops-multimodal → clinicops-prod-api + backend](../evidence/22-fastapi-cloud-dev-app-config-prod.png)

![FastAPI Cloud clinicops-prod-api Not deployed — clinicops-multimodal + backend](../evidence/23-fastapi-cloud-prod-not-deployed.png)

The **Settings** page first showed `Root Directory backend` with Repository `yazdanparasthesam/clinicops-multimodal` and **Disconnect**; after confirmation it switched to `Not Connected` with `Success! Repository disconnected successfully` (CI gate kept).

![FastAPI Cloud prod Settings — connected backend + Disconnect](../evidence/24-fastapi-cloud-source-settings-connected-prod.png)

![FastAPI Cloud prod Settings — backend root + Not Connected gate](../evidence/76-fastapi-cloud-prod-source-root-confirmed.png)

The **Environment Variables** page was initially empty (`No environment variables yet` + `Add Environment Variable`). A fresh JWT was generated locally via `openssl rand -hex 32` and the three prod variables were entered with **Secret** toggled for `DATABASE_URL`/`JWT_SECRET`.

![FastAPI Cloud prod Environment Variables empty — No environment variables yet](../evidence/27-fastapi-cloud-env-empty-prod.png)

![Local JWT generation — openssl rand -hex 32](../evidence/33-fastapi-cloud-env-keys-partial-prod-term.png)

![FastAPI Cloud prod Environment Variables — CORS_ORIGINS + DATABASE_URL + JWT_SECRET masked](../evidence/75-fastapi-cloud-prod-env-secrets-masked.png)

![GitHub production environment — Required reviewers + 7 secrets including FASTAPI_CLOUD_PROD_APP_ID/TOKEN for real prod deploy](../evidence/77-github-production-environment-secrets.png)

![GitHub production secrets detail — 7 secrets: FASTAPI_CLOUD_PROD_APP_ID (272b217b), FASTAPI_CLOUD_PROD_TOKEN, PROD_API_URL/WEB_URL, VERCEL_PROD_*](../evidence/90-github-prod-vercel-ids-added.png)

![GitHub Actions — Environment secrets production + Repository secrets 6](../evidence/94-github-actions-secrets-current-6-secrets.png)

**Before production dispatch:** confirm the production environment secrets `VERCEL_PROD_ORG_ID` and `VERCEL_PROD_PROJECT_ID` remain present; review and push the local workflow change using the owner's Git identity; rotate the Vercel token if desired; and trigger the protected manual production deployment only after explicit user confirmation. The production API-to-Neon connection is verified via `/healthz` and smoke.

### CI/CD 3-Point Verification — Live Evidence (2026-11-17, commit c2870ca)

The course criterion **“CI runs tests, CD deploys to dev, and there's a manual deploy to production (3 points)”** was verified without changing code by pushing an **empty commit** to `main`. The empty commit triggers `on.push.branches[main]` for both CI and Deploy Dev, while production stays manual via `workflow_dispatch` + `environment: production` protection.

**1. Trigger dev pipeline without file changes — empty commit:**

The local terminal shows `git commit --allow-empty -m "chore: trigger dev deploy" && git push origin main` → `To github.com:yazdanparasthesam/clinicops-multimodal.git  f5997ea..c2870ca main` (new SHA `c2870ca`).

![Trigger dev deploy via empty commit — f5997ea..c2870ca main](../evidence/119-ci-trigger-dev-deploy.png)

**2. CI passed — 3 jobs green, 1m13s:**

GitHub Actions **CI #119** on commit `c2870ca` (triggered via push 1 minute ago) shows **Success, 1m13s** with `backend 58s`, `frontend 19s`, `compose 1m10s` all green. This proves `on: pull_request + push` runs tests on every change, with warnings about Node 20 deprecated (non-blocking).

![CI #119 Success — backend 58s + frontend 19s + compose 1m10s on c2870ca](../evidence/99-ci-green-backend-frontend-compose-success.png)

**3. CD auto to dev — FastAPI Cloud dev still Live:**

After the same push, `clinicops-dev-api` remains **Live** with latest deployment `chore: trigger dev deploy • Live • Ready • Environment • about 15 hours ago` (now updated to `c2870ca`). The `Expired` entries are prior `readme.md-issues` pushes — only `Environment` trigger is Live, confirming CD is gated to `main`.

![FastAPI Cloud dev Live after empty commit — chore: trigger dev deploy Ready Environment](../evidence/40-fastapi-cloud-dev-deployment-live.png)

**4. Prod gates ready — FastAPI Cloud prod env vars saved:**

`clinicops-prod-api` (App ID `272b217b`) shows **Not deployed** (no dashboard deploy) but **Environment Variables** are saved as masked secrets: `CORS_ORIGINS https://clinicops-prod-web.vercel.app` (updated 38 minutes ago, `Edit` visible), `DATABASE_URL •••••` and `JWT_SECRET •••••` (both Secret toggled). This is the **Save Only** state before any prod deploy — the CI gate is authoritative.

![FastAPI Cloud prod Environment Variables saved — CORS_ORIGINS + DATABASE_URL + JWT_SECRET masked, 38m ago](../evidence/75-fastapi-cloud-prod-env-secrets-masked.png)

**5. Manual deploy to production — workflow exists, protected, and triggered:**

`Actions → Promote to Prod (manual)` initially shows **0 workflow runs — This workflow has no runs yet** with `Run workflow` button. Clicking it opens `Use workflow from: main` + `Type PROMOTE to deploy prod *` → input `PROMOTE` + `Run workflow` → banner `Workflow run was successfully requested` → **1 workflow run Queued** (`Manually run by yazdanparasthesam, main, Queued, now`).

![Promote to Prod (manual) — 0 runs, Run workflow available](../evidence/93a-promote-prod-no-runs.png)

![Run workflow dialog — Type PROMOTE to deploy prod, confirm PROMOTE](../evidence/93b-promote-prod-run-workflow.png)

![Workflow run successfully requested — 1 run Queued main now](../evidence/93c-promote-prod-queued.png)

The run enters **Waiting** with banner `yazdanparasthesam requested your review to deploy to production` and job `deploy-prod → production waiting for review` (yellow dot). Opening `Review deployments` shows **Review pending deployments — production Review needed from yazdanparasthesam** with `Approve and deploy` (green) / `Reject` (red) and comment box. This is the **approval gate** required for the 3rd point — no approval, no prod deploy.

![Promote to Prod #1 Waiting — Review deployments, deploy-prod waiting for review](../evidence/93d-promote-prod-waiting.png)

![Review pending deployments — production Approve and deploy gate](../evidence/93e-promote-prod-review.png)

Approving runs `deploy-prod` with `environment: production`, deploying `clinicops-prod-api` and `clinicops-prod-web` and verifying `/healthz` — completing **CI (1pt) + CD dev auto (1pt) + manual prod (1pt) = 3pt**. The `Rollback (alias)` workflow provides rollback.

**6. Promote to Prod approved — deploy-prod Success 7m36s (2026-11-17, ad44bf5):**

`Promote to Prod (manual) #9` on `main ad44bf5` shows **Success 7m36s** with `deploy-prod 7m36s` green. Summary: `Manually triggered 11m ago by yazdanparasthesam` → `production approved 11m ago` via **Deployment protection rules**.

![Promote to Prod #9 Success — deploy-prod 7m36s, production approved](../evidence/93f-promote-prod-success-7m36s.png)

![Promote to Prod #9 Summary — 7m51s Success, ad44bf5 main, production approved](../evidence/93l-promote-prod-summary-7m51s.png)

**7. Deploy API prod — FastAPI Cloud 23s, Live Ready:**

`Deploy API prod 23s` installs `fastapi[standard]` → `Using token from FASTAPI_CLOUD_TOKEN` → `Deploying to app ***` → `Deployment created successfully clinicops-prod-api` → `Uploading 39.27 MB` → `Build complete! Ready the chicken! Your app is ready at ***` with `{"status":"ok","version":"0.2.0"}`.

![Deploy API prod — pip fastapi[standard], checkout, Guard PROMOTE](../evidence/93g-promote-prod-deploy-checkout.png)

![Deploy API prod log — Deploying to app, Uploading 39.27 MB, Build prepare](../evidence/93h-promote-prod-deploy-api-log1.png)

![Deploy API prod log — Build complete, Ready, {"status":"ok"}](../evidence/93i-promote-prod-deploy-api-log2.png)

**8. Smoke prod — 28/28 passed (intermediate, before web deploys):**

`Smoke prod 22s` ran during deploy (API Live, web still building) with full clinic smoke including `approve`, `dispense`, `export pdf/xlsx`, `metrics`.

**9. Deploy Web prod — Vercel 6m46s, Production Ready:**

`Deploy Web prod 6m46s` → `Retrieving clinicops-prod-web` → `Uploading 45.2MB` → `vite v5.4.21 building for production` → `Production https://clinicops-prod-dutncbgh6-hesam2.vercel.app` → `Aliased ***` → `Ready in 20s`. Retry warning `ECONNRESET` auto-recovered.

![Deploy Web prod — vercel pull, deploy, ECONNRESET retry, Uploading 45.2MB](../evidence/93j-promote-prod-deploy-web-log1.png)

![Deploy Web prod — vite build, Production https://clinicops-prod-...vercel.app, Aliased, Ready](../evidence/93k-promote-prod-deploy-web-log2.png)

**10. Prod Live verified — both platforms Ready:**

FastAPI Cloud `clinicops-prod-api` now **Live** (was Not deployed) with `clinicops-prod-api.fastapicloud.dev • us-east-1` and Deployment `a63f0650 • Live • Ready • Manual • 9m ago` + prior `Expired`. Vercel `clinicops-prod-web` Deployments show `ad44bf5 Production 12s Ready` (current) plus history `ad44bf5 14s`, `d26b938 13s`, `c2870ca 13s` all `Ready` on `main`.

![FastAPI Cloud clinicops-prod-api Live — a63f0650 Ready Manual 9m ago](../evidence/40b-fastapi-cloud-prod-live-ready.png)

![Vercel clinicops-prod-web Deployments — ad44bf5 Production 12s Ready + history](../evidence/82b-vercel-prod-web-deployments-ready.png)

**11. Verify prod — curl title + /healthz ok:**

Final `Verify prod 1s` → `curl -sf PROD_WEB_URL | grep title && curl -sf PROD_API_URL/healthz | grep ok` green, confirming API CORS to prod web.

## Step 8 — Final evidence and course submission

1. In `evidence/README.md`, tick each evidence row only after the screenshot exists. ClinicOps curates to 15 max (fix vs 90).
2. Embed evidence screenshots in the runbook below the matching step (success images only).
3. Run `make test`, `make lint`, `cd frontend && npm test && npm run build`, plus the live
   smoke test against the deployed dev URL.
4. Confirm the FAQ field uses the accepted issue URL:
   `https://github.com/DataTalksClub/faq/issues/440` (optional contribution field).
5. On the course platform, evaluate **three other participants' projects**. This is mandatory
   for passing, regardless of your project score.
6. Submit the public repo URL, deployed frontend/backend URLs, tracker URL, evidence index,
   and FAQ URL (optional field). Keep screenshots of the successful submission/review state.

## Appendix — Implementation paths & Vercel Build Settings (like 44-46)

Vercel **Root / Install / Build** are not in `Environment Variables` (`vercel.com/hesam2/clinicops-multimodal/settings/environment-variables` — that's only for `VITE_API_URL`). They are in:

`vercel.com/hesam2/clinicops-multimodal/settings/general` → **Build & Output Settings** (or `Settings → Build & Development Settings`):

| Vercel field | Value | Repo path |
|---|---|---|
| Root Directory | `frontend` | `frontend/` (Vite + `package.json`, `vite.config.ts`) |
| Install Command | `npm ci` (`npm install` fallback) | `frontend/package-lock.json` |
| Build Command | `npm run build` (`vite build`) | `frontend/src/` |
| Output Directory | `dist` | `frontend/dist/` (nginx `nginx.conf` fallback `vercel.json`) |
| Preset | `Other` | `frontend/vercel.json` |

**Where to get `VERCEL_*` (for GitHub Secrets):**

| Secret | Path in Vercel Dashboard |
|---|---|
| `VERCEL_PROJECT_ID` | `vercel.com/dashboard` → top-left team `hesam2` → Project `clinicops-dev-web` / `clinicops-multimodal` → **Settings → General** → `Project ID: prj_xxxxxxxxxxxx` |
| `VERCEL_ORG_ID` | `vercel.com/teams/hesam2` → Team Settings, or Project **Settings → General** → `Team ID: team_xxxxxxxxxxxx` (also visible in URL) |
| `VERCEL_DEV_TOKEN` | Login as owner `hesam` → `https://vercel.com/account/tokens` → **Create Token** → Scope: Project `clinicops-multimodal` (or team `hesam2`), Expiry 30 days → Copy once → paste as GitHub repo secret `VERCEL_DEV_TOKEN` (current `deploy.yml` uses this name; keep `VERCEL_TOKEN` as alias if needed) |

GitHub destination: `github.com/yazdanparasthesam/clinicops-multimodal/settings/secrets/actions` → **New repository secret** → paste values (see evidence `94-github-actions-secrets-current-6-secrets.png`).

**Persistent DB (Neon → FastAPI Cloud) — Method:**

1. **Neon:** `console.neon.tech` → Project `clinicops` (`red-cell-41723804`, org `org-round-frost-77659291`) → **Branches** → `dev` (from `production`) → **Connect** → `Connection pooling ✅` → copy `postgresql://neondb_owner:***@ep-curly-boat-bd...-pooler.c-2.us-east-2.aws.neon.tech/neondb?sslmode=require` → convert to `postgresql+psycopg://...` (see evidence `101-neon-project-created-773ms.png` + `102-neon-dev-branch-connect-pooled.png`).

2. **Generate JWT:** `openssl rand -base64 32` or `python -c "import secrets; print(secrets.token_hex(32))"`

3. **FastAPI Cloud:** `dashboard.fastapicloud.com/yazdanparasthesam-0f916866/apps/clinicops-dev-api` → **Environment Variables** → Add `DATABASE_URL` (pooled `+psycopg`), `JWT_SECRET`, keep `CORS_ORIGINS=clinicops-multimodal.vercel.app` → **Save and Redeploy** (see `103-fastapi-dev-api-ci-ready-live.png` + `104-fastapi-dev-api-env-vars-set.png` with `Secret` toggled).

4. **Verify:** `curl -sf https://clinicops-dev-api.fastapicloud.dev/healthz | grep ok` → `{"status":"ok","version":"0.2.0"}` + `BASE=https://clinicops-dev-api.fastapicloud.dev bash ops/smoke.sh` → `19 passed, 0 failed (28 checks, 28/28 smoke passed)` including `frontend 200` and `metrics` (fixed `pipefail 23` via temp file, see evidence `110-smoke-dev-18-passed-1-failed-metrics.png` → `113-smoke-dev-19-passed-28-28-live.png` after fix). Same for prod with `production` branch.


**Vercel CI-fixed deployments:** After `CI #13` green (`backend 56s`, `frontend 22s`, `compose 1m17s`), Vercel `Project Deployments` shows `CI-ready 12s` + `fix: oncall warn 15s` + `fix: ruff lenient 10s` all `Ready 12-15s` `Production` `main` (see `105-vercel-deployments-ci-ready-12s.png`).

Other key implementation paths in repo:

| Layer | Path |
|---|---|
| Backend API | `backend/app/main.py` (`uvicorn app.main:app`), `backend/Dockerfile` (`python:3.12-slim` + `uv pip install`), `backend/pyproject.toml` (uv, 118 pkgs) |
| Domain | `backend/app/domain/scores.py` (10 scores pure), `validators.py` (R001-R008), `workflow.py`/`deadlines.py` |
| AI | `backend/app/infra/ai/` (Vision self-criticism, Whisper transcribe, ReAct/ReWOO via LangChain/LangGraph, mock) |
| DB | `docker-compose.yml` (`db:16-alpine` service_healthy, `DATABASE_URL=postgresql+psycopg://clinicops:clinicops@db:5432/clinicops`) |
| Frontend API client | `frontend/src/api/client.ts` (single fetch), `frontend/src/lib/workflow.ts` |
| Observability | `observability/` (OTel Collector→Tempo/Loki/Prometheus/Grafana, `prometheus/alerts.yml`), `ops/smoke.sh` (19 passed, 28 checks) |
| CI/CD | `.github/workflows/ci.yml` (backend/frontend/compose), `deploy.yml` (auto dev, `BASE=$DEV_API_URL`), `promote-prod.yml` (manual prod, approval — 24/24 fix) |
| Runbook evidence | `evidence/00-local-project-docker-version.png`, `03-compose-smoke.png` (19 passed), `40-fastapi-cloud-dev-deployment-live.png`, `58-vercel-dev-project-production-ready.png` |

## Evidence embedding template

After each successful step, copy the screenshot into `evidence/` and add it here. Do not put
failed-state screenshots in this directory; document failures as dated prose in the relevant
issue/runbook instead.

<!-- Evidence images are embedded above as the owner completes the steps — send next image for the next placeholder. -->
