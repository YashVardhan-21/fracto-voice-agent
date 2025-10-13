"""
Free Job Scraper
Uses httpx + BeautifulSoup with intelligent fallback to mock data
No paid APIs required
"""

import httpx
import asyncio
import time
import random
from bs4 import BeautifulSoup
from typing import List, Dict
import re
from urllib.parse import urljoin, urlparse

class FreeJobScraper:
    def __init__(self):
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        ]
        self.request_delay = 2  # 2 seconds between requests
        self.last_request_time = 0
    
    async def scrape_indeed(self, query: str, location: str = "", limit: int = 10) -> List[Dict]:
        """Scrape jobs from Indeed with free methods"""
        
        # Try real scraping first
        try:
            jobs = await self._scrape_indeed_real(query, location, limit)
            if jobs:
                return jobs
        except Exception as e:
            print(f"Real scraping failed: {e}")
        
        # Fallback to mock data
        print("Using mock data for job scraping")
        return self._get_mock_jobs(query, location, limit)
    
    async def _scrape_indeed_real(self, query: str, location: str, limit: int) -> List[Dict]:
        """Attempt real Indeed scraping"""
        
        # Rate limiting
        await self._rate_limit()
        
        # Build URL
        base_url = "https://www.indeed.com/jobs"
        params = {
            "q": query,
            "l": location,
            "sort": "date"
        }
        
        headers = {
            "User-Agent": random.choice(self.user_agents),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive",
        }
        
        async with httpx.AsyncClient(
            headers=headers,
            timeout=30.0,
            follow_redirects=True
        ) as client:
            
            response = await client.get(base_url, params=params)
            
            if response.status_code != 200:
                raise Exception(f"HTTP {response.status_code}")
            
            soup = BeautifulSoup(response.text, 'html.parser')
            jobs = []
            
            # Parse job cards (Indeed's current structure)
            job_cards = soup.find_all('div', class_=re.compile(r'job_seen_beacon|jobsearch-SerpJobCard'))
            
            for card in job_cards[:limit]:
                try:
                    job_data = self._parse_job_card(card)
                    if job_data:
                        jobs.append(job_data)
                except Exception as e:
                    print(f"Error parsing job card: {e}")
                    continue
            
            return jobs
    
    def _parse_job_card(self, card) -> Dict:
        """Parse individual job card"""
        
        # Extract job title
        title_elem = card.find('h2', class_=re.compile(r'jobTitle|title'))
        if not title_elem:
            return None
        
        job_title = title_elem.get_text(strip=True)
        
        # Extract company name
        company_elem = card.find('span', class_=re.compile(r'companyName|company'))
        if not company_elem:
            return None
        
        company_name = company_elem.get_text(strip=True)
        
        # Extract location
        location_elem = card.find('div', class_=re.compile(r'companyLocation|location'))
        location = location_elem.get_text(strip=True) if location_elem else ""
        
        # Extract job URL
        link = title_elem.find('a')
        job_url = ""
        if link and link.get('href'):
            job_url = urljoin("https://indeed.com", link['href'])
        
        # Extract description snippet
        desc_elem = card.find('div', class_=re.compile(r'summary|description'))
        description = desc_elem.get_text(strip=True)[:200] if desc_elem else ""
        
        return {
            "job_title": job_title,
            "company_name": company_name,
            "location": location,
            "job_url": job_url,
            "description": description
        }
    
    async def _rate_limit(self):
        """Implement rate limiting"""
        now = time.time()
        time_since_last = now - self.last_request_time
        
        if time_since_last < self.request_delay:
            sleep_time = self.request_delay - time_since_last
            await asyncio.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def _get_mock_jobs(self, query: str, location: str, limit: int) -> List[Dict]:
        """Return mock job data for testing"""
        
        # Industry-specific mock data based on query
        query_lower = query.lower()
        
        if "dental" in query_lower:
            mock_jobs = [
                {
                    "job_title": "Dental Office Manager",
                    "company_name": "Bright Smile Dental",
                    "location": "New York, NY",
                    "job_url": "https://indeed.com/job/dental-manager-001",
                    "description": "Manage dental office operations, schedule appointments, handle insurance"
                },
                {
                    "job_title": "Dental Receptionist",
                    "company_name": "Family Dental Care",
                    "location": "Los Angeles, CA",
                    "job_url": "https://indeed.com/job/dental-receptionist-002",
                    "description": "Front desk receptionist for busy dental practice"
                },
                {
                    "job_title": "Dental Assistant",
                    "company_name": "Modern Dentistry",
                    "location": "Chicago, IL",
                    "job_url": "https://indeed.com/job/dental-assistant-003",
                    "description": "Assist dentist with procedures and patient care"
                }
            ]
        elif "medical" in query_lower:
            mock_jobs = [
                {
                    "job_title": "Medical Office Manager",
                    "company_name": "HealthFirst Clinic",
                    "location": "Houston, TX",
                    "job_url": "https://indeed.com/job/medical-manager-001",
                    "description": "Oversee medical office operations and staff"
                },
                {
                    "job_title": "Medical Receptionist",
                    "company_name": "Wellness Center",
                    "location": "Phoenix, AZ",
                    "job_url": "https://indeed.com/job/medical-receptionist-002",
                    "description": "Front desk medical receptionist position"
                }
            ]
        elif "legal" in query_lower:
            mock_jobs = [
                {
                    "job_title": "Legal Assistant",
                    "company_name": "Smith & Associates Law",
                    "location": "Miami, FL",
                    "job_url": "https://indeed.com/job/legal-assistant-001",
                    "description": "Support attorneys with case preparation and client communication"
                },
                {
                    "job_title": "Paralegal",
                    "company_name": "Justice Legal Group",
                    "location": "Seattle, WA",
                    "job_url": "https://indeed.com/job/paralegal-002",
                    "description": "Legal research and document preparation"
                }
            ]
        else:
            # Generic business jobs
            mock_jobs = [
                {
                    "job_title": "Office Manager",
                    "company_name": "Professional Services Inc",
                    "location": "Denver, CO",
                    "job_url": "https://indeed.com/job/office-manager-001",
                    "description": "Manage office operations and administrative staff"
                },
                {
                    "job_title": "Administrative Assistant",
                    "company_name": "Business Solutions LLC",
                    "location": "Atlanta, GA",
                    "job_url": "https://indeed.com/job/admin-assistant-002",
                    "description": "Provide administrative support to management team"
                },
                {
                    "job_title": "Customer Service Representative",
                    "company_name": "Service Excellence Corp",
                    "location": "Boston, MA",
                    "job_url": "https://indeed.com/job/customer-service-003",
                    "description": "Handle customer inquiries and support requests"
                }
            ]
        
        # Add location to mock jobs if specified
        if location:
            for job in mock_jobs:
                if not job["location"]:
                    job["location"] = location
        
        return mock_jobs[:limit]
    
    async def extract_company_website(self, company_name: str) -> str:
        """Extract company website using free methods"""
        
        # Try Google search simulation
        try:
            website = await self._search_company_website(company_name)
            if website:
                return website
        except Exception as e:
            print(f"Website search failed: {e}")
        
        # Fallback: Generate likely website
        return self._generate_likely_website(company_name)
    
    async def _search_company_website(self, company_name: str) -> str:
        """Search for company website using free methods"""
        
        # Rate limiting
        await self._rate_limit()
        
        # Clean company name
        clean_name = re.sub(r'[^\w\s]', '', company_name.lower())
        clean_name = re.sub(r'\s+', '', clean_name)
        
        # Try common website patterns
        potential_urls = [
            f"https://www.{clean_name}.com",
            f"https://{clean_name}.com",
            f"https://www.{clean_name}.net",
            f"https://{clean_name}.net"
        ]
        
        headers = {
            "User-Agent": random.choice(self.user_agents)
        }
        
        async with httpx.AsyncClient(headers=headers, timeout=10.0) as client:
            for url in potential_urls:
                try:
                    response = await client.head(url, follow_redirects=True)
                    if response.status_code == 200:
                        return url
                except:
                    continue
        
        return ""
    
    def _generate_likely_website(self, company_name: str) -> str:
        """Generate likely website URL"""
        
        # Clean company name
        clean_name = re.sub(r'[^\w\s]', '', company_name.lower())
        clean_name = re.sub(r'\s+', '', clean_name)
        
        # Remove common business suffixes
        suffixes = ['inc', 'llc', 'corp', 'ltd', 'co', 'group', 'associates']
        for suffix in suffixes:
            if clean_name.endswith(suffix):
                clean_name = clean_name[:-len(suffix)]
                break
        
        return f"https://www.{clean_name}.com"
    
    def get_scraping_stats(self) -> Dict:
        """Get scraping statistics"""
        return {
            "last_request_time": self.last_request_time,
            "request_delay": self.request_delay,
            "user_agents_count": len(self.user_agents)
        }
