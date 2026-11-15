from typing import Optional
import time, hashlib
from ...config import settings

class MockChatModel:
    """Deterministic mock — same surface as LangChain chat model"""
    def invoke(self, prompt: str) -> str:
        h = hashlib.sha256(prompt.encode()).hexdigest()[:6]
        if "vision" in prompt.lower():
            return f"[MOCK Vision {h}] Erythematous lesion 2cm left forearm, well-demarcated, no necrosis. Recommend photo follow-up in 48h."
        if "transcribe" in prompt.lower() or "transcript" in prompt.lower():
            return f"[MOCK Transcript {h}] 45yo male chest pain, Wells 2, vitals stable, plan ECG and D-dimer."
        if "critique" in prompt.lower():
            return f"[MOCK Critique {h}] Add anatomical location and measurement precision; avoid definitive diagnosis."
        if "react" in prompt.lower():
            return f"[MOCK ReAct {h}] Based on scores: BMI 24.8, eGFR 88, MAP 93. No immediate red flag."
        if "rewoo" in prompt.lower():
            return f"[MOCK ReWOO {h}] Plan executed: 3 tools read; summary: visit ready for review, R007 warn only."
        return f"[MOCK {h}] Discharge summary draft: patient stable, follow-up in 72h, prescription reviewed."

def get_provider():
    if settings.ai_provider == "mock":
        return MockChatModel()
    # Gemini branch — lazy import
    try:
        from langchain_google_genai import ChatGoogleGenerativeAI
        return ChatGoogleGenerativeAI(model=settings.gemini_model, google_api_key=settings.gemini_api_key)
    except Exception:
        return MockChatModel()
