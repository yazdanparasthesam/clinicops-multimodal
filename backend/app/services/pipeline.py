import json
from sqlalchemy.orm import Session
from ..models import Visit, Validation, Attachment
from ..domain.scores import compute_all
from ..domain.validators import validate_all
try:
    from ..infra.telemetry.metrics import inc_statement, inc_validation, observe_journey_step
except Exception:
    inc_statement = inc_validation = observe_journey_step = lambda *a, **k: None

def recompute_visit(db: Session, visit: Visit, intake_override: dict | None = None):
    # gather intake from visit.scores_json or attachments CSV parse stub, or override
    if intake_override is not None:
        intake = intake_override
    else:
        intake = {}
        if visit.scores_json and isinstance(visit.scores_json, dict):
            # scores_json stores both intake and computed
            intake = visit.scores_json.get("_intake", {}) or visit.scores_json

    # compute scores deterministically
    scores = compute_all(intake)
    # gather attachments
    atts = db.query(Attachment).filter(Attachment.visit_id == visit.id).all()
    att_dicts = [{"kind": a.kind, "mime": a.mime} for a in atts]
    # build visit dict for validators
    # consent lives in intake, not top-level — read from _intake or override
    _intake_for_consent = intake if intake else (visit.scores_json or {}).get("_intake", {})
    consent_val = _intake_for_consent.get("consent") if isinstance(_intake_for_consent, dict) else False
    if isinstance(consent_val, str):
        consent_val = consent_val.strip().lower() in ("yes","true","1","y","consented")
    else:
        consent_val = bool(consent_val)
    visit_dict = {"id": visit.id, "patient_name": visit.patient_name, "consent": consent_val, "transcript_confidence": visit.transcript_confidence}
    # also allow intake allergies
    validations = validate_all(visit_dict, intake, att_dicts)
    # persist
    # Clear existing validations
    db.query(Validation).filter(Validation.visit_id == visit.id).delete()
    for v in validations:
        db.add(Validation(visit_id=visit.id, rule_id=v["rule_id"], severity=v["severity"], message=v["message"], field=v.get("field")))
    # merge intake + scores for storage
    stored = {**scores, "_intake": intake, "consent": visit_dict.get("consent")}
    visit.scores_json = stored
    # checklist
    visit.checklist_json = [{"id": f"chk-{v['rule_id']}", "rule_id": v["rule_id"], "status": "needs_fix" if v["severity"]=="error" else "warn", "message": v["message"]} for v in validations]
    if not validations:
        visit.checklist_json = [{"id":"chk-ok","rule_id":"OK","status":"ok","message":"All checks passed"}]
    db.commit()
    db.refresh(visit)
    try:
        inc_statement("visit")
        failures = len([x for x in validations if x.get("severity") == "error"])
        inc_validation(failures)
        observe_journey_step("recompute", 0.05)
    except Exception:
        pass
    return visit, validations, scores
