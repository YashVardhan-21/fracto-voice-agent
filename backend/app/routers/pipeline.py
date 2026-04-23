from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from app.database import get_db
from app.models.company import Company
from app.auth.dependencies import get_current_user
from app.models.user import User
from app.services.scraper import JobScraper
from app.workers.tasks import run_pipeline_for_company

router = APIRouter(prefix="/pipeline", tags=["pipeline"])


class ScrapeRequest(BaseModel):
    keywords: str = "receptionist"
    location: str = "Dublin, Ireland"
    limit: int = 20


@router.post("/scrape")
async def scrape_jobs(
    payload: ScrapeRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    scraper = JobScraper()
    jobs = await scraper.scrape_indeed(payload.keywords, payload.location, payload.limit)
    created = []
    for job in jobs:
        existing = await db.execute(
            select(Company).where(
                Company.name == job["company_name"],
                Company.tenant_id == current_user.tenant_id,
            )
        )
        if not existing.scalar_one_or_none():
            company = Company(
                name=job["company_name"],
                position=job.get("job_title"),
                location=job.get("location"),
                tenant_id=current_user.tenant_id,
                data_source="indeed_public",
                status="pending",
            )
            db.add(company)
            created.append(job["company_name"])
    await db.flush()
    return {"scraped": len(jobs), "new_companies": len(created), "companies": created}


@router.post("/analyze/{company_id}")
async def analyze_company(
    company_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Company).where(Company.id == company_id, Company.tenant_id == current_user.tenant_id)
    )
    company = result.scalar_one_or_none()
    if not company:
        raise HTTPException(404, "Company not found")
    run_pipeline_for_company.delay(company_id)
    return {"message": "Pipeline started", "company_id": company_id}


@router.post("/run-batch")
async def run_batch(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Company)
        .where(Company.tenant_id == current_user.tenant_id, Company.status == "pending")
        .limit(10)
    )
    companies = result.scalars().all()
    for c in companies:
        run_pipeline_for_company.delay(c.id)
    return {"queued": len(companies)}
