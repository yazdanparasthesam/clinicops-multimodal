# AGENTS.md — Instructions for coding agents working on ClinicOps Multimodal

You are operating on a course-project codebase that is graded on structure, contracts, tests, and documentation. Follow these rules exactly; they encode decisions that must not drift.

## Project in one paragraph

ClinicOps turns multimodal patient intake (CSV vitals/labs/meds + JPG/PNG wound/derm photos + WebM/MP3/WAV voice memos + PDF labs) into validated SOAP notes and prescriptions, computes 10 clinical scores deterministically, validates against 8 rules, assists with AI (vision finding drafts, transcript structuring, discharge notes, mapping suggestions, grounded chat) — never computing numbers — and runs a nurse→doctor→pharmacist workflow with audit trail. FastAPI backend, React frontend, SQLite/Postgres, LangChain/LangGraph AI layer (Gemini Vision / Whisper or deterministic mock; self-criticism, ReAct, ReWOO), Docker Compose, GitHub Actions.

## Documentation map (read the module you are touching)

| Doc | Read it when… |
|---|---|
| [product-spec.md](product-spec.md) | touching rules R001–R008, journeys, personas, glossary |
| [docs/architecture.md](docs/architecture.md) | touching layers, data model, ADR-lite decisions (1–9) |
| [docs/ai-workflow.md](docs/ai-workflow.md) | touching prompts, graphs, provider behavior, multimodal agents |
| [docs/testing.md](docs/testing.md) | writing/fixing tests, markers, fixtures |
| [docs/deployment.md](docs/deployment.md) | touching CI/CD, FastAPI Cloud/Vercel/Neon, secrets, rollback |
| [docs/observability.md](docs/observability.md) | touching metrics/logs/traces, the obs compose profile, alerts |
| [docs/operations.md](docs/operations.md) | runbooks, diagnostics, drills, data ops |
| [docs/agent-team.md](docs/agent-team.md) | who (which agent) does what; handoff artifacts |
| [docs/agent-extension-pack.md](docs/agent-extension-pack.md) + [docs/permissions.md](docs/permissions.md) | MCP server, hooks, subagent, permission matrix |
| [security/](security/) | telemetry privacy policy, AI data policy, agent security, credentials handling, multimodal scan policy |
| [tracker/](tracker/) | the task queue: issues with acceptance criteria + evidence logs |

## Non-negotiable laws

1. **The AI never computes.** Any number that appears in scores, validations, checklist, or deadline MUST come from `backend/app/domain/*` (pure functions). LLM output is prose only. If a task seems to need model arithmetic, stop and re-read this rule.
2. **The contract is frozen.** `openapi.yaml` at the repo root is the source of truth. After ANY router/schema change run `make openapi` and commit the regenerated file. The CI contract test fails on drift — never edit the yaml by hand to make a test pass.
3. **Suggestions ≠ mutations.** AI mapping suggestions and vision/transcript drafts are returned to the client; only a human action (`PATCH ...` or `POST .../finalize`) changes data. Never auto-apply model output.
4. **Every LLM call goes through `services/ai_service`** (`call_ai`, `run_vision_draft`, `run_transcribe_structured`, `run_notes_draft`, `run_chat`, `run_audit_memo`) — each logs to `ai_requests` and redacts identifiers. Do not call providers or graphs directly from routers.
5. **Secrets never enter the repo.** `.env` is gitignored; `.env.example` holds placeholders. If you see a real key anywhere, remove it, say so loudly, and advise rotation.
6. **Gates stay deterministic.** Submit/approve/dispense blocking logic lives in `routers/workflow.py::_gate_errors` + `domain/workflow.py`. Don't soften gates.
7. **Agent loops are bounded; agent tools are read-only.** The self-criticism revise loop is capped by `Settings.ai_max_critique_loops` (default 2); the ReWOO executor runs at most `max_steps` planned tools and drops unknown names. Tools in `ai_service.tools_registry` only serialize deterministic domain output — never add a mutating tool, never let a model request one, and never raise the caps to make a failing test pass.
8. **Telemetry describes the system, never the patient.** The log formatter emits only its whitelist (`method, route, status, duration_ms, step, rule_id, modality`) — do not add fields carrying patient data, names or figures; metric labels come from fixed enumerations only. The on-call agent's command allowlist (`oncall-agent/agent.py`) is a security control: never extend it to make a drill pass. Both contracts are unit-tested and specified in `security/telemetry-policy.md`.
9. **Multimodal files never execute.** `infra/attachments.validate_and_store()` enforces MIME allowlist (`image/jpeg,image/png,audio/webm,audio/wav,audio/mpeg,application/pdf,text/csv`), 10MB cap, filename sanitization, EXIF strip, hash dedup. Never trust client `Content-Type` alone; sniff magic bytes. Never store executables.

## Layer rules (backend)

```
routers/    HTTP concerns ONLY: parse, authorize (deps), call services, shape responses
services/   orchestration: pipeline.py (intake/scores/validate/checklist), ai_service.py, audit.py
domain/     PURE business logic, no imports from routers/services/infra, no IO (scores, validators, workflow, deadlines, multimodal metrics)
infra/      IO adapters: attachments (files), ai (providers/graphs), exports (pdf/xlsx), telemetry
```

Dependency direction is strictly inward: routers → services → domain; infra is used by services/routers at the edges. `models.py`/`schemas.py`/`db.py`/`deps.py`/`security.py`/`config.py` are the shared kernel. New validation rule = new R-id in `domain/validators.py` + unit test + row in product-spec.md §5.

## Frontend rules

- ALL HTTP goes through `src/api/client.ts` (`api.*` + `download`). Never call `fetch` from a component.
- Types in `src/api/types.ts` mirror `openapi.yaml`.
- Pure UI logic lives in `src/lib/*` and gets a vitest suite in `src/lib/__tests__/`.
- The workflow mirror in `src/lib/workflow.ts` is a UI hint; the server always re-checks.
- Styling: Tailwind utilities + the `.card/.btn/.input/.label/.th/.td` classes in `index.css`.
- Attachments: dropzone + audio recorder components use `api.uploadAttachment()` only; never post `FormData` directly.

## Definition of done for any change

1. `cd backend && ruff check app tests scripts` → clean.
2. `cd backend && python -m pytest` → all green (unit + integration + contract).
3. `cd frontend && npm test && npm run build` → green.
4. `python -m pytest oncall-agent/tests -q` → green (or `make test`, which includes it).
5. `make openapi` → commit the regenerated file if it changed.
6. Docs touched when behavior changed: product-spec.md (rules/FRs), docs/ai-workflow.md (if prompts/AI behavior changed), docs/observability.md (if signals/alerts changed), README (if user-visible flow changed).

## Testing conventions

- Unit tests: pure domain only, no DB/HTTP, `@pytest.mark.unit`, in `backend/tests/unit/`.
- Integration: real app + DB via TestClient, `@pytest.mark.integration`, in `backend/tests/integration/`. Fixtures in `tests/conftest.py` (env is set BEFORE app import; AI is always mock in tests; emails must use `@example.com`; fixtures include `lesion-sample.jpg` + `memo-sample.webm`).
- Dates: never hardcode today-relative assertions; derive from `date.today()` (see the `CUR_FY` pattern).
- Frontend: vitest, node environment, stub `fetch` with `vi.stubGlobal`.

## Useful context

- Demo story: adult patient with wound + voice memo + labs → R002 dose-range + R005 missing-consent initially → fixed after reviewer note. Files in `seed/` + `evidence/fixtures/`, seeder in `backend/scripts/seed_demo.py`.
- `ops/smoke.sh` exercises the full lifecycle over HTTP against any deployment — including multimodal uploads.
- Telemetry: metrics on `/metrics` are ALWAYS on; traces/OTLP logs only when `OTEL_ENABLED=true` (compose `--profile obs` ships collector/Tempo/Loki/Prometheus/Alertmanager/Grafana). Journey hooks live in `app/infra/telemetry/` + service call sites.
- The on-call responder (`oncall-agent/`) is deterministic — alertname → runbook → allow-listed command → verify → report in `ops/incidents/`. Drill: `./ops/alert-drill.sh [--simulate]`.
- Commit style: conventional commits (`feat:`, `fix:`, `test:`, `docs:`, `ci:`).

