from datetime import datetime, timedelta, timezone
import hashlib
import hmac
import os

import jwt
from fastapi import Depends
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.session import get_db
from app.models.user import User

security = HTTPBearer(auto_error=False)


def hash_password(password: str, salt: bytes | None = None) -> str:
    salt = salt or os.urandom(16)
    derived = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 120_000)
    return f"{salt.hex()}${derived.hex()}"


def verify_password(password: str, stored_hash: str) -> bool:
    salt_hex, derived_hex = stored_hash.split("$", 1)
    recalculated = hash_password(password, bytes.fromhex(salt_hex))
    return hmac.compare_digest(recalculated, stored_hash)


def create_token(subject: str, token_type: str, minutes: int | None = None, days: int | None = None) -> str:
    settings = get_settings()
    now = datetime.now(timezone.utc)
    if minutes is not None:
        expires = now + timedelta(minutes=minutes)
    elif days is not None:
        expires = now + timedelta(days=days)
    else:
        expires = now + timedelta(minutes=settings.access_token_exp_minutes)

    payload = {"sub": subject, "type": token_type, "iat": int(now.timestamp()), "exp": int(expires.timestamp())}
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def create_access_token(subject: str) -> str:
    settings = get_settings()
    return create_token(subject, "access", minutes=settings.access_token_exp_minutes)


def create_refresh_token(subject: str) -> str:
    settings = get_settings()
    return create_token(subject, "refresh", days=settings.refresh_token_exp_days)


def decode_token(token: str, expected_type: str) -> dict:
    settings = get_settings()
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
    except jwt.PyJWTError as exc:
        raise HTTPException(status_code=401, detail="Invalid or expired token") from exc

    if payload.get("type") != expected_type:
        raise HTTPException(status_code=401, detail="Invalid token type")

    return payload


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    if credentials is None:
        raise HTTPException(status_code=401, detail="Not authenticated")

    payload = decode_token(credentials.credentials, "access")
    subject = payload.get("sub")
    user = db.query(User).filter(User.email == subject).first()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user
