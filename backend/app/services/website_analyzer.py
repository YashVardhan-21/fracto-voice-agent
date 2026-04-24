import httpx
import json
import re
from typing import Optional
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from app.config import settings

class WebsiteAnalyzer:
    """Multi-provider LLM analyzer with local keyword fallback."""

    async def analyze(self, url: str, company_name: str) -> dict:
        content = ""
        html = ""
        try:
            async with httpx.AsyncClient(
                headers={"User-Agent": "Mozilla/5.0 Chrome/124"},
                follow_redirects=True,
                timeout=20.0,
            ) as client:
                resp = await client.get(url)
                resp.raise_for_status()
                html = resp.text
                soup = BeautifulSoup(html, "html.parser")
                content = soup.get_text(" ", strip=True)[:6000]
        except Exception as e:
            return {**self._local_analysis("", company_name, "", url), "fetch_error": str(e)}

        for provider in [self._gemini, self._openai, self._deepseek]:
            result = await provider(content, company_name)
            if result:
                return result

        return self._local_analysis(content, company_name, html, url)

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
                resp.raise_for_status()
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
                resp.raise_for_status()
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
                resp.raise_for_status()
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
            '"email": "info@example.com", "hours": "Mon-Fri 9am-6pm", '
            '"offers": ["new patient offer", "free consultation"], '
            '"booking_url": "https://example.com/book", '
            '"website_quality_score": 72, '
            '"website_quality_issues": ["no clear booking CTA", "outdated design"], '
            '"confidence_score": 0.85}'
        )

    def _parse_json(self, text: str) -> Optional[dict]:
        try:
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0]
            elif "```" in text:
                text = text.split("```")[1].split("```")[0]
            parsed = json.loads(text.strip())
            return self._normalize_result(parsed)
        except Exception:
            return None

    def _normalize_result(self, parsed: dict) -> dict:
        services = parsed.get("services") if isinstance(parsed.get("services"), list) else []
        offers = parsed.get("offers") if isinstance(parsed.get("offers"), list) else []
        issues = parsed.get("website_quality_issues") if isinstance(parsed.get("website_quality_issues"), list) else []
        quality = parsed.get("website_quality_score")
        try:
            quality_value = float(quality) if quality is not None else None
        except Exception:
            quality_value = None
        if quality_value is not None:
            quality_value = max(0.0, min(100.0, quality_value))
        return {
            "business_type": parsed.get("business_type") or "other",
            "services": services[:10],
            "phone": parsed.get("phone") or "",
            "email": parsed.get("email") or "",
            "hours": parsed.get("hours") or "",
            "offers": [str(o).strip() for o in offers if str(o).strip()][:8],
            "booking_url": parsed.get("booking_url") or "",
            "website_quality_score": quality_value,
            "website_quality_issues": [str(i).strip() for i in issues if str(i).strip()][:8],
            "confidence_score": parsed.get("confidence_score", 0.5),
        }

    def _local_analysis(self, content: str, company_name: str, raw_html: str = "", base_url: str = "") -> dict:
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
        offers: list[str] = []
        for phrase in [
            "discount",
            "offer",
            "promotion",
            "free consultation",
            "new patient",
            "package",
            "free contraception scheme",
        ]:
            if phrase in c:
                offers.append(phrase.title())
        euro_price = re.search(r"€\s?\d{2,4}", content)
        if euro_price:
            offers.append(f"Published price point {euro_price.group(0)}")
        hours_match = re.search(r"(mon[^<\n]{0,80}(fri|sat|sun)[^<\n]{0,50})", c, re.I)
        booking_match = re.search(r"https?://[^\s\"'>]*(book|appointment|schedule)[^\s\"'>]*", content, re.I)
        if not booking_match and raw_html:
            href_matches = re.findall(r'href=[\'"]([^\'"]+)[\'"]', raw_html, flags=re.I)
            for href in href_matches:
                if re.search(r"book|appointment|schedule", href, re.I):
                    booking_match = re.match(r".*", urljoin(base_url, href))
                    if booking_match:
                        break
            if not booking_match:
                for href in href_matches:
                    if re.search(r"contact", href, re.I):
                        booking_match = re.match(r".*", urljoin(base_url, href))
                        if booking_match:
                            break

        service_keywords = [
            "travel vaccines",
            "sti clinic",
            "std tests",
            "smear test",
            "contraception",
            "blood tests",
            "family planning",
            "pregnancy testing",
            "ear wax removal",
            "general practice",
            "vaccines",
            "children's health",
            "maternity",
        ]
        services = [s.title() for s in service_keywords if s in c][:10]

        quality_score = 45.0
        quality_issues: list[str] = []
        if len(content) > 3500:
            quality_score += 25
        else:
            quality_issues.append("Thin website content")
        if phone:
            quality_score += 10
        else:
            quality_issues.append("Phone number not clearly visible")
        if email:
            quality_score += 5
        if booking_match:
            quality_score += 20
        else:
            quality_issues.append("No clear online booking link")
        if services:
            quality_score += 10
        else:
            quality_issues.append("Service menu not clearly structured")
        if re.search(r"testimonials|reviews|google reviews", c):
            quality_score += 8
        if re.search(r"open|opening hours|monday|friday", c):
            quality_score += 7
        else:
            quality_issues.append("Opening hours not clearly visible")
        if "testimonials" in c or "reviews" in c:
            quality_score += 10
        if "copyright 20" in c and ("2018" in c or "2019" in c or "2020" in c):
            quality_issues.append("Potentially outdated website")
            quality_score -= 10
        quality_score = max(0.0, min(100.0, quality_score))

        return {
            "business_type": btype,
            "services": services,
            "hours": hours_match.group(0).strip() if hours_match else "",
            "offers": offers[:6],
            "booking_url": booking_match.group(0).strip() if booking_match else "",
            "phone": phone.group(0).strip() if phone else "",
            "email": email.group(0) if email else "",
            "website_quality_score": quality_score,
            "website_quality_issues": quality_issues[:6],
            "confidence_score": 0.55 if services else 0.4,
            "source": "local",
        }
