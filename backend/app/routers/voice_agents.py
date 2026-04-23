from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.voice_agent import VoiceAgent
from app.schemas.voice_agent import VoiceAgentRead
from app.auth.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/agents", tags=["agents"])


@router.get("/", response_model=list[VoiceAgentRead])
async def list_agents(
    limit: int = Query(50, le=200),
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    q = (
        select(VoiceAgent)
        .where(VoiceAgent.tenant_id == current_user.tenant_id)
        .order_by(VoiceAgent.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    result = await db.execute(q)
    return result.scalars().all()


@router.get("/{agent_id}", response_model=VoiceAgentRead)
async def get_agent(
    agent_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(VoiceAgent).where(VoiceAgent.id == agent_id, VoiceAgent.tenant_id == current_user.tenant_id)
    )
    agent = result.scalar_one_or_none()
    if not agent:
        raise HTTPException(404, "Agent not found")
    return agent
