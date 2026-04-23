import asyncio
from app.workers.celery_app import celery_app
from app.database import AsyncSessionLocal
from app.services.pipeline import Pipeline


@celery_app.task(bind=True, max_retries=3, default_retry_delay=30, name="tasks.run_pipeline_for_company")
def run_pipeline_for_company(self, company_id: int):
    async def _run():
        async with AsyncSessionLocal() as db:
            pipeline = Pipeline()
            return await pipeline.process_company(company_id, db)

    try:
        return asyncio.run(_run())
    except Exception as exc:
        raise self.retry(exc=exc)


@celery_app.task(name="tasks.run_campaign_pipeline")
def run_campaign_pipeline(campaign_id: int):
    async def _run():
        from sqlalchemy import select
        from app.models.campaign import Campaign

        async with AsyncSessionLocal() as db:
            result = await db.execute(select(Campaign).where(Campaign.id == campaign_id))
            campaign = result.scalar_one_or_none()
            if not campaign or not campaign.prospects:
                return {"success": False, "reason": "no_prospects"}
            pipeline = Pipeline()
            results = []
            for prospect in campaign.prospects:
                company_id = prospect.get("company_id")
                if company_id:
                    r = await pipeline.process_company(company_id, db)
                    results.append(r)
            campaign.status = "running"
            return {"success": True, "processed": len(results)}

    return asyncio.run(_run())
