import httpx
import asyncio
import re
from bs4 import BeautifulSoup
from app.config import settings

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}

class JobScraper:
    """
    Scrapes Indeed for publicly-listed job postings.
    Collects only: company name, job title, location — no personal data.
    GDPR-safe: public business information only.
    """

    async def scrape_indeed(self, keywords: str, location: str, limit: int = 20) -> list[dict]:
        results = []
        url = (
            f"https://www.indeed.com/jobs"
            f"?q={keywords.replace(' ', '+')}"
            f"&l={location.replace(' ', '+')}"
            f"&limit={min(limit, 50)}"
        )
        try:
            async with httpx.AsyncClient(headers=HEADERS, follow_redirects=True, timeout=30.0) as client:
                resp = await client.get(url)
                resp.raise_for_status()
                soup = BeautifulSoup(resp.text, "html.parser")
                cards = soup.find_all("div", class_=re.compile(r"job_seen_beacon|jobsearch-SerpJobCard"))
                for card in cards[:limit]:
                    company = (
                        card.find(attrs={"data-testid": "company-name"})
                        or card.find(class_=re.compile("companyName"))
                    )
                    title = card.find(class_=re.compile("jobTitle"))
                    loc = (
                        card.find(attrs={"data-testid": "text-location"})
                        or card.find(class_=re.compile("companyLocation"))
                    )
                    if company and title:
                        results.append({
                            "company_name": company.get_text(strip=True),
                            "job_title": title.get_text(strip=True),
                            "location": loc.get_text(strip=True) if loc else "",
                            "source": "indeed",
                        })
        except Exception as e:
            print(f"Indeed scraping failed: {e} — using mock data")
            results = self._mock_data(location, limit)
        finally:
            await asyncio.sleep(settings.scraping_delay_seconds)
        return results if results else self._mock_data(location, limit)

    def _mock_data(self, location: str, limit: int) -> list[dict]:
        templates = [
            ("Bright Smile Dental", "Receptionist", "dental"),
            ("City Medical Clinic", "Front Desk Coordinator", "medical"),
            ("Smith & Associates Law", "Legal Receptionist", "legal"),
            ("Serenity Wellness Spa", "Appointment Coordinator", "salon"),
            ("Peak Physical Therapy", "Patient Coordinator", "medical"),
        ]
        return [
            {
                "company_name": t[0],
                "job_title": t[1],
                "location": location,
                "source": "mock",
                "business_type_hint": t[2],
            }
            for t in templates[:limit]
        ]
