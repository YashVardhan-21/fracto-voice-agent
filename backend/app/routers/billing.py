from fastapi import APIRouter, Depends, Request, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.auth.dependencies import get_current_user
from app.models.user import User
from app.services.billing import BillingService, PLANS
from app.middleware.rate_limit import limiter

router = APIRouter(prefix="/billing", tags=["billing"])
svc = BillingService()

@router.post("/checkout/{plan}")
async def create_checkout(
    plan: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if plan not in ["starter", "pro", "agency"]:
        raise HTTPException(400, "Invalid plan")
    url = await svc.create_checkout_session(current_user.tenant_id, plan, db)
    return {"checkout_url": url}

@router.post("/webhook")
@limiter.limit("60/minute")
async def stripe_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    body = await request.body()
    if len(body) > 1_048_576:  # 1 MB
        raise HTTPException(413, "Payload too large")
    sig = request.headers.get("stripe-signature", "")
    return await svc.handle_webhook(body, sig, db)

@router.get("/plans")
async def list_plans():
    return {"plans": PLANS}
