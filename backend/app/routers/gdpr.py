from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.auth.dependencies import get_current_user
from app.models.user import User
from app.services.gdpr import GDPRService

router = APIRouter(prefix="/gdpr", tags=["gdpr"])
_svc = GDPRService()


@router.post("/opt-out/{company_id}")
async def opt_out(
    company_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    ok = await _svc.opt_out_company(company_id, db, current_user.id)
    if not ok:
        raise HTTPException(404, "Company not found")
    return {"message": "Company opted out — no further outreach will be attempted"}


@router.delete("/erase/{company_id}")
async def erase(
    company_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await _svc.delete_company_data(company_id, db, current_user.id)


@router.get("/export/{company_id}")
async def export_data(
    company_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    data = await _svc.export_company_data(company_id, db)
    if not data:
        raise HTTPException(404, "Company not found")
    return data
