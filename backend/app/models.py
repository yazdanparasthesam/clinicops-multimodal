import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, Float, JSON, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from .db import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False)  # nurse, doctor, pharmacist
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class Visit(Base):
    __tablename__ = "visits"
    id = Column(Integer, primary_key=True)
    patient_name = Column(String(255), nullable=False)
    patient_dob = Column(String(20), nullable=True)
    status = Column(String(30), default="draft", nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    deadline_at = Column(DateTime, nullable=True)
    scores_json = Column(JSON, nullable=True)
    checklist_json = Column(JSON, nullable=True)
    notes_draft = Column(Text, nullable=True)
    transcript = Column(Text, nullable=True)
    transcript_confidence = Column(Float, nullable=True)
    vision_finding = Column(Text, nullable=True)

class Attachment(Base):
    __tablename__ = "attachments"
    id = Column(Integer, primary_key=True)
    visit_id = Column(Integer, ForeignKey("visits.id"), nullable=False, index=True)
    kind = Column(String(20), nullable=False)  # csv,image,audio,pdf
    filename = Column(String(255), nullable=False)
    mime = Column(String(100), nullable=False)
    size = Column(Integer, nullable=False)
    sha256 = Column(String(64), nullable=False)
    stored_path = Column(String(500), nullable=True)
    thumb_path = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class Validation(Base):
    __tablename__ = "validations"
    id = Column(Integer, primary_key=True)
    visit_id = Column(Integer, ForeignKey("visits.id"), nullable=False, index=True)
    rule_id = Column(String(10), nullable=False)
    severity = Column(String(10), nullable=False)  # error, warn
    message = Column(Text, nullable=False)
    field = Column(String(100), nullable=True)

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(Integer, primary_key=True)
    visit_id = Column(Integer, ForeignKey("visits.id"), nullable=False)
    from_status = Column(String(30), nullable=True)
    to_status = Column(String(30), nullable=False)
    actor_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    at = Column(DateTime, default=datetime.datetime.utcnow)
    note = Column(Text, nullable=True)

class AIRequest(Base):
    __tablename__ = "ai_requests"
    id = Column(Integer, primary_key=True)
    visit_id = Column(Integer, ForeignKey("visits.id"), nullable=True)
    kind = Column(String(30), nullable=False)
    provider = Column(String(20), nullable=False)
    model = Column(String(50), nullable=True)
    prompt_hash = Column(String(64), nullable=True)
    status = Column(String(20), default="ok")
    latency_ms = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class Comment(Base):
    __tablename__ = "comments"
    id = Column(Integer, primary_key=True)
    visit_id = Column(Integer, ForeignKey("visits.id"), nullable=False, index=True)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    body = Column(Text, nullable=False)
    anchor = Column(String(100), nullable=True)
    resolved = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
