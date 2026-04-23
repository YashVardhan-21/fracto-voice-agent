from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.company import Company
from app.models.voice_agent import VoiceAgent
from app.services.website_analyzer import WebsiteAnalyzer
from app.services.prompt_generator import PromptGenerator
from app.services.vapi_client import VapiClient
from app.config import settings


class Pipeline:
    """
    Orchestrates: analyze website → generate prompt → create VAPI agent.
    Called from Celery tasks for async background processing.
    """

    def __init__(self):
        self.analyzer = WebsiteAnalyzer()
        self.generator = PromptGenerator()
        self.vapi = VapiClient()

    async def process_company(self, company_id: int, db: AsyncSession) -> dict:
        result = await db.execute(select(Company).where(Company.id == company_id))
        company = result.scalar_one_or_none()
        if not company:
            return {"success": False, "error": "Company not found"}

        company.status = "analyzing"
        await db.flush()

        if company.website:
            analysis = await self.analyzer.analyze(company.website, company.name)
            company.business_type = analysis.get("business_type", company.business_type)
            company.services = analysis.get("services", [])
            company.phone = analysis.get("phone") or company.phone
            company.email = analysis.get("email")
            company.analysis_score = analysis.get("confidence_score", 0.5)
            company.analysis_source = analysis.get("source", "local")

        company_data = {
            "name": company.name,
            "business_type": company.business_type or "default",
            "services": company.services or [],
            "phone": company.phone or "",
        }
        prompt = await self.generator.generate(company_data)

        if settings.vapi_api_key:
            try:
                vapi_result = await self.vapi.create_assistant(
                    name=f"{company.name} — AI Receptionist",
                    system_prompt=prompt,
                    business_type=company.business_type or "default",
                )
                agent = VoiceAgent(
                    company_id=company.id,
                    tenant_id=company.tenant_id,
                    name=f"{company.name} — AI Receptionist",
                    vapi_agent_id=vapi_result.get("id"),
                    system_prompt=prompt,
                    voice_config=vapi_result.get("voice"),
                    status="active",
                )
                db.add(agent)
                company.status = "agent_created"
            except Exception as e:
                company.status = "vapi_failed"
                return {"success": False, "error": str(e), "prompt": prompt}
        else:
            agent = VoiceAgent(
                company_id=company.id,
                tenant_id=company.tenant_id,
                name=f"{company.name} — AI Receptionist",
                system_prompt=prompt,
                status="draft",
            )
            db.add(agent)
            company.status = "prompt_ready"

        await db.flush()
        return {"success": True, "company_id": company.id, "status": company.status, "prompt": prompt}
