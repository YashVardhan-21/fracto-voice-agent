import stripe
from app.config import settings
from app.models.tenant import Tenant
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

if settings.stripe_secret_key:
    stripe.api_key = settings.stripe_secret_key

PLANS = {
    "starter": {"name": "Starter", "price": 9900, "agents": 10, "campaigns": 5},
    "pro": {"name": "Pro", "price": 29900, "agents": 100, "campaigns": 50},
    "agency": {"name": "Agency", "price": 99900, "agents": -1, "campaigns": -1},
}

class BillingService:

    async def create_checkout_session(self, tenant_id: str, plan: str, db: AsyncSession) -> str:
        if not stripe.api_key:
            from fastapi import HTTPException
            raise HTTPException(status_code=503, detail="Billing not configured")

        result = await db.execute(select(Tenant).where(Tenant.id == tenant_id))
        tenant = result.scalar_one_or_none()

        if tenant is None:
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail="Tenant not found")

        price_map = {
            "starter": settings.stripe_starter_price_id,
            "pro": settings.stripe_pro_price_id,
        }
        price_id = price_map.get(plan)
        if not price_id:
            from fastapi import HTTPException
            raise HTTPException(status_code=400, detail="Plan not available for self-service checkout")

        session = stripe.checkout.Session.create(
            customer=tenant.stripe_customer_id or None,
            payment_method_types=["card"],
            line_items=[{"price": price_id, "quantity": 1}],
            mode="subscription",
            success_url=f"{settings.frontend_url}/billing/success?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{settings.frontend_url}/billing",
            metadata={"tenant_id": tenant_id, "plan": plan},
        )
        return session.url

    async def handle_webhook(self, payload: bytes, sig: str, db: AsyncSession) -> dict:
        if settings.stripe_webhook_secret is None:
            # Dev mode: skip signature verification
            import json as _json
            try:
                event = _json.loads(payload)
            except Exception:
                from fastapi import HTTPException
                raise HTTPException(status_code=400, detail="Invalid JSON payload")
        else:
            try:
                event = stripe.Webhook.construct_event(payload, sig, settings.stripe_webhook_secret)
            except stripe.error.SignatureVerificationError as exc:
                from fastapi import HTTPException
                raise HTTPException(status_code=400, detail="Invalid webhook signature") from exc
            except ValueError as exc:
                from fastapi import HTTPException
                raise HTTPException(status_code=400, detail="Invalid payload") from exc

        if event["type"] == "checkout.session.completed":
            session = event["data"]["object"]
            tenant_id = session["metadata"]["tenant_id"]
            plan = session["metadata"]["plan"]
            result = await db.execute(select(Tenant).where(Tenant.id == tenant_id))
            tenant = result.scalar_one_or_none()
            if tenant:
                tenant.plan = plan
                tenant.stripe_customer_id = session.get("customer")
                tenant.stripe_subscription_id = session.get("subscription")
                await db.commit()
        return {"received": True}
