from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..db import get_db
from ..models import Visit, Validation, AuditLog
from ..deps import get_current_user
from ..models import User
from ..domain.workflow import can_transition, gate_errors_for_transition, role_allowed
from ..schemas import WorkflowIn

router = APIRouter(prefix="/visits/{visit_id}/workflow", tags=["workflow"])

def _gate_errors(db: Session, visit: Visit, target: str):
    errors = db.query(Validation).filter(Validation.visit_id==visit.id, Validation.severity=="error").all()
    blocked = gate_errors_for_transition(target, [e.rule_id for e in errors])
    if blocked:
        raise HTTPException(status_code=422, detail=f"Cannot {target}: failing error rules {blocked}")

@router.post("/{action}")
def workflow_action(visit_id: int, action: str, payload: WorkflowIn = None, db: Session=Depends(get_db), user: User=Depends(get_current_user)):
    v = db.query(Visit).filter(Visit.id==visit_id).first()
    if not v: raise HTTPException(status_code=404, detail="Not found")
    mapping = {"submit":"submitted","start_review":"in_review","approve":"approved","dispense":"dispensed","reject":"rejected","request_changes":"changes_requested","reopen":"draft"}
    target = mapping.get(action)
    if not target:
        raise HTTPException(status_code=400, detail="Invalid action")
    if not can_transition(v.status, target):
        raise HTTPException(status_code=409, detail=f"Cannot transition {v.status} -> {target}")
    if not role_allowed(user.role, target):
        raise HTTPException(status_code=403, detail=f"Role {user.role} cannot do {action}")
    _gate_errors(db, v, target)
    frm = v.status
    v.status = target
    db.add(AuditLog(visit_id=v.id, from_status=frm, to_status=target, actor_id=user.id, note=(payload.note if payload else None)))
    db.commit()
    return {"ok": True, "from": frm, "to": target}

@router.get("/audit")
def get_audit(visit_id: int, db: Session=Depends(get_db), user: User=Depends(get_current_user)):
    logs = db.query(AuditLog).filter(AuditLog.visit_id==visit_id).order_by(AuditLog.at).all()
    return [{"from":l.from_status,"to":l.to_status,"actor":l.actor_id,"at":l.at,"note":l.note} for l in logs]
