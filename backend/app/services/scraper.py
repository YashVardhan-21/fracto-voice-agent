import httpx
import asyncio
import re
from urllib.parse import quote_plus
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

    @staticmethod
    def _normalize_name(name: str) -> str:
        return re.sub(r"[^a-z0-9]+", "", (name or "").lower())

    @staticmethod
    def _score_lead(lead: dict) -> float:
        score = 0.0
        source = (lead.get("source") or "").lower()
        job_title = (lead.get("job_title") or "").lower()
        business_type = (lead.get("business_type_hint") or "").lower()
        location = (lead.get("location") or "").lower()

        if lead.get("job_title"):
            score += 35.0
        if source in {"indeed_public", "adzuna_public", "remotive_public"}:
            score += 15.0
        if any(k in job_title for k in ["reception", "front desk", "call", "customer", "appointment"]):
            score += 25.0
        if lead.get("phone"):
            score += 10.0
        if lead.get("website"):
            score += 10.0
        if location and "remote" not in location:
            score += 5.0
        if any(k in business_type for k in ["dental", "medical", "clinic", "law", "salon", "spa", "therapy"]):
            score += 10.0
        if source == "google_places_public":
            score += 20.0

        return round(min(score, 100.0), 2)

    def _rank_and_dedupe(self, leads: list[dict], limit: int) -> list[dict]:
        by_name: dict[str, dict] = {}
        for lead in leads:
            name = (lead.get("company_name") or "").strip()
            if not name:
                continue
            lead["lead_score"] = self._score_lead(lead)
            key = self._normalize_name(name)
            existing = by_name.get(key)
            if not existing or lead["lead_score"] > existing.get("lead_score", 0):
                by_name[key] = lead
        ranked = sorted(by_name.values(), key=lambda x: x.get("lead_score", 0), reverse=True)
        return ranked[:limit]

    async def scrape_indeed(self, keywords: str, location: str, limit: int = 20) -> tuple[list[dict], dict]:
        results = []
        diagnostics = {"source": "indeed_public", "url": "", "status_code": None, "blocked": False, "error": None}
        url = f"https://www.indeed.com/jobs?q={quote_plus(keywords)}&l={quote_plus(location)}&limit={min(limit, 50)}"
        diagnostics["url"] = url
        try:
            async with httpx.AsyncClient(headers=HEADERS, follow_redirects=True, timeout=30.0) as client:
                resp = await client.get(url)
                diagnostics["status_code"] = resp.status_code
                resp.raise_for_status()
                if re.search(r"captcha|verify you are human|security check|challenge", resp.text, re.I):
                    diagnostics["blocked"] = True
                    return [], diagnostics
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
                            "source": "indeed_public",
                            "website": None,
                            "phone": None,
                            "business_type_hint": None,
                        })
        except Exception as e:
            diagnostics["error"] = str(e)
            if "403" in str(e) or "429" in str(e):
                diagnostics["blocked"] = True
            print(f"Indeed scraping failed: {e}")
        finally:
            await asyncio.sleep(settings.scraping_delay_seconds)
        return results, diagnostics

    async def scrape_remotive(self, keywords: str, location: str, limit: int = 20) -> tuple[list[dict], dict]:
        diagnostics = {"source": "remotive_public", "url": "", "status_code": None, "error": None}
        url = f"https://remotive.com/api/remote-jobs?search={quote_plus(keywords)}"
        diagnostics["url"] = url
        results: list[dict] = []
        fallback_results: list[dict] = []
        try:
            async with httpx.AsyncClient(headers=HEADERS, follow_redirects=True, timeout=30.0) as client:
                resp = await client.get(url)
                diagnostics["status_code"] = resp.status_code
                resp.raise_for_status()
                jobs = resp.json().get("jobs", [])
                normalized_location = location.lower().strip()
                for job in jobs:
                    candidate_location = (job.get("candidate_required_location") or "").strip()
                    normalized_job = {
                        "company_name": job.get("company_name", "").strip(),
                        "job_title": job.get("title", "").strip(),
                        "location": candidate_location or "Remote",
                        "source": "remotive_public",
                        "website": None,
                        "phone": None,
                        "business_type_hint": None,
                    }
                    if normalized_job["company_name"] and normalized_job["job_title"]:
                        fallback_results.append(normalized_job)
                    if normalized_location and normalized_location not in {"remote", "any"}:
                        if candidate_location and candidate_location.lower() not in {"worldwide", "anywhere", "remote"}:
                            if normalized_location not in candidate_location.lower():
                                continue
                    results.append(normalized_job)
                    if len(results) >= limit:
                        break
                if not results and fallback_results:
                    diagnostics["error"] = "No location-specific results, returned remote matches"
                    results = fallback_results[:limit]
        except Exception as e:
            diagnostics["error"] = str(e)
            print(f"Remotive scraping failed: {e}")
        finally:
            await asyncio.sleep(settings.scraping_delay_seconds)
        return [r for r in results if r["company_name"] and r["job_title"]], diagnostics

    async def scrape_adzuna(self, keywords: str, location: str, limit: int = 20) -> tuple[list[dict], dict]:
        diagnostics = {"source": "adzuna_public", "url": "", "status_code": None, "error": None}
        if not settings.adzuna_app_id or not settings.adzuna_app_key:
            diagnostics["error"] = "ADZUNA_APP_ID or ADZUNA_APP_KEY missing"
            return [], diagnostics

        country = settings.adzuna_country.lower().strip()
        base_url = f"https://api.adzuna.com/v1/api/jobs/{country}/search/1"
        url = (
            f"{base_url}?app_id={quote_plus(settings.adzuna_app_id)}"
            f"&app_key={quote_plus(settings.adzuna_app_key)}"
            f"&results_per_page={min(limit, 50)}"
            f"&what={quote_plus(keywords)}"
            f"&where={quote_plus(location)}"
            f"&content-type=application/json"
        )
        diagnostics["url"] = url.replace(settings.adzuna_app_key, "***")
        results: list[dict] = []

        try:
            async with httpx.AsyncClient(headers=HEADERS, follow_redirects=True, timeout=30.0) as client:
                resp = await client.get(url)
                diagnostics["status_code"] = resp.status_code
                resp.raise_for_status()
                for job in resp.json().get("results", [])[:limit]:
                    company_name = (job.get("company") or {}).get("display_name", "").strip()
                    title = (job.get("title") or "").strip()
                    job_location = ((job.get("location") or {}).get("display_name") or "").strip()
                    redirect_url = (job.get("redirect_url") or "").strip()
                    if company_name and title:
                        results.append(
                            {
                                "company_name": company_name,
                                "job_title": title,
                                "location": job_location or location,
                                "source": "adzuna_public",
                                "website": redirect_url or None,
                                "phone": None,
                                "business_type_hint": None,
                            }
                        )
        except Exception as e:
            diagnostics["error"] = str(e)
            print(f"Adzuna scraping failed: {e}")
        finally:
            await asyncio.sleep(settings.scraping_delay_seconds)
        return results, diagnostics

    async def scrape_google_places(self, keywords: str, location: str, limit: int = 20) -> tuple[list[dict], dict]:
        diagnostics = {"source": "google_places_public", "url": "", "status_code": None, "error": None}
        if not settings.google_places_api_key:
            diagnostics["error"] = "GOOGLE_PLACES_API_KEY missing"
            return [], diagnostics

        categories = [
            "dental clinic",
            "medical clinic",
            "law firm",
            "salon",
            "spa",
            "physiotherapy clinic",
            "veterinary clinic",
            "real estate agency",
        ]
        per_query_limit = max(3, min(limit, 10))
        results: list[dict] = []

        try:
            async with httpx.AsyncClient(headers=HEADERS, follow_redirects=True, timeout=30.0) as client:
                async def _fetch_place_details(place_id: str) -> dict:
                    details_url = (
                        "https://maps.googleapis.com/maps/api/place/details/json"
                        f"?place_id={quote_plus(place_id)}"
                        "&fields=website,formatted_phone_number,opening_hours,url"
                        f"&key={quote_plus(settings.google_places_api_key)}"
                    )
                    details_resp = await client.get(details_url)
                    details_resp.raise_for_status()
                    details_payload = details_resp.json()
                    if details_payload.get("status") != "OK":
                        return {}
                    return details_payload.get("result", {}) or {}

                for category in categories:
                    if len(results) >= limit:
                        break
                    query = f"{category} in {location}"
                    url = (
                        "https://maps.googleapis.com/maps/api/place/textsearch/json"
                        f"?query={quote_plus(query)}&key={quote_plus(settings.google_places_api_key)}"
                    )
                    diagnostics["url"] = "https://maps.googleapis.com/maps/api/place/textsearch/json?query=<redacted>&key=***"
                    resp = await client.get(url)
                    diagnostics["status_code"] = resp.status_code
                    resp.raise_for_status()
                    payload = resp.json()
                    status = payload.get("status")
                    if status not in {"OK", "ZERO_RESULTS"}:
                        diagnostics["error"] = f"Google Places status: {status}"
                        continue
                    for place in payload.get("results", [])[:per_query_limit]:
                        name = (place.get("name") or "").strip()
                        if not name:
                            continue
                        place_types = place.get("types") or []
                        details = {}
                        place_id = place.get("place_id")
                        if place_id:
                            try:
                                details = await _fetch_place_details(place_id)
                            except Exception:
                                details = {}
                        hours_text = ""
                        opening_hours = details.get("opening_hours") or {}
                        weekday_text = opening_hours.get("weekday_text") or []
                        if isinstance(weekday_text, list) and weekday_text:
                            raw_hours = " | ".join(str(x).strip() for x in weekday_text[:3] if str(x).strip())
                            hours_text = re.sub(r"\s+", " ", raw_hours.replace("\u202f", " ").replace("\xa0", " ")).strip()
                        results.append(
                            {
                                "company_name": name,
                                "job_title": f"Likely needs front desk support ({category})",
                                "location": (place.get("formatted_address") or location).strip(),
                                "source": "google_places_public",
                                "website": (details.get("website") or "").strip() or None,
                                "phone": (details.get("formatted_phone_number") or "").strip() or None,
                                "hours": hours_text,
                                "booking_url": (details.get("url") or "").strip() or None,
                                "offers": [],
                                "business_type_hint": place_types[0] if place_types else category,
                            }
                        )
                        if len(results) >= limit:
                            break
        except Exception as e:
            diagnostics["error"] = str(e)
            print(f"Google Places scraping failed: {e}")
        finally:
            await asyncio.sleep(settings.scraping_delay_seconds)
        return results[:limit], diagnostics

    async def scrape_jobs(self, keywords: str, location: str, limit: int = 20) -> tuple[list[dict], dict]:
        per_source_limit = max(5, min(limit, settings.max_scraping_results, 25))
        all_leads: list[dict] = []
        attempts: list[dict] = []

        indeed_jobs, indeed_diag = await self.scrape_indeed(keywords, location, per_source_limit)
        indeed_diag["result_count"] = len(indeed_jobs)
        attempts.append(indeed_diag)
        all_leads.extend(indeed_jobs)

        adzuna_jobs, adzuna_diag = await self.scrape_adzuna(keywords, location, per_source_limit)
        adzuna_diag["result_count"] = len(adzuna_jobs)
        attempts.append(adzuna_diag)
        all_leads.extend(adzuna_jobs)

        places_leads, places_diag = await self.scrape_google_places(keywords, location, per_source_limit)
        places_diag["result_count"] = len(places_leads)
        attempts.append(places_diag)
        all_leads.extend(places_leads)

        remotive_jobs, remotive_diag = await self.scrape_remotive(keywords, location, per_source_limit)
        remotive_diag["result_count"] = len(remotive_jobs)
        attempts.append(remotive_diag)
        all_leads.extend(remotive_jobs)

        ranked_leads = self._rank_and_dedupe(all_leads, limit)
        if ranked_leads:
            selected_sources = sorted({lead.get("source", "unknown") for lead in ranked_leads})
            return ranked_leads, {"selected_source": ",".join(selected_sources), "attempts": attempts}

        if settings.allow_mock_scraping_fallback:
            mock = self._mock_data(location, limit)
            for row in mock:
                row["lead_score"] = self._score_lead(row)
                row["website"] = None
                row["phone"] = None
            return mock, {"selected_source": "mock", "attempts": attempts}

        return [], {"selected_source": None, "attempts": attempts}

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
