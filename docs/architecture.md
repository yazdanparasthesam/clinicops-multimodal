# Architecture

## Layers

```
routers/  → services/ → domain/ → infra/
                ↘ infra/ai, infra/attachments
```

## Data Model

See product-spec.md §4. `models.py` defines SQLAlchemy tables; `schemas.py` defines Pydantic I/O; `db.py` provides session.

## Attachments Flow

`POST /visits/{id}/attachments` → `infra/attachments.validate_and_store()` → checks MIME allowlist, size, magic bytes, sanitizes filename, strips EXIF, generates thumb (Pillow), computes sha256, dedup check → writes to `/data/attachments/{visit_id}/{hash}.bin` + DB row → `services/pipeline.py` recomputes scores/validations.

## AI Layer

`services/ai_service.py` is sole gateway: `call_ai()`, `run_vision_draft()`, `run_transcribe_structured()`, `run_notes_draft()`, `run_chat()`, `run_audit_memo()`. Providers: `infra/ai/providers.py` (Gemini + Vision + Whisper mock). Graphs: `infra/ai/graphs.py` (self-criticism, ReAct, ReWOO) — all bounded, read-only tools.

## ADR-lite

1. SQLite local / Postgres Compose/Prod — zero friction + prod grade.
2. Local volume for attachments (S3-ready via env `STORAGE_BACKEND=s3`).
3. Deterministic mock AI for CI (no keys).
4. Single `api/client.ts` for frontend.
5. Nginx frontend proxies `/api` → backend.
6. OTel always-on metrics, traces/logs opt-in via `OTEL_ENABLED`.
7. One Docker image for backend, one for frontend+nginx.
8. RBAC via `deps.get_current_user` + role checks in routers.
9. Audit log + ai_requests for every decision.

