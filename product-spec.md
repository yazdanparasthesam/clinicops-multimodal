# Product Specification — ClinicOps Multimodal

## 1. Problem & Users

See README §Problem Statement. Users: **Nurse** (triage + uploads), **Doctor** (reviews, AI drafts, approves), **Pharmacist** (dispenses). All authenticated via JWT.

## 2. Journeys

**J1 — Multimodal Intake:** Nurse creates Visit → uploads CSV (vitals/labs/meds) + JPG (wound) + WebM (dictation) + PDF → system maps columns, computes scores, runs validations, shows anomalies → AI drafts (vision + transcript) available.
**J2 — Review:** Doctor triggers AI drafts (vision self-criticism, transcribe), edits, resolves comments → submits → reviewer approves → pharmacist dispenses.
**J3 — Timeline & Exports:** Checklist + deadline 72h + Rx expiry → PDF/XLSX exports.

## 3. Features & Acceptance Criteria

| ID | Feature | AC |
|---|---|---|
| FR01 | Create Visit | `POST /visits` with patient demographics creates draft; GET lists with filters |
| FR02 | Multimodal Attachments | `POST /visits/{id}/attachments` accepts `image/jpeg,image/png,audio/webm,audio/wav,audio/mpeg,application/pdf,text/csv` ≤10MB; invalid MIME/size → 400; stored with hash+thumb |
| FR03 | Ingestion & Mapping | CSV columns auto-mapped to vitals/labs/meds; suggestion returned, human PATCH applies |
| FR04 | Clinical Scores (10) | BMI, eGFR (CKD-EPI), MAP, CCI, Wells, APGAR, Dose/kg, BSA, Adherence, RiskScore computed deterministically; formulas unit-tested |
| FR05 | Validations R001-R008 | See §5; error-rules block submit/approve; warn-rules show but don't block |
| FR06 | AI Vision Draft | `POST /visits/{id}/ai/vision-draft` runs self-criticism (≤2 loops) over latest JPG; returns draft prose; logged to ai_requests |
| FR07 | AI Transcription | `POST /visits/{id}/ai/transcribe` runs Whisper mock/real → transcript + structured SOAP fields + confidence; low confidence triggers R006 warn |
| FR08 | AI Notes & Chat | Discharge notes via self-criticism; ReAct chat over 6 read-only tools; all logged/redacted |
| FR09 | Workflow | draft→submitted→in_review→approved→dispensed / changes_requested↔rejected; gates deterministic; audit log |
| FR10 | Comments | Line-anchored comments, resolve; role-checked |
| FR11 | Checklist & Deadlines | 72h close deadline; Rx expiry; checklist computed |
| FR12 | Exports | PDF Rx + XLSX visit; Bearer-authenticated; deterministic content |
| FR13 | Auth & RBAC | JWT login; nurse/doctor/pharmacist matrix enforced (403 otherwise) |

## 4. Data Model

| Table | Purpose |
|---|---|
| users | id, email, password_hash, role |
| visits | id, patient_name, dob, status, created_by, deadline_at, scores_json |
| attachments | id, visit_id, kind (csv/image/audio/pdf), filename, mime, size, sha256, thumb_path, stored_path |
| validations | id, visit_id, rule_id, severity, message, field |
| audit_log | id, visit_id, from_status, to_status, actor, at |
| ai_requests | id, visit_id, kind, provider, model, prompt_hash, status, latency_ms |
| comments | id, visit_id, author, body, anchor, resolved |

## 5. Rules R001-R008

| Rule | Severity | Description |
|---|---|---|
| R001 | error | Drug-allergy conflict (patient allergy vs prescription) |
| R002 | error | Dose out of allowed range (dose/kg) |
| R003 | error | Known drug interaction |
| R004 | warn | Duplicate therapy |
| R005 | error | Image without consent flag |
| R006 | warn | Transcript confidence <0.6 |
| R007 | warn | Vitals out of physiological range |
| R008 | error | Missing required vitals for score |

New rule = new R-id + domain/validators.py + test + row here.

## 6. API

Source of truth: `openapi.yaml` (generated via `make openapi`). Base `/api` proxied by frontend Nginx. Health: `GET /healthz` (no auth), metrics: `GET /metrics` (no PII), docs: `/docs`.

## 7. Non-Goals

- Real DICOM PACS, HL7 FHIR, e-prescription network
- AI diagnosis (AI only drafts findings, human diagnoses)
- Real payment/billing, insurance claims

## 8. Glossary

- **SOAP:** Subjective/Objective/Assessment/Plan note
- **Wells:** DVT risk score (deterministic)
- **eGFR:** estimated glomerular filtration rate (CKD-EPI)
- **Self-criticism:** draft→critique→bounded revise agent pattern
- **ReAct:** Reason+Act loop over tools; **ReWOO:** Plan→Execute→Solve

