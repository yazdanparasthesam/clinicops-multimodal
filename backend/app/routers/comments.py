from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..db import get_db
from ..models import Comment, Visit, User
from ..deps import get_current_user
from ..schemas import CommentCreate, CommentOut

router = APIRouter(prefix="/visits/{visit_id}/comments", tags=["comments"])

@router.post("", response_model=CommentOut)
def add_comment(visit_id: int, payload: CommentCreate, db: Session=Depends(get_db), user: User=Depends(get_current_user)):
    v = db.query(Visit).filter(Visit.id==visit_id).first()
    if not v: raise HTTPException(status_code=404, detail="Not found")
    c = Comment(visit_id=visit_id, author_id=user.id, body=payload.body, anchor=payload.anchor, resolved=False)
    db.add(c); db.commit(); db.refresh(c)
    return c

@router.get("", response_model=list[CommentOut])
def list_comments(visit_id: int, db: Session=Depends(get_db), user: User=Depends(get_current_user)):
    return db.query(Comment).filter(Comment.visit_id==visit_id).order_by(Comment.created_at).all()

@router.post("/{comment_id}/resolve")
def resolve_comment(visit_id: int, comment_id: int, db: Session=Depends(get_db), user: User=Depends(get_current_user)):
    c = db.query(Comment).filter(Comment.id==comment_id, Comment.visit_id==visit_id).first()
    if not c: raise HTTPException(status_code=404, detail="Not found")
    c.resolved = True; db.commit()
    return {"ok": True}

