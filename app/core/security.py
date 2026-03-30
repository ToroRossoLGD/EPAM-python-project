from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

_pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


def hash_password(password: str) -> str:
    return _pwd_context.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return _pwd_context.verify(password, password_hash)


def create_access_token(*, subject: str, expires_minutes: int | None = None) -> str:
    minutes = expires_minutes if expires_minutes is not None else settings.JWT_EXPIRES_MINUTES
    expire = datetime.now(timezone.utc) + timedelta(minutes=minutes)

    payload = {"sub": subject, "exp": expire}
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def decode_access_token(token: str) -> dict:
    try:
        return jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
    except JWTError as e:
        raise ValueError("Invalid token") from e

def create_invite_token(email: str, project_id: int) -> str:
    expire = datetime.utcnow() + timedelta(hours=24)

    payload = {
        "sub": email,
        "project_id": project_id,
        "type": "invite",
        "exp": expire,
    }

    return jwt.encode(payload, settings.JWT_SECRET, algorithm="HS256")