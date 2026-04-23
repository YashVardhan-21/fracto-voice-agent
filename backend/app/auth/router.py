import re
import secrets
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from app.database import get_db
from app.models.user import User
from app.models.tenant import Tenant
from app.auth.service import AuthService, verify_password, create_access_token
from app.auth.schemas import LoginRequest, TokenResponse, UserCreate

router = APIRouter(prefix="/auth", tags=["auth"])


def _make_slug(name: str, suffix: str) -> str:
    base = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")[:40]
    return f"{base}-{suffix}"


@router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == payload.email))
    user = result.scalar_one_or_none()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    token = create_access_token({"sub": str(user.id), "email": user.email, "role": user.role})
    return TokenResponse(
        access_token=token,
        user_id=user.id,
        email=user.email,
        full_name=user.full_name,
        role=user.role,
    )


@router.post("/register", response_model=TokenResponse, status_code=201)
async def register(payload: UserCreate, db: AsyncSession = Depends(get_db)):
    existing = await db.execute(select(User).where(User.email == payload.email))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")
    tenant_token = secrets.token_hex(16)  # 128-bit entropy
    tenant_id = f"tenant_{tenant_token}"
    slug = _make_slug(payload.full_name, tenant_token[:8])
    tenant = Tenant(id=tenant_id, name=payload.full_name, slug=slug, plan="starter")
    user = User(
        email=payload.email,
        hashed_password=AuthService.hash_password(payload.password),
        full_name=payload.full_name,
        role=payload.role,
        tenant_id=tenant_id,
    )
    try:
        db.add(tenant)
        db.add(user)
        await db.flush()
    except IntegrityError:
        raise HTTPException(status_code=409, detail="Registration conflict, please try again")
    token = create_access_token({"sub": str(user.id), "email": user.email, "role": user.role})
    return TokenResponse(
        access_token=token,
        user_id=user.id,
        email=user.email,
        full_name=user.full_name,
        role=user.role,
    )
