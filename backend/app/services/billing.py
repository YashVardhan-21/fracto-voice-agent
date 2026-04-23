import stripe
from app.config import settings
from app.models.tenant import Tenant
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

stripe.api_key = settings.stripe_secret_key

PLANS = {
    "starter": {"name": "Starter", "price": 9900, "agents": 10, "campaigns": 5},
    "pro": {"name": "Pro", "price": 29900, "agents": 100, "campaigns": 50},
    "agency": {"name": "Agency", "price": 99900, "agents": -1, "campaigns": -1},
}

class BillingService:

    async def create_checkout_session(self, tenant_id: str, plan: str, db: AsyncSession) -> str:
        result = await db.execute(select(Tenant).where(Tenant.id == tenant_id))
        tenant = result.scalar_one_or_none()
        price_id = settings.stripe_starter_price_id if plan == "starter" else settings.stripe_pro_price_id

        session = stripe.checkout.Session.create(
            customer=tenant.stripe_customer_id or None,
            payment_method_types=["card"],
            line_items=[{"price": price_id, "quantity": 1}],
            mode="subscription",
            success_url=f"{settings.allowed_origins[0]}/billing/success?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{settings.allowed_origins[0]}/billing",
            metadata={"tenant_id": tenant_id, "plan": plan},
        )
        return session.url

    async def handle_webhook(self, payload: bytes, sig: str, db: AsyncSession) -> dict:
        try:
            event = stripe.Webhook.construct_event(payload, sig, settings.stripe_webhook_secret)
        except Exception:
            return {"error": "invalid_signature"}

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
        return {"received": True}
