# DAY 1: Backend Core + Job Scraping
## 8-10 Hour Sprint

---

## 🌅 MORNING SESSION (4 hours) - 8:00 AM - 12:00 PM

### Task 1.1: Project Setup (1 hour) ⏰ 8:00-9:00 AM

```bash
# 1. Navigate to project directory
cd C:\Users\hp\Downloads\FRACTO_Voice_Agent_System_Complete

# 2. Initialize Git (if not already)
git init
git add .
git commit -m "Initial project structure"

# 3. Backend virtual environment
cd backend
python -m venv venv
venv\Scripts\activate

# 4. Install core dependencies
pip install fastapi==0.104.1 uvicorn==0.24.0 sqlalchemy==2.0.23 
pip install pydantic==2.5.0 httpx==0.25.2 beautifulsoup4==4.12.2
pip install python-dotenv==1.0.0 openai==1.3.5 requests==2.31.0

# 5. Create .env file
echo "OPENAI_API_KEY=your_key_here" > .env
echo "VAPI_API_KEY=your_key_here" >> .env
echo "SCRAPER_API_KEY=your_key_here" >> .env
echo "DATABASE_URL=sqlite:///./fracto.db" >> .env

# 6. Test FastAPI installation
python -c "import fastapi; print('FastAPI installed successfully')"
```

**Checkpoint:** ✅ Virtual environment active, dependencies installed, .env created

---

### Task 1.2: Database Schema (1 hour) ⏰ 9:00-10:00 AM

**File: backend/app/models.py**

```python
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Job(Base):
    __tablename__ = "jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    job_title = Column(String(255), nullable=False)
    company_name = Column(String(255), nullable=False)
    job_url = Column(String(500), nullable=False, unique=True)
    location = Column(String(255))
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship to company analysis
    company = relationship("Company", back_populates="jobs", uselist=False)

class Company(Base):
    __tablename__ = "companies"
    
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), unique=True)
    name = Column(String(255), nullable=False)
    website = Column(String(500))
    business_type = Column(String(100))  # dental, medical, legal, etc.
    services = Column(Text)  # JSON string of services
    contact_phone = Column(String(50))
    contact_email = Column(String(255))
    confidence_score = Column(Float, default=0.0)
    analyzed_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    jobs = relationship("Job", back_populates="company")
    voice_agents = relationship("VoiceAgent", back_populates="company")

class VoiceAgent(Base):
    __tablename__ = "voice_agents"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"))
    vapi_assistant_id = Column(String(255), unique=True)
    name = Column(String(255))
    prompt = Column(Text)
    voice_type = Column(String(50), default="jennifer")
    status = Column(String(50), default="created")  # created, tested, active, archived
    performance_score = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    company = relationship("Company", back_populates="voice_agents")

class Campaign(Base):
    __tablename__ = "campaigns"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    status = Column(String(50), default="pending")  # pending, processing, completed, failed
    job_search_query = Column(String(500))
    jobs_found = Column(Integer, default=0)
    agents_created = Column(Integer, default=0)
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)
```

**File: backend/app/database.py**

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./fracto.db")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)
    print("✅ Database initialized successfully")

def get_db():
    """Dependency for getting database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

**Test the database:**

```bash
cd backend
python -c "from app.database import init_db; init_db()"
```

**Checkpoint:** ✅ Database created with 4 tables (jobs, companies, voice_agents, campaigns)

---

### Task 1.3: Job Scraping Module (1.5 hours) ⏰ 10:00-11:30 AM

**File: backend/app/scrapers/job_scraper.py**

```python
import httpx
import os
from bs4 import BeautifulSoup
from typing import List, Dict
import re

class JobScraper:
    def __init__(self):
        self.scraper_api_key = os.getenv("SCRAPER_API_KEY")
        self.use_scraper_api = bool(self.scraper_api_key)
    
    def scrape_indeed(self, query: str, location: str = "", limit: int = 10) -> List[Dict]:
        """Scrape jobs from Indeed"""
        jobs = []
        
        # Build Indeed search URL
        base_url = "https://www.indeed.com/jobs"
        params = {"q": query, "l": location}
        
        try:
            if self.use_scraper_api:
                # Use ScraperAPI for reliable scraping
                url = f"http://api.scraperapi.com"
                response = httpx.get(url, params={
                    "api_key": self.scraper_api_key,
                    "url": f"{base_url}?q={query}&l={location}"
                }, timeout=30.0)
            else:
                # Direct scraping (may be blocked)
                response = httpx.get(base_url, params=params, timeout=30.0)
            
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Parse job cards (Indeed's structure)
            job_cards = soup.find_all('div', class_=re.compile('job_seen_beacon'))
            
            for card in job_cards[:limit]:
                try:
                    # Extract job details
                    title_elem = card.find('h2', class_='jobTitle')
                    company_elem = card.find('span', class_='companyName')
                    location_elem = card.find('div', class_='companyLocation')
                    
                    if title_elem and company_elem:
                        job_data = {
                            "job_title": title_elem.get_text(strip=True),
                            "company_name": company_elem.get_text(strip=True),
                            "location": location_elem.get_text(strip=True) if location_elem else "",
                            "job_url": "",  # Will extract website separately
                            "description": ""
                        }
                        
                        # Try to extract job URL
                        link = title_elem.find('a')
                        if link and link.get('href'):
                            job_data["job_url"] = f"https://indeed.com{link['href']}"
                        
                        jobs.append(job_data)
                
                except Exception as e:
                    print(f"Error parsing job card: {e}")
                    continue
        
        except Exception as e:
            print(f"Error scraping Indeed: {e}")
            # Return mock data for testing
            return self._get_mock_jobs(query, limit)
        
        return jobs
    
    def extract_company_website(self, company_name: str) -> str:
        """Extract company website using Google search or API"""
        try:
            # Simple heuristic: most companies have .com domain
            cleaned_name = company_name.lower().replace(' ', '').replace(',', '')
            potential_url = f"https://www.{cleaned_name}.com"
            
            # Quick check if website exists
            try:
                response = httpx.head(potential_url, timeout=5.0, follow_redirects=True)
                if response.status_code == 200:
                    return potential_url
            except:
                pass
            
            # Fallback: return empty and mark for manual review
            return ""
        
        except Exception as e:
            print(f"Error extracting website for {company_name}: {e}")
            return ""
    
    def _get_mock_jobs(self, query: str, limit: int) -> List[Dict]:
        """Return mock data for testing when scraping fails"""
        mock_jobs = [
            {
                "job_title": "Dental Office Manager",
                "company_name": "Bright Smile Dental",
                "location": "New York, NY",
                "job_url": "https://indeed.com/job/123",
                "description": "Manage dental office operations",
            },
            {
                "job_title": "Medical Receptionist",
                "company_name": "HealthFirst Clinic",
                "location": "Los Angeles, CA",
                "job_url": "https://indeed.com/job/456",
                "description": "Front desk medical receptionist",
            },
            {
                "job_title": "Legal Assistant",
                "company_name": "Smith & Associates Law",
                "location": "Chicago, IL",
                "job_url": "https://indeed.com/job/789",
                "description": "Legal assistant for law firm",
            },
        ]
        
        return mock_jobs[:limit]
```

**Checkpoint:** ✅ Job scraper module created (returns data even if APIs fail)

---

### Task 1.4: Website Analysis Module (1.5 hours) ⏰ 11:30 AM - 1:00 PM

**File: backend/app/analyzers/website_analyzer.py**

```python
import httpx
from bs4 import BeautifulSoup
import openai
import os
import re
import json
from typing import Dict

class WebsiteAnalyzer:
    def __init__(self):
        openai.api_key = os.getenv("OPENAI_API_KEY")
    
    def analyze_website(self, url: str, company_name: str) -> Dict:
        """Analyze company website and extract business information"""
        
        # Step 1: Scrape website content
        content = self._scrape_website(url)
        
        if not content:
            return {
                "success": False,
                "business_type": "unknown",
                "services": [],
                "contact_phone": "",
                "contact_email": "",
                "confidence_score": 0.0
            }
        
        # Step 2: Use GPT-4 to analyze content
        analysis = self._analyze_with_gpt(content, company_name)
        
        return analysis
    
    def _scrape_website(self, url: str) -> str:
        """Scrape website content"""
        try:
            response = httpx.get(url, timeout=10.0, follow_redirects=True)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.extract()
            
            # Get text content
            text = soup.get_text()
            
            # Clean up text
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            # Limit to first 3000 characters for GPT
            return text[:3000]
        
        except Exception as e:
            print(f"Error scraping website {url}: {e}")
            return ""
    
    def _analyze_with_gpt(self, content: str, company_name: str) -> Dict:
        """Use GPT-4 to analyze website content"""
        try:
            prompt = f"""Analyze this company website content and extract structured information.

Company Name: {company_name}

Website Content:
{content}

Extract the following information:
1. Business Type (dental, medical, legal, retail, restaurant, salon, spa, gym, other)
2. Services offered (list of 3-5 main services)
3. Contact phone number (if found)
4. Contact email (if found)
5. Confidence score (0.0-1.0 based on how clear the information is)

Return ONLY a JSON object with this exact structure:
{{
    "business_type": "dental",
    "services": ["General Dentistry", "Cosmetic Dentistry", "Orthodontics"],
    "contact_phone": "+1-555-1234",
    "contact_email": "info@example.com",
    "confidence_score": 0.85
}}"""

            response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a business analyst that extracts structured information from websites. Always return valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=500
            )
            
            result_text = response.choices[0].message.content.strip()
            
            # Extract JSON from response (handle markdown code blocks)
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0].strip()
            elif "```" in result_text:
                result_text = result_text.split("```")[1].split("```")[0].strip()
            
            result = json.loads(result_text)
            result["success"] = True
            
            return result
        
        except Exception as e:
            print(f"Error analyzing with GPT: {e}")
            return {
                "success": False,
                "business_type": "unknown",
                "services": [],
                "contact_phone": "",
                "contact_email": "",
                "confidence_score": 0.0
            }
```

**Checkpoint:** ✅ Website analyzer created with GPT-4 integration

---

## ☀️ AFTERNOON SESSION (4 hours) - 2:00 PM - 6:00 PM

### Task 1.5: FastAPI Endpoints (2 hours) ⏰ 2:00-4:00 PM

**File: backend/app/main.py**

```python
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
import os

from app.database import get_db, init_db
from app.models import Job, Company, VoiceAgent, Campaign
from app.scrapers.job_scraper import JobScraper
from app.analyzers.website_analyzer import WebsiteAnalyzer

# Initialize FastAPI app
app = FastAPI(
    title="FRACTO Voice Agent API",
    description="Automated voice agent creation for outreach campaigns",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database on startup
@app.on_event("startup")
def startup_event():
    init_db()
    print("🚀 FRACTO Voice Agent API started")

# Pydantic models for requests/responses
class JobSearchRequest(BaseModel):
    query: str
    location: Optional[str] = ""
    limit: Optional[int] = 10

class JobResponse(BaseModel):
    id: int
    job_title: str
    company_name: str
    location: str
    job_url: str
    
    class Config:
        from_attributes = True

class AnalyzeWebsiteRequest(BaseModel):
    url: str
    company_name: str

class CompanyResponse(BaseModel):
    id: int
    name: str
    website: Optional[str]
    business_type: Optional[str]
    services: Optional[str]
    confidence_score: float
    
    class Config:
        from_attributes = True

# Endpoints

@app.get("/")
def root():
    return {
        "message": "FRACTO Voice Agent API",
        "docs": "/docs",
        "status": "running"
    }

@app.post("/api/scrape-jobs", response_model=List[JobResponse])
def scrape_jobs(request: JobSearchRequest, db: Session = Depends(get_db)):
    """Scrape jobs from Indeed and store in database"""
    
    scraper = JobScraper()
    jobs_data = scraper.scrape_indeed(
        query=request.query,
        location=request.location,
        limit=request.limit
    )
    
    saved_jobs = []
    
    for job_data in jobs_data:
        # Check if job already exists
        existing_job = db.query(Job).filter(Job.job_url == job_data["job_url"]).first()
        
        if not existing_job:
            # Create new job
            new_job = Job(
                job_title=job_data["job_title"],
                company_name=job_data["company_name"],
                location=job_data["location"],
                job_url=job_data["job_url"],
                description=job_data.get("description", "")
            )
            db.add(new_job)
            db.commit()
            db.refresh(new_job)
            saved_jobs.append(new_job)
        else:
            saved_jobs.append(existing_job)
    
    return saved_jobs

@app.post("/api/analyze-website", response_model=CompanyResponse)
def analyze_website(request: AnalyzeWebsiteRequest, db: Session = Depends(get_db)):
    """Analyze company website and extract business information"""
    
    analyzer = WebsiteAnalyzer()
    analysis = analyzer.analyze_website(request.url, request.company_name)
    
    if not analysis.get("success"):
        raise HTTPException(status_code=400, detail="Failed to analyze website")
    
    # Create or update company record
    company = Company(
        name=request.company_name,
        website=request.url,
        business_type=analysis["business_type"],
        services=", ".join(analysis.get("services", [])),
        contact_phone=analysis.get("contact_phone", ""),
        contact_email=analysis.get("contact_email", ""),
        confidence_score=analysis.get("confidence_score", 0.0)
    )
    
    db.add(company)
    db.commit()
    db.refresh(company)
    
    return company

@app.get("/api/jobs", response_model=List[JobResponse])
def get_jobs(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all jobs"""
    jobs = db.query(Job).offset(skip).limit(limit).all()
    return jobs

@app.get("/api/companies", response_model=List[CompanyResponse])
def get_companies(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all analyzed companies"""
    companies = db.query(Company).offset(skip).limit(limit).all()
    return companies

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

**Test the API:**

```bash
cd backend
uvicorn app.main:app --reload

# Open browser: http://localhost:8000/docs
# Test /api/scrape-jobs endpoint
```

**Checkpoint:** ✅ API running with Swagger docs, can scrape and analyze

---

### Task 1.6: Integration Testing (2 hours) ⏰ 4:00-6:00 PM

**Create test script: backend/test_day1.py**

```python
import requests
import json

BASE_URL = "http://localhost:8000"

def test_scrape_jobs():
    """Test job scraping"""
    print("Testing job scraping...")
    
    response = requests.post(f"{BASE_URL}/api/scrape-jobs", json={
        "query": "dental office manager",
        "location": "New York",
        "limit": 5
    })
    
    print(f"Status: {response.status_code}")
    jobs = response.json()
    print(f"Jobs found: {len(jobs)}")
    
    for job in jobs:
        print(f"  - {job['job_title']} at {job['company_name']}")
    
    return jobs

def test_analyze_website(url, company_name):
    """Test website analysis"""
    print(f"\nTesting website analysis for {company_name}...")
    
    response = requests.post(f"{BASE_URL}/api/analyze-website", json={
        "url": url,
        "company_name": company_name
    })
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        analysis = response.json()
        print(f"Business Type: {analysis['business_type']}")
        print(f"Services: {analysis['services']}")
        print(f"Confidence: {analysis['confidence_score']}")
    else:
        print(f"Error: {response.text}")

if __name__ == "__main__":
    # Test 1: Scrape jobs
    jobs = test_scrape_jobs()
    
    # Test 2: Analyze sample websites
    test_websites = [
        ("https://www.aspendental.com", "Aspen Dental"),
        ("https://www.kleinerperkins.com", "Kleiner Perkins"),  # Test non-dental
    ]
    
    for url, name in test_websites:
        test_analyze_website(url, name)
    
    print("\n✅ Day 1 testing complete!")
```

**Run tests:**

```bash
cd backend
python test_day1.py
```

**Manual Testing Checklist:**
- [ ] API starts without errors
- [ ] Swagger UI loads at /docs
- [ ] Can scrape at least 3 jobs
- [ ] Can analyze at least 1 website
- [ ] Database has data (check with SQLite browser)
- [ ] No critical errors in console

**Checkpoint:** ✅ All Day 1 features working, data in database

---

## 🌙 EVENING WRAP-UP (1 hour) - 6:00-7:00 PM

### Documentation & Cleanup

1. **Update .env.example:**
```env
OPENAI_API_KEY=sk-your-key-here
VAPI_API_KEY=your-vapi-key
SCRAPER_API_KEY=your-scraper-key
DATABASE_URL=sqlite:///./fracto.db
```

2. **Create backend/README.md:**
```markdown
# FRACTO Backend - Day 1 Complete

## Setup
1. Create virtual environment: `python -m venv venv`
2. Activate: `venv\Scripts\activate`
3. Install: `pip install -r requirements.txt`
4. Configure: Copy `.env.example` to `.env` and add keys
5. Run: `uvicorn app.main:app --reload`

## Endpoints
- POST /api/scrape-jobs - Scrape jobs from Indeed
- POST /api/analyze-website - Analyze company website
- GET /api/jobs - Get all jobs
- GET /api/companies - Get all companies

## Testing
Run `python test_day1.py` to test all endpoints
```

3. **Git commit:**
```bash
git add .
git commit -m "Day 1 complete: Job scraping + website analysis"
```

---

## 🎯 DAY 1 SUCCESS CRITERIA

**Must Be Completed:**
- ✅ Virtual environment and dependencies installed
- ✅ Database with 4 tables created
- ✅ Job scraper returns data (real or mock)
- ✅ Website analyzer extracts business info
- ✅ FastAPI running with Swagger docs
- ✅ Can scrape 10 jobs via API
- ✅ Can analyze 1 website via API
- ✅ All data stored in database

**Stretch Goals (If Time):**
- ⭐ Scraper works with real Indeed data
- ⭐ Added error handling and logging
- ⭐ Created unit tests
- ⭐ Deployed to Railway/Render

---

## 🐛 TROUBLESHOOTING

**Import errors:**
```bash
# Make sure PYTHONPATH includes app directory
cd backend
export PYTHONPATH=.  # Linux/Mac
$env:PYTHONPATH="." # Windows PowerShell
```

**Database errors:**
```bash
# Delete and recreate database
rm fracto.db
python -c "from app.database import init_db; init_db()"
```

**OpenAI API errors:**
```bash
# Test API key
python -c "import openai; openai.api_key='YOUR_KEY'; print('OK')"
```

---

## 📝 NOTES FOR DAY 2

Tomorrow we'll build:
1. LLM prompt generation for voice agents
2. VAPI integration to create assistants
3. Complete workflow orchestration
4. Background task processing

**Data to have ready:**
- 10+ jobs in database
- 5+ analyzed companies
- API keys for VAPI and Gemini

---

**Good luck! 🚀 Ship Day 1 by 7 PM!**

