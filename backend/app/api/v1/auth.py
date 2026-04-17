from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import LoginRequest
from app.schemas.auth import RefreshRequest
from app.schemas.auth import RegisterRequest
from app.schemas.auth import TokenResponse
from app.schemas.auth import UserResponse
from app.services.auth import create_access_token
from app.services.auth import create_refresh_token
from app.services.auth import decode_token
from app.services.auth import hash_password
from app.services.auth import verify_password

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse)
def register(payload: RegisterRequest, db: Session = Depends(get_db)) -> User:
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing is not None:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(email=payload.email, password_hash=hash_password(payload.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    user = db.query(User).filter(User.email == payload.email).first()
    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return TokenResponse(
        access_token=create_access_token(user.email),
        refresh_token=create_refresh_token(user.email),
    )


@router.post("/refresh", response_model=TokenResponse)
def refresh(payload: RefreshRequest, db: Session = Depends(get_db)) -> TokenResponse:
    decoded = decode_token(payload.refresh_token, "refresh")
    user = db.query(User).filter(User.email == decoded.get("sub")).first()
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    return TokenResponse(
        access_token=create_access_token(user.email),
        refresh_token=create_refresh_token(user.email),
    )
