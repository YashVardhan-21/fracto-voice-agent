from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from app.models.company import Company
from app.models.voice_agent import VoiceAgent
from app.models.call_log import CallLog
from app.models.audit_log import AuditLog
from datetime import datetime, timezone


class GDPRService:

    async def opt_out_company(self, company_id: int, db: AsyncSession, actor_id: int) -> bool:
        """Mark company as opted-out — no further outreach. Irreversible via UI."""
        result = await db.execute(select(Company).where(Company.id == company_id))
        company = result.scalar_one_or_none()
        if not company:
            return False
        company.opted_out = True
        company.opted_out_at = datetime.now(timezone.utc).isoformat()
        company.status = "opted_out"
        db.add(
            AuditLog(
                tenant_id=company.tenant_id,
                actor_id=actor_id,
                action="gdpr_opt_out",
                resource_type="company",
                resource_id=str(company_id),
                details={"company_name": company.name},
            )
        )
        return True

    async def delete_company_data(self, company_id: int, db: AsyncSession, actor_id: int) -> dict:
        """Right to erasure — anonymises all PII. Keeps audit log entry."""
        result = await db.execute(select(Company).where(Company.id == company_id))
        company = result.scalar_one_or_none()
        if not company:
            return {"deleted": False, "reason": "not_found"}

        agent_result = await db.execute(
            select(VoiceAgent).where(VoiceAgent.company_id == company_id)
        )
        agents = agent_result.scalars().all()
        agent_ids = [a.id for a in agents]

        if agent_ids:
            await db.execute(
                update(CallLog)
                .where(CallLog.voice_agent_id.in_(agent_ids))
                .values(transcript=None, phone_number="[deleted]", recording_url=None)
            )
        for agent in agents:
            agent.system_prompt = "[deleted per GDPR request]"

        original_name = company.name
        company.name = f"[Deleted Company {company_id}]"
        company.website = None
        company.phone = None
        company.email = None
        company.opted_out = True

        db.add(
            AuditLog(
                tenant_id=company.tenant_id,
                actor_id=actor_id,
                action="gdpr_erasure",
                resource_type="company",
                resource_id=str(company_id),
                details={"original_name": original_name, "agents_anonymised": len(agents)},
            )
        )
        return {"deleted": True, "agents_anonymised": len(agents)}

    async def export_company_data(self, company_id: int, db: AsyncSession) -> dict:
        """Right to data portability — export all data held for a company."""
        result = await db.execute(select(Company).where(Company.id == company_id))
        company = result.scalar_one_or_none()
        if not company:
            return {}
        agents_result = await db.execute(
            select(VoiceAgent).where(VoiceAgent.company_id == company_id)
        )
        agents = agents_result.scalars().all()
        return {
            "company": {
                "id": company.id,
                "name": company.name,
                "website": company.website,
                "phone": company.phone,
                "email": company.email,
                "data_source": company.data_source,
                "created_at": str(company.created_at),
            },
            "voice_agents": [
                {"id": a.id, "name": a.name, "created_at": str(a.created_at)}
                for a in agents
            ],
        }
