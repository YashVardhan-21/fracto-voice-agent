import httpx
from app.config import settings

VAPI_BASE = "https://api.vapi.ai"

class VapiClient:
    @staticmethod
    def _raise_for_status_with_body(resp: httpx.Response) -> None:
        if resp.is_success:
            return
        try:
            detail = resp.json()
        except Exception:
            detail = resp.text
        raise RuntimeError(f"VAPI {resp.status_code} error: {detail}")

    @property
    def _headers(self) -> dict:
        return {
            "Authorization": f"Bearer {settings.vapi_api_key}",
            "Content-Type": "application/json",
        }

    async def create_assistant(self, name: str, system_prompt: str, business_type: str = "default") -> dict:
        if not settings.vapi_voice_id:
            raise ValueError("VAPI_VOICE_ID is required when VAPI_API_KEY is set")

        payload = {
            "name": name,
            "model": {
                "provider": "openai",
                "model": "gpt-4o-mini",
                "systemPrompt": system_prompt,
                "temperature": 0.7,
            },
            "voice": {
                "provider": "11labs",
                "voiceId": settings.vapi_voice_id,
            },
            "firstMessage": f"Thank you for calling {name}. How can I help you today?",
            "transcriber": {"provider": "deepgram", "model": "nova-2", "language": "en"},
        }
        async with httpx.AsyncClient(headers=self._headers, timeout=30.0) as client:
            resp = await client.post(f"{VAPI_BASE}/assistant", json=payload)
            self._raise_for_status_with_body(resp)
            return resp.json()

    async def get_assistant(self, vapi_id: str) -> dict:
        async with httpx.AsyncClient(headers=self._headers, timeout=15.0) as client:
            resp = await client.get(f"{VAPI_BASE}/assistant/{vapi_id}")
            self._raise_for_status_with_body(resp)
            return resp.json()

    async def delete_assistant(self, vapi_id: str) -> bool:
        async with httpx.AsyncClient(headers=self._headers, timeout=15.0) as client:
            resp = await client.delete(f"{VAPI_BASE}/assistant/{vapi_id}")
            self._raise_for_status_with_body(resp)
            return resp.status_code == 200

    async def make_call(self, vapi_agent_id: str, phone_number: str) -> dict:
        if not settings.vapi_phone_number_id:
            raise ValueError("VAPI_PHONE_NUMBER_ID not configured")
        payload = {
            "assistantId": vapi_agent_id,
            "customer": {"number": phone_number},
            "phoneNumberId": settings.vapi_phone_number_id,
        }
        async with httpx.AsyncClient(headers=self._headers, timeout=30.0) as client:
            resp = await client.post(f"{VAPI_BASE}/call/phone", json=payload)
            self._raise_for_status_with_body(resp)
            return resp.json()
