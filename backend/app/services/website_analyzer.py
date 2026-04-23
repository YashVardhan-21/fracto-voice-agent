import httpx
import json
import re
from typing import Optional
from app.config import settings

class WebsiteAnalyzer:
    """Multi-provider LLM analyzer with local keyword fallback."""

    async def analyze(self, url: str, company_name: str) -> dict:
        content = ""
        try:
            async with httpx.AsyncClient(
                headers={"User-Agent": "Mozilla/5.0 Chrome/124"},
                follow_redirects=True,
                timeout=20.0,
            ) as client:
                resp = await client.get(url)
                content = resp.text[:3000]
        except Exception as e:
            return {**self._local_analysis("", company_name), "fetch_error": str(e)}

        for provider in [self._gemini, self._openai, self._deepseek]:
            result = await provider(content, company_name)
            if result:
                return result

        return self._local_analysis(content, company_name)

    async def _gemini(self, content: str, company_name: str) -> Optional[dict]:
        if not settings.gemini_api_key:
            return None
        prompt = self._build_prompt(content, company_name)
        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                resp = await client.post(
                    f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={settings.gemini_api_key}",
                    json={"contents": [{"parts": [{"text": prompt}]}]},
                )
                text = resp.json()["candidates"][0]["content"]["parts"][0]["text"]
                parsed = self._parse_json(text)
                if parsed:
                    return {**parsed, "source": "gemini"}
        except Exception:
            return None

    async def _openai(self, content: str, company_name: str) -> Optional[dict]:
        if not settings.openai_api_key:
            return None
        prompt = self._build_prompt(content, company_name)
        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                resp = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={"Authorization": f"Bearer {settings.openai_api_key}"},
                    json={
                        "model": "gpt-4o-mini",
                        "messages": [{"role": "user", "content": prompt}],
                        "temperature": 0.2,
                    },
                )
                text = resp.json()["choices"][0]["message"]["content"]
                parsed = self._parse_json(text)
                if parsed:
                    return {**parsed, "source": "openai"}
        except Exception:
            return None

    async def _deepseek(self, content: str, company_name: str) -> Optional[dict]:
        if not settings.deepseek_api_key:
            return None
        prompt = self._build_prompt(content, company_name)
        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                resp = await client.post(
                    "https://api.deepseek.com/v1/chat/completions",
                    headers={"Authorization": f"Bearer {settings.deepseek_api_key}"},
                    json={
                        "model": "deepseek-chat",
                        "messages": [{"role": "user", "content": prompt}],
                        "temperature": 0.2,
                    },
                )
                text = resp.json()["choices"][0]["message"]["content"]
                parsed = self._parse_json(text)
                if parsed:
                    return {**parsed, "source": "deepseek"}
        except Exception:
            return None

    def _build_prompt(self, content: str, company_name: str) -> str:
        return (
            f"Extract business info for {company_name} from this website content.\n"
            f"Content: {content}\n\n"
            'Return ONLY valid JSON: {"business_type": "dental|medical|legal|salon|restaurant|gym|other", '
            '"services": ["list","of","services"], "phone": "+1-555-0000", '
            '"email": "info@example.com", "confidence_score": 0.85}'
        )

    def _parse_json(self, text: str) -> Optional[dict]:
        try:
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0]
            elif "```" in text:
                text = text.split("```")[1].split("```")[0]
            return json.loads(text.strip())
        except Exception:
            return None

    def _local_analysis(self, content: str, company_name: str) -> dict:
        c = content.lower()
        btype = "other"
        for t, words in [
            ("dental", ["dental", "dentist", "teeth"]),
            ("medical", ["medical", "doctor", "clinic", "health"]),
            ("legal", ["legal", "attorney", "lawyer", "law firm"]),
            ("salon", ["salon", "hair", "beauty", "spa"]),
            ("restaurant", ["restaurant", "dining", "menu", "food"]),
            ("gym", ["gym", "fitness", "workout", "yoga"]),
        ]:
            if any(w in c for w in words):
                btype = t
                break
        phone = re.search(r"(\+?[\d\s\-().]{7,})", content)
        email = re.search(r"\b[\w._%+-]+@[\w.-]+\.[a-z]{2,}\b", content, re.I)
        return {
            "business_type": btype,
            "services": [],
            "phone": phone.group(0).strip() if phone else "",
            "email": email.group(0) if email else "",
            "confidence_score": 0.3,
            "source": "local",
        }
