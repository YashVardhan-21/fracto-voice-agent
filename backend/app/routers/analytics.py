from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.database import get_db
from app.auth.dependencies import get_current_user
from app.models.user import User
from app.models.company import Company
from app.models.voice_agent import VoiceAgent
from app.models.campaign import Campaign
from app.models.call_log import CallLog

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/dashboard")
async def dashboard_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    tid = current_user.tenant_id
    total_companies = (
        await db.execute(select(func.count()).select_from(Company).where(Company.tenant_id == tid))
    ).scalar()
    active_agents = (
        await db.execute(
            select(func.count()).select_from(VoiceAgent).where(
                VoiceAgent.tenant_id == tid, VoiceAgent.status == "active"
            )
        )
    ).scalar()
    total_campaigns = (
        await db.execute(select(func.count()).select_from(Campaign).where(Campaign.tenant_id == tid))
    ).scalar()
    total_calls = (
        await db.execute(select(func.count()).select_from(CallLog).where(CallLog.tenant_id == tid))
    ).scalar()
    return {
        "total_companies": total_companies,
        "active_agents": active_agents,
        "total_campaigns": total_campaigns,
        "total_calls": total_calls,
    }
