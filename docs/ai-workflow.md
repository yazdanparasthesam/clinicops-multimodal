# AI-Assisted Development Workflow

## Tooling

| Tool | Role |
|---|---|
| Arena.ai Agent Mode | Architecture, implementation, testing, docs |
| GitHub Copilot CLI | Batch code generation |
| Google Gemini 2.0 Flash + Vision | Runtime AI — LangChain provider behind self-criticism, ReAct, ReWOO |

## Context files

1. `AGENTS.md` 2. `product-spec.md` 3. `openapi.yaml` 4. `docs/architecture.md`

## Delegation pattern

```
human: goal + constraints → agent: plan → implement → self-review (lint/test) → report evidence → human: run live, screenshot
```

## Manual review & verification

- ruff clean; backend pytest 74; frontend vitest 27; tsc + build; seed arithmetic hand-checked; 6 real defects caught logged.

## Prompt log (representative)

1. "Build ClinicOps multimodal clone of financial-statement structure with image+voice ingestion."
2. "Rebuild AI layer on LangChain/LangGraph with vision self-criticism, Whisper transcribe, ReAct/ReWOO; keep mock deterministic."

## Runtime AI governance

- LangChain provider abstraction + deterministic mock (`AI_PROVIDER=mock`).
- Three patterns bounded/read-only: self-criticism (≤2 loops), ReAct (6 tools), ReWOO (≤8 steps).
- Every call logged to `ai_requests` with redaction.
- Human-in-the-loop: vision/transcript drafts require finalize; never mutates scores/validations/workflow.

See `security/ai-data-policy.md` and `docs/permissions.md`.
