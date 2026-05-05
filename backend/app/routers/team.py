from typing import Literal, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user, require_admin
from app.auth.service import AuthService
from app.database import get_db
from app.models.user import User

router = APIRouter(prefix="/team", tags=["team"])


class TeamUserRead(BaseModel):
    id: int
    email: str
    full_name: str
    role: str
    is_admin: bool
    is_active: bool
    tenant_id: str

    class Config:
        from_attributes = True


class TeamUserCreate(BaseModel):
    email: EmailStr
    full_name: str = Field(min_length=1, max_length=255)
    role: Literal["agent", "manager", "admin"] = "agent"
    temporary_password: str = Field(min_length=8, max_length=128)


class TeamUserUpdate(BaseModel):
    full_name: Optional[str] = Field(default=None, min_length=1, max_length=255)
    role: Optional[Literal["agent", "manager", "admin"]] = None
    is_active: Optional[bool] = None
    reset_password: Optional[str] = Field(default=None, min_length=8, max_length=128)


@router.get("/users", response_model=list[TeamUserRead])
async def list_team_users(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(User)
        .where(User.tenant_id == current_user.tenant_id)
        .order_by(User.created_at.asc(), User.id.asc())
    )
    return result.scalars().all()


@router.post("/users", response_model=TeamUserRead, status_code=201)
async def create_team_user(
    payload: TeamUserCreate,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    existing = await db.execute(select(User).where(User.email == payload.email))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        email=payload.email,
        hashed_password=AuthService.hash_password(payload.temporary_password),
        full_name=payload.full_name,
        role=payload.role,
        is_admin=payload.role == "admin",
        is_active=True,
        tenant_id=current_user.tenant_id,
    )
    db.add(user)
    await db.flush()
    await db.commit()
    await db.refresh(user)
    return user


@router.patch("/users/{user_id}", response_model=TeamUserRead)
async def update_team_user(
    user_id: int,
    payload: TeamUserUpdate,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(User).where(User.id == user_id, User.tenant_id == current_user.tenant_id)
    )
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    was_admin = bool(user.is_admin)

    if payload.full_name is not None:
        user.full_name = payload.full_name
    if payload.role is not None:
        user.role = payload.role
        user.is_admin = payload.role == "admin"
    if payload.is_active is not None:
        user.is_active = payload.is_active
    if payload.reset_password:
        user.hashed_password = AuthService.hash_password(payload.reset_password)

    # Safety: keep at least one admin in tenant.
    if was_admin and not user.is_admin:
        admin_count = await db.execute(
            select(func.count(User.id)).where(
                User.tenant_id == current_user.tenant_id, User.is_admin == True  # noqa: E712
            )
        )
        if admin_count.scalar_one() <= 1:
            raise HTTPException(status_code=400, detail="Tenant must have at least one admin")

    await db.commit()
    await db.refresh(user)
    return user
