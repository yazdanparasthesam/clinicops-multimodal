import time, datetime
from sqlalchemy.orm import Session
from ..models import AIRequest, Visit, Attachment, Validation
from ..infra.ai.providers import get_provider
from ..infra.ai.graphs import self_criticism_loop, react_agent, rewoo_agent
from ..infra.ai.prompts import VISION_PROMPT, TRANSCRIBE_PROMPT, NOTES_PROMPT, CHAT_SYSTEM, AUDIT_PROMPT
from ..security import hash_prompt
from ..config import settings

def _log(db: Session, visit_id, kind, prompt, start):
    latency = int((time.time()-start)*1000)
    db.add(AIRequest(visit_id=visit_id, kind=kind, provider=settings.ai_provider, model=settings.gemini_model if settings.ai_provider!="mock" else "mock", prompt_hash=hash_prompt(prompt), status="ok", latency_ms=latency))
    db.commit()
    return latency

def call_ai(prompt: str, provider=None):
    prov = provider or get_provider()
    if hasattr(prov, "invoke"):
        return prov.invoke(prompt)
    return str(prov)

def run_vision_draft(db: Session, visit: Visit):
    start = time.time()
    atts = db.query(Attachment).filter(Attachment.visit_id==visit.id, Attachment.kind=="image").all()
    if not atts:
        return "No image attachment found for vision draft."
    context = f"Visit {visit.id}, image {atts[-1].filename}, SHA {atts[-1].sha256[:8]}, scores {visit.scores_json}"
    prompt = VISION_PROMPT.format(context=context)
    content = self_criticism_loop(prompt)
    _log(db, visit.id, "vision_draft", prompt, start)
    # do not auto-mutate; caller stores as vision_finding draft
    visit.vision_finding = content
    db.commit()
    return content

def run_transcribe_structured(db: Session, visit: Visit, transcript_text: str, confidence: float=0.92):
    start = time.time()
    scores = visit.scores_json
    prompt = TRANSCRIBE_PROMPT.format(transcript=transcript_text, confidence=confidence, scores=scores)
    content = self_criticism_loop(prompt)
    _log(db, visit.id, "transcribe", prompt, start)
    visit.transcript = transcript_text
    visit.transcript_confidence = confidence
    # optionally fill notes_draft
    visit.notes_draft = content
    db.commit()
    return content

def run_notes_draft(db: Session, visit: Visit):
    start = time.time()
    validations = db.query(Validation).filter(Validation.visit_id==visit.id).all()
    prompt = NOTES_PROMPT.format(scores=visit.scores_json, validations=[v.rule_id for v in validations], visit={"id":visit.id,"patient_name":visit.patient_name})
    content = self_criticism_loop(prompt)
    _log(db, visit.id, "notes_draft", prompt, start)
    visit.notes_draft = content
    db.commit()
    return content

def run_chat(db: Session, visit: Visit, query: str):
    start = time.time()
    tools_registry = build_tools_registry(db, visit)
    content = react_agent(query, tools_registry)
    _log(db, visit.id, "chat", query, start)
    return content

def run_audit_memo(db: Session, visit: Visit):
    start = time.time()
    tools_registry = build_tools_registry(db, visit)
    prompt = AUDIT_PROMPT.format(tools=list(tools_registry.keys()), visit={"id":visit.id,"status":visit.status})
    content = rewoo_agent(prompt, tools_registry)
    _log(db, visit.id, "audit_memo", prompt, start)
    return content

def build_tools_registry(db: Session, visit: Visit):
    def get_visit():
        return {"id":visit.id,"status":visit.status,"patient":visit.patient_name}
    def get_scores():
        return visit.scores_json
    def get_validations():
        vs = db.query(Validation).filter(Validation.visit_id==visit.id).all()
        return [{"rule_id":v.rule_id,"severity":v.severity,"message":v.message} for v in vs]
    def get_attachments():
        atts = db.query(Attachment).filter(Attachment.visit_id==visit.id).all()
        return [{"id":a.id,"kind":a.kind,"filename":a.filename} for a in atts]
    def get_deadline():
        return str(visit.deadline_at)
    def get_checklist():
        return visit.checklist_json
    return {"get_visit":get_visit,"get_scores":get_scores,"get_validations":get_validations,"get_attachments":get_attachments,"get_deadline":get_deadline,"get_checklist":get_checklist}

tools_registry = {}  # populated per call
