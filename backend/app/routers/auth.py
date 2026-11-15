from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..db import get_db
from ..models import User
from ..schemas import UserCreate, UserOut, LoginIn, TokenOut
from ..security import hash_password, verify_password, create_token
from ..deps import get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=UserOut)
def register(payload: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email==payload.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    u = User(email=payload.email, password_hash=hash_password(payload.password), role=payload.role)
    db.add(u); db.commit(); db.refresh(u)
    return u

@router.post("/login", response_model=TokenOut)
def login(payload: LoginIn, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email==payload.email).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_token(user.id, user.email, user.role)
    return TokenOut(access_token=token)

@router.get("/me", response_model=UserOut)
def me(current: User = Depends(get_current_user)):
    return current
