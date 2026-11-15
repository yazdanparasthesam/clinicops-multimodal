from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Any
import datetime

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    role: str = Field(pattern="^(nurse|doctor|pharmacist)$")

class UserOut(BaseModel):
    id: int
    email: str
    role: str
    class Config:
        from_attributes = True

class LoginIn(BaseModel):
    email: EmailStr
    password: str

class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"

class VisitCreate(BaseModel):
    patient_name: str
    patient_dob: Optional[str] = None
    allergies: Optional[str] = None

class VisitOut(BaseModel):
    id: int
    patient_name: str
    patient_dob: Optional[str] = None
    status: str
    created_by: int
    created_at: datetime.datetime
    deadline_at: Optional[datetime.datetime] = None
    scores: Optional[Any] = None
    checklist: Optional[Any] = None
    notes_draft: Optional[str] = None
    transcript: Optional[str] = None
    vision_finding: Optional[str] = None
    class Config:
        from_attributes = True

class AttachmentOut(BaseModel):
    id: int
    visit_id: int
    kind: str
    filename: str
    mime: str
    size: int
    sha256: str
    class Config:
        from_attributes = True

class ValidationOut(BaseModel):
    id: int
    visit_id: int
    rule_id: str
    severity: str
    message: str
    field: Optional[str] = None
    class Config:
        from_attributes = True

class CommentCreate(BaseModel):
    body: str
    anchor: Optional[str] = None

class CommentOut(BaseModel):
    id: int
    visit_id: int
    author_id: int
    body: str
    anchor: Optional[str] = None
    resolved: bool
    class Config:
        from_attributes = True

class WorkflowIn(BaseModel):
    note: Optional[str] = None

class AIDraftIn(BaseModel):
    instruction: Optional[str] = None

class AIDraftOut(BaseModel):
    kind: str
    content: str
    model: str
    latency_ms: int

class ChecklistOut(BaseModel):
    visit_id: int
    items: List[dict]
    deadline_at: Optional[datetime.datetime] = None
