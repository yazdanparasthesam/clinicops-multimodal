from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..db import get_db
from ..models import Visit
from ..deps import get_current_user
from ..models import User
from ..services.ai_service import run_vision_draft, run_notes_draft, run_chat, run_audit_memo, run_transcribe_structured
from ..schemas import AIDraftIn, AIDraftOut
try:
    from ..infra.telemetry.metrics import observe_ai_call, observe_journey_step
except Exception:
    observe_ai_call = observe_journey_step = lambda *a, **k: None

router = APIRouter(prefix="/visits/{visit_id}/ai", tags=["ai"])

@router.post("/vision-draft", response_model=AIDraftOut)
def vision_draft(visit_id: int, payload: AIDraftIn = None, db: Session=Depends(get_db), user: User=Depends(get_current_user)):
    v = db.query(Visit).filter(Visit.id==visit_id).first()
    if not v: raise HTTPException(status_code=404, detail="Not found")
    content = run_vision_draft(db, v)
    try:
        observe_ai_call("vision_draft", "mock", "ok", 0.12)
        observe_journey_step("vision_draft", 0.12)
    except Exception:
        pass
    return AIDraftOut(kind="vision_draft", content=content, model="mock", latency_ms=120)

@router.post("/transcribe", response_model=AIDraftOut)
def transcribe(visit_id: int, payload: dict, db: Session=Depends(get_db), user: User=Depends(get_current_user)):
    v = db.query(Visit).filter(Visit.id==visit_id).first()
    if not v: raise HTTPException(status_code=404, detail="Not found")
    transcript = payload.get("transcript") or "Sample dictated note for testing."
    conf = payload.get("confidence", 0.92)
    content = run_transcribe_structured(db, v, transcript, confidence=conf)
    try:
        observe_ai_call("transcribe", "mock", "ok", 0.2)
        observe_journey_step("transcribe", 0.2)
    except Exception:
        pass
    return AIDraftOut(kind="transcribe", content=content, model="mock", latency_ms=200)

@router.post("/notes-draft", response_model=AIDraftOut)
def notes_draft(visit_id: int, payload: AIDraftIn = None, db: Session=Depends(get_db), user: User=Depends(get_current_user)):
    v = db.query(Visit).filter(Visit.id==visit_id).first()
    if not v: raise HTTPException(status_code=404, detail="Not found")
    content = run_notes_draft(db, v)
    try:
        observe_ai_call("notes_draft", "mock", "ok", 0.15)
        observe_journey_step("notes_draft", 0.15)
    except Exception:
        pass
    return AIDraftOut(kind="notes_draft", content=content, model="mock", latency_ms=150)

@router.post("/chat", response_model=AIDraftOut)
def chat(visit_id: int, payload: dict, db: Session=Depends(get_db), user: User=Depends(get_current_user)):
    v = db.query(Visit).filter(Visit.id==visit_id).first()
    if not v: raise HTTPException(status_code=404, detail="Not found")
    query = payload.get("query","Show visit status")
    content = run_chat(db, v, query)
    try:
        observe_ai_call("chat", "mock", "ok", 0.09)
        observe_journey_step("chat", 0.09)
    except Exception:
        pass
    return AIDraftOut(kind="chat", content=content, model="mock", latency_ms=90)

@router.post("/audit-memo", response_model=AIDraftOut)
def audit_memo(visit_id: int, payload: AIDraftIn = None, db: Session=Depends(get_db), user: User=Depends(get_current_user)):
    v = db.query(Visit).filter(Visit.id==visit_id).first()
    if not v: raise HTTPException(status_code=404, detail="Not found")
    content = run_audit_memo(db, v)
    return AIDraftOut(kind="audit_memo", content=content, model="mock", latency_ms=180)
