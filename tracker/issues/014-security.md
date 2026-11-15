---
title: "Security hardening + no-PII telemetry"
labels: [security]
milestone: "M7 — Ship"
state: closed
agent: "Arena Agent"
---

## Goal
No secrets, no PII, allowlist.

## Acceptance criteria
- [x] telemetry-policy, ai-data-policy, credentials-handling
- [x] Law 9 MIME allowlist, magic sniff, EXIF strip

## Agent evidence log
- Verified: test_telemetry_policy, gitleaks
