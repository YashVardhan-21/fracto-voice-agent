from typing import Literal

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select
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


class ReanalyzeRequest(BaseModel):
    mode: Literal["top", "all"] = "top"
    limit: int = 50
    only_with_website: bool = True


@router.post("/scrape")
async def scrape_jobs(
    payload: ScrapeRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    scraper = JobScraper()
    jobs, diagnostics = await scraper.scrape_jobs(payload.keywords, payload.location, payload.limit)
    created = []
    updated = []
    for job in jobs:
        lead_score = job.get("lead_score")
        existing = await db.execute(
            select(Company).where(
                Company.name == job["company_name"],
                Company.tenant_id == current_user.tenant_id,
            )
        )
        existing_company = existing.scalar_one_or_none()
        if not existing_company:
            company = Company(
                name=job["company_name"],
                website=job.get("website"),
                position=job.get("job_title"),
                location=job.get("location"),
                business_type=job.get("business_type_hint"),
                hours=job.get("hours"),
                offers=job.get("offers"),
                booking_url=job.get("booking_url"),
                phone=job.get("phone"),
                tenant_id=current_user.tenant_id,
                data_source=job.get("source", "unknown"),
                analysis_score=lead_score,
                analysis_source="lead_scoring_v1",
                status="pending",
            )
            db.add(company)
            created.append(job["company_name"])
        else:
            # Keep existing records fresh with higher-confidence lead signals.
            existing_company.position = job.get("job_title") or existing_company.position
            existing_company.location = job.get("location") or existing_company.location
            existing_company.website = job.get("website") or existing_company.website
            existing_company.phone = job.get("phone") or existing_company.phone
            existing_company.business_type = job.get("business_type_hint") or existing_company.business_type
            existing_company.hours = job.get("hours") or existing_company.hours
            existing_company.booking_url = job.get("booking_url") or existing_company.booking_url
            if job.get("offers"):
                existing_company.offers = job.get("offers")
            if lead_score is not None:
                current_score = existing_company.analysis_score or 0
                if lead_score > current_score:
                    existing_company.analysis_score = lead_score
                    existing_company.analysis_source = "lead_scoring_v1"
                    existing_company.data_source = job.get("source", existing_company.data_source)
            updated.append(existing_company.name)
    await db.flush()
    return {
        "scraped": len(jobs),
        "new_companies": len(created),
        "updated_companies": len(updated),
        "companies": created,
        "diagnostics": diagnostics,
    }


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


@router.post("/reanalyze")
async def reanalyze_companies(
    payload: ReanalyzeRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    limit = max(1, min(payload.limit, 500))

    stmt = (
        select(Company.id)
        .where(Company.tenant_id == current_user.tenant_id, Company.opted_out == False)  # noqa: E712
    )
    if payload.only_with_website:
        stmt = stmt.where(Company.website.is_not(None), Company.website != "")
    if payload.mode == "top":
        stmt = stmt.order_by(func.coalesce(Company.analysis_score, 0).desc(), Company.created_at.desc())
    else:
        stmt = stmt.order_by(Company.created_at.desc())
    stmt = stmt.limit(limit)

    company_ids = (await db.execute(stmt)).scalars().all()
    for company_id in company_ids:
        run_pipeline_for_company.delay(company_id)

    return {
        "queued": len(company_ids),
        "mode": payload.mode,
        "limit": limit,
        "only_with_website": payload.only_with_website,
    }
