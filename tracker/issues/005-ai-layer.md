---
title: "AI layer: Vision self-criticism, Whisper, ReAct, ReWOO + Mock"
labels: [ai,backend]
milestone: "M4 — AI"
state: closed
agent: "Arena Agent"
---

## Goal
Multimodal AI assist — AI never computes.

## Acceptance criteria
- [x] AI_PROVIDER=mock|gemini; MockChatModel deterministic
- [x] Self-criticism loop max 2
- [x] ReAct 6 tools, ReWOO ≤8 steps, all via ai_service with redaction

## Agent evidence log
- Arena Agent — designed graphs + providers + prompts.
- Verified: test_vision_and_transcribe MOCK content
