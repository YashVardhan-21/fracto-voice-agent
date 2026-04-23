from typing import Optional
import httpx
from app.config import settings

TEMPLATES = {
    "dental": """You are a warm, professional receptionist for {name}, a dental practice.

Your responsibilities:
- Answer questions about services: {services}
- Schedule new patient and follow-up appointments
- Provide pre-appointment instructions
- Handle insurance and payment inquiries with sensitivity

Contact number: {phone}

Tone: Reassuring and calm — many callers are anxious about dental visits. Always confirm appointment details before ending the call.""",

    "medical": """You are a professional medical receptionist for {name}.

Your responsibilities:
- Schedule patient appointments with the appropriate provider
- Answer questions about services: {services}
- Triage appointment urgency (routine vs. urgent)
- Collect basic insurance information

Contact number: {phone}

Tone: Empathetic, efficient, and professional. Never provide medical advice — always defer clinical questions to the provider.""",

    "legal": """You are an experienced legal intake specialist for {name}.

Your responsibilities:
- Schedule initial consultations with attorneys
- Collect basic case information (nature of matter, timeline, parties involved)
- Answer questions about practice areas: {services}
- Explain the consultation process

Contact number: {phone}

Tone: Professional and discrete. Reassure callers that their information is confidential.""",

    "salon": """You are a friendly booking coordinator for {name}.

Your responsibilities:
- Book appointments for services: {services}
- Answer questions about pricing and availability
- Handle rescheduling and cancellations with grace

Contact number: {phone}

Tone: Upbeat and friendly. Make every caller feel welcome.""",

    "default": """You are a helpful virtual receptionist for {name}.

Your responsibilities:
- Answer questions about the business and services: {services}
- Schedule appointments and take messages
- Connect callers with the right team member

Contact number: {phone}

Tone: Friendly, professional, and efficient.""",
}

class PromptGenerator:
    def generate_local(self, company: dict) -> str:
        template = TEMPLATES.get(company.get("business_type", "default"), TEMPLATES["default"])
        return template.format(
            name=company.get("name", "our business"),
            services=", ".join(company.get("services") or ["our services"]),
            phone=company.get("phone", "our office number"),
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
                                "content": f"Enhance this voice agent prompt to sound more natural and persuasive, keeping it under 500 words:\n\n{base}",
                            },
                        ],
                        "temperature": 0.7,
                    },
                )
                resp.raise_for_status()
                return resp.json()["choices"][0]["message"]["content"]
        except Exception:
            return None

    async def generate(self, company: dict) -> str:
        enhanced = await self.generate_with_llm(company)
        return enhanced or self.generate_local(company)
