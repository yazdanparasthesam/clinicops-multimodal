from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from ..db import get_db
from ..models import Visit, Validation
from ..deps import get_current_user
from ..models import User
import io, openpyxl
from fpdf import FPDF

router = APIRouter(prefix="/visits/{visit_id}/export", tags=["exports"])

@router.get("/pdf")
def export_pdf(visit_id: int, db: Session=Depends(get_db), user: User=Depends(get_current_user)):
    v = db.query(Visit).filter(Visit.id==visit_id).first()
    if not v: raise HTTPException(status_code=404, detail="Not found")
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, f"ClinicOps Prescription - Visit {v.id}", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 12)
    pdf.cell(0, 10, f"Patient: {v.patient_name} Status: {v.status}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 10, f"Scores: {v.scores_json}", new_x="LMARGIN", new_y="NEXT")
    validations = db.query(Validation).filter(Validation.visit_id==visit_id).all()
    for val in validations:
        pdf.cell(0, 8, f"{val.rule_id} [{val.severity}] {val.message}", new_x="LMARGIN", new_y="NEXT")
    out = io.BytesIO(pdf.output())
    out.seek(0)
    return StreamingResponse(out, media_type="application/pdf", headers={"Content-Disposition": f"attachment; filename=visit-{v.id}.pdf"})

@router.get("/xlsx")
def export_xlsx(visit_id: int, db: Session=Depends(get_db), user: User=Depends(get_current_user)):
    v = db.query(Visit).filter(Visit.id==visit_id).first()
    if not v: raise HTTPException(status_code=404, detail="Not found")
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Visit"
    ws.append(["Field","Value"])
    ws.append(["Patient", v.patient_name])
    ws.append(["Status", v.status])
    ws.append(["Scores", str(v.scores_json)])
    buf = io.BytesIO()
    wb.save(buf); buf.seek(0)
    return StreamingResponse(buf, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", headers={"Content-Disposition": f"attachment; filename=visit-{v.id}.xlsx"})

@router.get("/checklist")
def checklist(visit_id: int, db: Session=Depends(get_db), user: User=Depends(get_current_user)):
    v = db.query(Visit).filter(Visit.id==visit_id).first()
    if not v: raise HTTPException(status_code=404, detail="Not found")
    return {"visit_id": v.id, "items": v.checklist_json, "deadline_at": v.deadline_at }
