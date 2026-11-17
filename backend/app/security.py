import datetime, jwt, hashlib
from passlib.context import CryptContext
from .config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(p: str) -> str:
    # bcrypt 72-byte limit — truncate safely 
    return pwd_context.hash(p[:72])

def verify_password(p: str, h: str) -> bool:
    # try full, then truncated fallback for compat
    try:
        return pwd_context.verify(p, h)
    except ValueError:
        return pwd_context.verify(p[:72], h)

def create_token(user_id: int, email: str, role: str) -> str:
    payload = {
        "sub": str(user_id),
        "email": email,
        "role": role,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=settings.jwt_expire_hours),
        "iat": datetime.datetime.utcnow(),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)

def decode_token(token: str) -> dict:
    return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])

def hash_prompt(prompt: str) -> str:
    return hashlib.sha256(prompt.encode()).hexdigest()[:16]
