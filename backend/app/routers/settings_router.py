from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import Optional
from app.database import get_db
from app.auth.dependencies import get_current_user, require_admin
from app.models.tenant import Tenant
from app.models.user import User

router = APIRouter(prefix="/settings", tags=["settings"])

class BrandingUpdate(BaseModel):
    company_name: Optional[str] = None
    primary_color: Optional[str] = None
    logo_url: Optional[str] = None

@router.get("/branding")
async def get_branding(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Tenant).where(Tenant.id == current_user.tenant_id))
    tenant = result.scalar_one_or_none()
    tenant_settings = (tenant.settings or {}) if tenant else {}
    return {
        "company_name": tenant_settings.get("company_name", "FRACTO"),
        "primary_color": tenant_settings.get("primary_color", "#4F46E5"),
        "logo_url": tenant_settings.get("logo_url"),
    }

@router.patch("/branding")
async def update_branding(
    payload: BrandingUpdate,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Tenant).where(Tenant.id == current_user.tenant_id))
    tenant = result.scalar_one_or_none()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    current = tenant.settings or {}
    if payload.company_name is not None:
        current["company_name"] = payload.company_name
    if payload.primary_color is not None:
        current["primary_color"] = payload.primary_color
    if payload.logo_url is not None:
        current["logo_url"] = payload.logo_url
    tenant.settings = current
    await db.commit()
    return {"updated": True}
