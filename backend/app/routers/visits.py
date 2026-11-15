from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from ..db import get_db
from ..models import Visit, User, Attachment, Validation
from ..schemas import VisitCreate, VisitOut, AttachmentOut, ValidationOut
from ..deps import get_current_user
from ..domain.deadlines import compute_deadline
from ..services.pipeline import recompute_visit
from ..infra.attachments import validate_and_store
import csv, io, datetime, json

router = APIRouter(prefix="/visits", tags=["visits"])

@router.post("", response_model=VisitOut)
def create_visit(payload: VisitCreate, db: Session=Depends(get_db), user: User=Depends(get_current_user)):
    if user.role not in ("nurse","doctor"):
        raise HTTPException(status_code=403, detail="Only nurse/doctor can create")
    v = Visit(patient_name=payload.patient_name, patient_dob=payload.patient_dob, created_by=user.id, status="draft", scores_json={"_intake":{"allergies": payload.allergies}}, deadline_at=compute_deadline(datetime.datetime.utcnow()))
    db.add(v); db.commit(); db.refresh(v)
    recompute_visit(db, v)
    return VisitOut(id=v.id, patient_name=v.patient_name, patient_dob=v.patient_dob, status=v.status, created_by=v.created_by, created_at=v.created_at, deadline_at=v.deadline_at, scores=v.scores_json, checklist=v.checklist_json, notes_draft=v.notes_draft, transcript=v.transcript, vision_finding=v.vision_finding)

@router.get("", response_model=list[VisitOut])
def list_visits(db: Session=Depends(get_db), user: User=Depends(get_current_user)):
    visits = db.query(Visit).order_by(Visit.created_at.desc()).all()
    return [VisitOut(id=v.id, patient_name=v.patient_name, patient_dob=v.patient_dob, status=v.status, created_by=v.created_by, created_at=v.created_at, deadline_at=v.deadline_at, scores=v.scores_json, checklist=v.checklist_json, notes_draft=v.notes_draft, transcript=v.transcript, vision_finding=v.vision_finding) for v in visits]

@router.get("/{visit_id}", response_model=VisitOut)
def get_visit(visit_id: int, db: Session=Depends(get_db), user: User=Depends(get_current_user)):
    v = db.query(Visit).filter(Visit.id==visit_id).first()
    if not v: raise HTTPException(status_code=404, detail="Not found")
    return VisitOut(id=v.id, patient_name=v.patient_name, patient_dob=v.patient_dob, status=v.status, created_by=v.created_by, created_at=v.created_at, deadline_at=v.deadline_at, scores=v.scores_json, checklist=v.checklist_json, notes_draft=v.notes_draft, transcript=v.transcript, vision_finding=v.vision_finding)

@router.patch("/{visit_id}")
def patch_visit(visit_id: int, payload: dict, db: Session=Depends(get_db), user: User=Depends(get_current_user)):
    v = db.query(Visit).filter(Visit.id==visit_id).first()
    if not v: raise HTTPException(status_code=404, detail="Not found")
    # update intake inside scores_json._intake
    intake = (v.scores_json or {}).get("_intake", {}) if isinstance(v.scores_json, dict) else {}
    # also support scores_json being dict directly
    if v.scores_json and isinstance(v.scores_json, dict) and "_intake" not in v.scores_json:
        intake = v.scores_json
    for k in ["weight_kg","height_cm","systolic","diastolic","creatinine","age","sex","dose_mg","meds","allergies","consent","conditions","dvt_factors","taken","prescribed","apgar_scores"]:
        if k in payload:
            intake[k] = payload[k]
    # merge
    # persist new intake first, then recompute with override to avoid JSON mutation pitfalls
    if v.scores_json is None:
        v.scores_json = {}
    # Use flag for SQLAlchemy JSON change detection
    from sqlalchemy.orm.attributes import flag_modified
    v.scores_json = {**v.scores_json, "_intake": intake}
    flag_modified(v, "scores_json")
    db.commit()
    recompute_visit(db, v, intake_override=intake)
    return {"ok": True, "intake": intake, "scores": v.scores_json}

@router.get("/{visit_id}/validations", response_model=list[ValidationOut])
def get_validations(visit_id: int, db: Session=Depends(get_db), user: User=Depends(get_current_user)):
    vs = db.query(Validation).filter(Validation.visit_id==visit_id).all()
    return vs

@router.get("/{visit_id}/attachments", response_model=list[AttachmentOut])
def get_attachments(visit_id: int, db: Session=Depends(get_db), user: User=Depends(get_current_user)):
    atts = db.query(Attachment).filter(Attachment.visit_id==visit_id).all()
    return atts

@router.post("/{visit_id}/attachments", response_model=AttachmentOut)
def upload_attachment(visit_id: int, file: UploadFile = File(...), db: Session=Depends(get_db), user: User=Depends(get_current_user)):
    v = db.query(Visit).filter(Visit.id==visit_id).first()
    if not v: raise HTTPException(status_code=404, detail="Not found")
    if user.role not in ("nurse","doctor"):
        raise HTTPException(status_code=403, detail="Not allowed")
    data = file.file.read()
    try:
        meta = validate_and_store(file.filename, file.content_type or "application/octet-stream", data, visit_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    att = Attachment(visit_id=visit_id, kind=meta["kind"], filename=meta["filename"], mime=meta["mime"], size=meta["size"], sha256=meta["sha256"], stored_path=meta["stored_path"], thumb_path=meta.get("thumb_path"))
    db.add(att); db.commit(); db.refresh(att)
    # if CSV, parse intake
    if meta["kind"] == "csv":
        try:
            text = data.decode("utf-8", errors="ignore")
            reader = csv.DictReader(io.StringIO(text))
            row = next(reader, None)
            if row:
                intake = {}
                for k in row:
                    if not k: continue
                    kl = k.strip().lower()
                    val = row[k]
                    # try numeric
                    try:
                        if kl in ("weight_kg","height_cm","systolic","diastolic","creatinine","age","dose_mg","taken","prescribed"):
                            intake[kl] = float(val) if "." in val else int(val)
                        else:
                            intake[kl] = val
                    except Exception:
                        intake[kl] = val
                # merge
                cur = (v.scores_json or {}).get("_intake", {}) if isinstance(v.scores_json, dict) else {}
                cur.update(intake)
                v.scores_json = {**(v.scores_json or {}), "_intake": cur}
                db.commit()
        except Exception:
            pass
    recompute_visit(db, v)
    return att
