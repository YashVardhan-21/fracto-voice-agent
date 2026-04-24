from typing import Optional
import httpx
from app.config import settings

TYPE_HINT = {
    "dental": "dental clinic receptionist",
    "medical": "medical front-desk coordinator",
    "legal": "legal intake coordinator",
    "salon": "salon booking coordinator",
    "default": "business receptionist",
}

PROMPT_TEMPLATE = """ROLE
You are the {role} for {name}.

BUSINESS FACTS
- Services: {services}
- Opening Hours: {hours}
- Current Offers: {offers}
- Contact: {phone}
- Booking URL: {booking_url}
- Website Quality Notes: {website_quality_notes}

GOALS
1) Understand caller intent quickly.
2) Help with service questions, booking/rescheduling, and message-taking.
3) End with a clear next step.

RULES
- Keep replies concise: max 2 short sentences per turn unless details are requested.
- Ask one question at a time.
- If information is unknown, say so briefly and offer to take a message/callback.
- Do not invent policies, prices, hours, or guarantees.
- For medical/legal topics: do not provide professional advice; route to staff.
- Stay polite, confident, and task-focused.

SALES CONTEXT
- Upsell Mode: {upsell_mode}
- If upsell mode is ON and caller context fits, you may briefly mention website + voice automation package.
- Do not force a pitch when caller intent is unrelated.

CALL FLOW
- Greet + identify need.
- Resolve if possible.
- If not, collect: name, phone, reason, preferred callback time.
- Confirm captured details before ending."""

class PromptGenerator:
    @staticmethod
    def _compact_services(services: list[str] | None) -> str:
        if not services:
            return "general business services"
        clean = [s.strip() for s in services if isinstance(s, str) and s.strip()]
        if not clean:
            return "general business services"
        # Keep context tight to avoid bloating per-call prompt tokens.
        return ", ".join(clean[:6])

    @staticmethod
    def _compact_offers(offers: list[str] | None) -> str:
        if not offers:
            return "no published offers"
        clean = [str(o).strip() for o in offers if isinstance(o, str) and o.strip()]
        return ", ".join(clean[:4]) if clean else "no published offers"

    @staticmethod
    def _website_notes(company: dict) -> str:
        issues = company.get("website_quality_issues") or []
        if isinstance(issues, list) and issues:
            return ", ".join(str(i).strip() for i in issues[:3] if str(i).strip())
        score = company.get("website_quality_score")
        if score is None:
            return "not evaluated"
        return f"quality score {score}/100"

    @staticmethod
    def _upsell_mode(company: dict) -> str:
        score = company.get("website_quality_score")
        issues = company.get("website_quality_issues") or []
        website = company.get("website")
        if not website:
            return "ON (no website on record)"
        if isinstance(score, (int, float)) and score < 55:
            return "ON (website quality below target)"
        if isinstance(issues, list) and len(issues) >= 2:
            return "ON (multiple website issues detected)"
        return "OFF"

    def generate_local(self, company: dict) -> str:
        business_type = (company.get("business_type") or "default").lower()
        role = TYPE_HINT.get(business_type, TYPE_HINT["default"])
        return PROMPT_TEMPLATE.format(
            role=role,
            name=company.get("name", "our business"),
            services=self._compact_services(company.get("services")),
            hours=company.get("hours", "unknown"),
            offers=self._compact_offers(company.get("offers")),
            phone=company.get("phone", "our office number"),
            booking_url=company.get("booking_url", "not published"),
            website_quality_notes=self._website_notes(company),
            upsell_mode=self._upsell_mode(company),
        )

    async def generate_with_llm(self, company: dict) -> Optional[str]:
        if not settings.openai_api_key:
            return None
        base = self.generate_local(company)
        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                resp = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={"Authorization": f"Bearer {settings.openai_api_key}"},
                    json={
                        "model": "gpt-4o-mini",
                        "messages": [
                            {
                                "role": "system",
                                "content": "You are an expert at writing natural, effective voice agent system prompts.",
                            },
                            {
                                "role": "user",
                                "content": (
                                    "Refine this receptionist prompt. Keep all constraints intact, keep it concise "
                                    "(under 240 words), and optimize for low-token phone conversations.\n\n"
                                    f"{base}"
                                ),
                            },
                        ],
                        "temperature": 0.2,
                        "max_tokens": 260,
                    },
                )
                resp.raise_for_status()
                return resp.json()["choices"][0]["message"]["content"]
        except Exception:
            return None

    async def generate(self, company: dict) -> str:
        enhanced = await self.generate_with_llm(company)
        return enhanced or self.generate_local(company)
