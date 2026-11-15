# Testing

## Pyramid

| Level | Where | Count |
|---|---|---|
| Unit (domain + AI graphs + telemetry) | `backend/tests/unit/` | 62 |
| Integration (API+DB+multimodal) | `backend/tests/integration/` | 12 |
| Contract | `backend/tests/integration/test_contract.py` | 2 |
| Frontend core logic | `frontend/src/**/__tests__/` | 27 |
| E2E smoke | `ops/smoke.sh` | 1 script (28 checks incl image+audio) |

Separation by markers `unit`, `integration`.

## Running

```bash
make test              # backend + oncall
make frontend-test     # vitest
make test-all          # all + compose integration
cd backend && python -m pytest tests/unit -k test_scores -q
cd backend && python -m pytest tests/integration -k test_visit_lifecycle -q
```

## Fixtures

- `evidence/fixtures/lesion-sample.jpg` (2KB valid JPEG)
- `evidence/fixtures/memo-sample.webm` (42s stub)
- `seed/demo-intake.csv` — vitals/labs/meds that trigger R002,R007
- All integration tests use `AI_PROVIDER=mock` (no external calls).

## Matrix

| Test file | Covers |
|---|---|
| test_scores.py | BMI, eGFR, MAP, etc. pure + edge |
| test_validators.py | R001-R008 each |
| test_workflow.py | gates, 422 on failing error-rules |
| test_attachments.py | MIME, size, magic bytes, dedup, thumb |
| test_multimodal.py | CSV+JPG+WAV → scores/validations |
| test_api_auth.py | RBAC 403 matrix |

