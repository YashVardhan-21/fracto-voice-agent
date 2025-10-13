# DAY 2: LLM Integration + VAPI Voice Agents
## 8-10 Hour Sprint

---

## 🌅 MORNING SESSION (4 hours) - 8:00 AM - 12:00 PM

### Task 2.1: Prompt Generation System (2 hours) ⏰ 8:00-10:00 AM

**File: backend/app/generators/prompt_generator.py**

```python
import openai
import os
from typing import Dict, List
import json

class PromptGenerator:
    def __init__(self):
        openai.api_key = os.getenv("OPENAI_API_KEY")
        self.templates = self._load_templates()
    
    def _load_templates(self) -> Dict[str, str]:
        """Load industry-specific prompt templates"""
        return {
            "dental": """You are a friendly AI receptionist for {company_name}, a dental practice in {location}.

Your role:
- Answer questions about our services: {services}
- Schedule appointments for new patients
- Provide information about dental procedures
- Handle emergency dental inquiries

Key information:
- We accept most insurance plans
- New patient exams include X-rays and cleaning
- Emergency appointments available same-day
{contact_info}

Always be warm, professional, and reassuring. Many patients are nervous about dental visits.""",
            
            "medical": """You are a professional medical receptionist for {company_name}, a healthcare facility in {location}.

Your responsibilities:
- Schedule patient appointments
- Answer questions about our services: {services}
- Provide general medical information (not medical advice)
- Handle insurance inquiries
- Triage urgent medical needs

Important notes:
- All medical advice comes from our physicians
- We maintain strict HIPAA compliance
- Emergency cases: direct to 911 or ER
{contact_info}

Be professional, empathetic, and efficient.""",
            
            "legal": """You are an experienced legal assistant for {company_name}, a law firm in {location}.

Your duties:
- Schedule consultations with attorneys
- Provide information about our practice areas: {services}
- Collect basic case information
- Answer general questions about legal processes
- Screen potential clients

Key points:
- Initial consultations are typically 30-60 minutes
- Client confidentiality is paramount
- No legal advice given without attorney review
{contact_info}

Be professional, discrete, and detail-oriented.""",
            
            "default": """You are a helpful AI assistant for {company_name}, located in {location}.

Your role:
- Answer questions about our business
- Provide information about our services: {services}
- Schedule appointments or consultations
- Connect callers with the right department
{contact_info}

Always be friendly, professional, and helpful."""
        }
    
    def generate_prompt(self, company_data: Dict) -> str:
        """Generate custom prompt for a company"""
        
        business_type = company_data.get("business_type", "default")
        template = self.templates.get(business_type, self.templates["default"])
        
        # Prepare contact info
        contact_info = ""
        if company_data.get("contact_phone"):
            contact_info += f"\nPhone: {company_data['contact_phone']}"
        if company_data.get("contact_email"):
            contact_info += f"\nEmail: {company_data['contact_email']}"
        if company_data.get("website"):
            contact_info += f"\nWebsite: {company_data['website']}"
        
        # Fill in template
        prompt = template.format(
            company_name=company_data.get("name", "our company"),
            location=company_data.get("location", "your area"),
            services=company_data.get("services", "various services"),
            contact_info=contact_info
        )
        
        # Enhance with GPT-4
        enhanced_prompt = self._enhance_with_gpt(prompt, company_data)
        
        return enhanced_prompt
    
    def _enhance_with_gpt(self, base_prompt: str, company_data: Dict) -> str:
        """Use GPT-4 to enhance the prompt with specific details"""
        try:
            system_message = """You are an expert at creating voice agent prompts. 
Enhance the given prompt with:
1. More specific details about the business
2. Common questions customers might ask
3. Better conversation flow
4. Professional personality traits

Keep the enhanced prompt under 600 words. Make it natural and conversational."""

            user_message = f"""Base Prompt:
{base_prompt}

Company Details:
- Name: {company_data.get('name')}
- Type: {company_data.get('business_type')}
- Services: {company_data.get('services')}

Enhance this prompt to make it more effective for a voice agent."""

            response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.7,
                max_tokens=800
            )
            
            enhanced = response.choices[0].message.content.strip()
            return enhanced
        
        except Exception as e:
            print(f"Error enhancing prompt with GPT: {e}")
            return base_prompt
    
    def generate_test_questions(self, business_type: str) -> List[str]:
        """Generate test questions for voice agent testing"""
        questions = {
            "dental": [
                "Do you accept my insurance?",
                "I have a toothache, can I get an emergency appointment?",
                "How much does a teeth cleaning cost?",
                "What are your office hours?",
                "Do you offer Invisalign?"
            ],
            "medical": [
                "I need to schedule a physical exam",
                "Do you accept Medicare?",
                "What should I bring to my first appointment?",
                "Can I see a doctor today?",
                "Do you have weekend hours?"
            ],
            "legal": [
                "I need a divorce attorney",
                "How much do you charge?",
                "What's included in a free consultation?",
                "Do you take payment plans?",
                "How long does a case typically take?"
            ],
            "default": [
                "What services do you offer?",
                "What are your hours?",
                "How can I schedule an appointment?",
                "Where are you located?",
                "Do you offer free consultations?"
            ]
        }
        
        return questions.get(business_type, questions["default"])
```

**Test the prompt generator:**

```python
# backend/test_prompts.py
from app.generators.prompt_generator import PromptGenerator

generator = PromptGenerator()

# Test data
company_data = {
    "name": "Bright Smile Dental",
    "business_type": "dental",
    "location": "New York, NY",
    "services": "General Dentistry, Cosmetic Dentistry, Orthodontics",
    "contact_phone": "+1-555-0123",
    "website": "https://brightsmile.com"
}

prompt = generator.generate_prompt(company_data)
print("Generated Prompt:")
print(prompt)
print("\n" + "="*80 + "\n")

questions = generator.generate_test_questions("dental")
print("Test Questions:")
for q in questions:
    print(f"  - {q}")
```

**Checkpoint:** ✅ Prompt generator creates industry-specific prompts

---

### Task 2.2: VAPI Integration (2 hours) ⏰ 10:00 AM - 12:00 PM

**File: backend/app/integrations/vapi_client.py**

```python
import httpx
import os
from typing import Dict, Optional

class VAPIClient:
    def __init__(self):
        self.api_key = os.getenv("VAPI_API_KEY")
        self.base_url = "https://api.vapi.ai"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def create_assistant(
        self,
        name: str,
        prompt: str,
        voice: str = "jennifer",
        language: str = "en-US"
    ) -> Dict:
        """Create a new VAPI voice assistant"""
        
        payload = {
            "name": name,
            "model": {
                "provider": "openai",
                "model": "gpt-4",
                "messages": [
                    {
                        "role": "system",
                        "content": prompt
                    }
                ],
                "temperature": 0.7
            },
            "voice": {
                "provider": "11labs",  # or "playht", "deepgram"
                "voiceId": voice
            },
            "firstMessage": "Hello! Thank you for calling. How can I help you today?",
            "endCallMessage": "Thank you for calling. Have a great day!",
            "endCallPhrases": ["goodbye", "thank you, bye", "that's all"],
            "recordingEnabled": True,
            "hipaaEnabled": False,  # Set to true for medical practices
            "metadata": {
                "created_by": "FRACTO_Automation"
            }
        }
        
        try:
            response = httpx.post(
                f"{self.base_url}/assistant",
                headers=self.headers,
                json=payload,
                timeout=30.0
            )
            
            response.raise_for_status()
            result = response.json()
            
            return {
                "success": True,
                "assistant_id": result.get("id"),
                "name": result.get("name"),
                "phone_number": result.get("phoneNumber"),
                "data": result
            }
        
        except httpx.HTTPStatusError as e:
            return {
                "success": False,
                "error": f"HTTP {e.response.status_code}: {e.response.text}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_assistant(self, assistant_id: str) -> Dict:
        """Get assistant details"""
        try:
            response = httpx.get(
                f"{self.base_url}/assistant/{assistant_id}",
                headers=self.headers,
                timeout=10.0
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def update_assistant(self, assistant_id: str, updates: Dict) -> Dict:
        """Update an existing assistant"""
        try:
            response = httpx.patch(
                f"{self.base_url}/assistant/{assistant_id}",
                headers=self.headers,
                json=updates,
                timeout=30.0
            )
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def delete_assistant(self, assistant_id: str) -> Dict:
        """Delete an assistant"""
        try:
            response = httpx.delete(
                f"{self.base_url}/assistant/{assistant_id}",
                headers=self.headers,
                timeout=10.0
            )
            response.raise_for_status()
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def make_test_call(self, assistant_id: str, phone_number: str) -> Dict:
        """Make a test call with the assistant"""
        try:
            payload = {
                "assistantId": assistant_id,
                "phoneNumber": phone_number
            }
            
            response = httpx.post(
                f"{self.base_url}/call",
                headers=self.headers,
                json=payload,
                timeout=30.0
            )
            response.raise_for_status()
            
            return {
                "success": True,
                "call_id": response.json().get("id"),
                "status": response.json().get("status")
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_call_recording(self, call_id: str) -> Dict:
        """Get call recording and transcript"""
        try:
            response = httpx.get(
                f"{self.base_url}/call/{call_id}",
                headers=self.headers,
                timeout=10.0
            )
            response.raise_for_status()
            
            call_data = response.json()
            return {
                "success": True,
                "transcript": call_data.get("transcript"),
                "recording_url": call_data.get("recordingUrl"),
                "duration": call_data.get("duration"),
                "cost": call_data.get("cost")
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
```

**Add VAPI endpoints to main.py:**

```python
# Add to backend/app/main.py

from app.integrations.vapi_client import VAPIClient
from app.generators.prompt_generator import PromptGenerator

class CreateVoiceAgentRequest(BaseModel):
    company_id: int

@app.post("/api/create-voice-agent")
def create_voice_agent(request: CreateVoiceAgentRequest, db: Session = Depends(get_db)):
    """Create a VAPI voice agent for a company"""
    
    # Get company data
    company = db.query(Company).filter(Company.id == request.company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    # Generate prompt
    generator = PromptGenerator()
    prompt = generator.generate_prompt({
        "name": company.name,
        "business_type": company.business_type,
        "location": "",  # Add if you have it
        "services": company.services,
        "contact_phone": company.contact_phone,
        "contact_email": company.contact_email,
        "website": company.website
    })
    
    # Create VAPI assistant
    vapi = VAPIClient()
    result = vapi.create_assistant(
        name=f"{company.name} - Voice Agent",
        prompt=prompt,
        voice="jennifer"
    )
    
    if not result.get("success"):
        raise HTTPException(status_code=500, detail=result.get("error"))
    
    # Save to database
    voice_agent = VoiceAgent(
        company_id=company.id,
        vapi_assistant_id=result["assistant_id"],
        name=result["name"],
        prompt=prompt,
        voice_type="jennifer",
        status="created"
    )
    
    db.add(voice_agent)
    db.commit()
    db.refresh(voice_agent)
    
    return {
        "success": True,
        "agent_id": voice_agent.id,
        "vapi_assistant_id": voice_agent.vapi_assistant_id,
        "phone_number": result.get("phone_number"),
        "prompt": prompt
    }
```

**Checkpoint:** ✅ VAPI integration working, can create voice agents

---

## ☀️ AFTERNOON SESSION (4 hours) - 2:00 PM - 6:00 PM

### Task 2.3: Complete Workflow Orchestration (2 hours) ⏰ 2:00-4:00 PM

**File: backend/app/core/workflow.py**

```python
from sqlalchemy.orm import Session
from app.models import Job, Company, VoiceAgent, Campaign
from app.scrapers.job_scraper import JobScraper
from app.analyzers.website_analyzer import WebsiteAnalyzer
from app.generators.prompt_generator import PromptGenerator
from app.integrations.vapi_client import VAPIClient
import time
from typing import Dict, List

class WorkflowOrchestrator:
    def __init__(self, db: Session):
        self.db = db
        self.job_scraper = JobScraper()
        self.website_analyzer = WebsiteAnalyzer()
        self.prompt_generator = PromptGenerator()
        self.vapi_client = VAPIClient()
    
    def process_campaign(
        self,
        campaign_name: str,
        job_query: str,
        location: str = "",
        limit: int = 10
    ) -> Dict:
        """
        Complete workflow:
        1. Scrape jobs
        2. Analyze company websites
        3. Generate prompts
        4. Create voice agents
        """
        
        # Create campaign record
        campaign = Campaign(
            name=campaign_name,
            job_search_query=f"{job_query} in {location}",
            status="processing"
        )
        self.db.add(campaign)
        self.db.commit()
        
        results = {
            "campaign_id": campaign.id,
            "jobs_processed": 0,
            "agents_created": 0,
            "errors": []
        }
        
        try:
            # Step 1: Scrape jobs
            print(f"📋 Scraping jobs for: {job_query}")
            jobs_data = self.job_scraper.scrape_indeed(job_query, location, limit)
            
            for job_data in jobs_data:
                try:
                    # Check if job exists
                    job = self.db.query(Job).filter(Job.job_url == job_data["job_url"]).first()
                    
                    if not job:
                        job = Job(
                            job_title=job_data["job_title"],
                            company_name=job_data["company_name"],
                            location=job_data["location"],
                            job_url=job_data["job_url"],
                            description=job_data.get("description", "")
                        )
                        self.db.add(job)
                        self.db.commit()
                        self.db.refresh(job)
                    
                    results["jobs_processed"] += 1
                    
                    # Step 2: Analyze company website
                    website = self.job_scraper.extract_company_website(job.company_name)
                    
                    if not website:
                        print(f"⚠️  No website found for {job.company_name}")
                        results["errors"].append(f"No website for {job.company_name}")
                        continue
                    
                    print(f"🔍 Analyzing website: {website}")
                    analysis = self.website_analyzer.analyze_website(website, job.company_name)
                    
                    if not analysis.get("success"):
                        print(f"⚠️  Analysis failed for {website}")
                        results["errors"].append(f"Analysis failed for {job.company_name}")
                        continue
                    
                    # Create or update company record
                    company = self.db.query(Company).filter(Company.job_id == job.id).first()
                    
                    if not company:
                        company = Company(
                            job_id=job.id,
                            name=job.company_name,
                            website=website,
                            business_type=analysis["business_type"],
                            services=", ".join(analysis.get("services", [])),
                            contact_phone=analysis.get("contact_phone", ""),
                            contact_email=analysis.get("contact_email", ""),
                            confidence_score=analysis.get("confidence_score", 0.0)
                        )
                        self.db.add(company)
                        self.db.commit()
                        self.db.refresh(company)
                    
                    # Step 3: Generate prompt
                    print(f"✍️  Generating prompt for {company.name}")
                    prompt = self.prompt_generator.generate_prompt({
                        "name": company.name,
                        "business_type": company.business_type,
                        "location": job.location,
                        "services": company.services,
                        "contact_phone": company.contact_phone,
                        "contact_email": company.contact_email,
                        "website": company.website
                    })
                    
                    # Step 4: Create voice agent
                    print(f"🎙️  Creating voice agent for {company.name}")
                    vapi_result = self.vapi_client.create_assistant(
                        name=f"{company.name} - Voice Agent",
                        prompt=prompt,
                        voice="jennifer"
                    )
                    
                    if not vapi_result.get("success"):
                        print(f"⚠️  VAPI creation failed: {vapi_result.get('error')}")
                        results["errors"].append(f"VAPI failed for {company.name}")
                        continue
                    
                    # Save voice agent
                    voice_agent = VoiceAgent(
                        company_id=company.id,
                        vapi_assistant_id=vapi_result["assistant_id"],
                        name=vapi_result["name"],
                        prompt=prompt,
                        voice_type="jennifer",
                        status="created"
                    )
                    self.db.add(voice_agent)
                    self.db.commit()
                    
                    results["agents_created"] += 1
                    print(f"✅ Voice agent created: {voice_agent.vapi_assistant_id}")
                    
                    # Rate limiting
                    time.sleep(2)
                
                except Exception as e:
                    print(f"❌ Error processing job: {e}")
                    results["errors"].append(str(e))
                    continue
            
            # Update campaign
            campaign.status = "completed"
            campaign.jobs_found = results["jobs_processed"]
            campaign.agents_created = results["agents_created"]
            self.db.commit()
            
            return results
        
        except Exception as e:
            campaign.status = "failed"
            campaign.error_message = str(e)
            self.db.commit()
            raise
```

**Add workflow endpoint to main.py:**

```python
# Add to backend/app/main.py

from app.core.workflow import WorkflowOrchestrator

class ProcessCampaignRequest(BaseModel):
    campaign_name: str
    job_query: str
    location: Optional[str] = ""
    limit: Optional[int] = 10

@app.post("/api/process-campaign")
def process_campaign(request: ProcessCampaignRequest, db: Session = Depends(get_db)):
    """Process complete campaign: scrape -> analyze -> create agents"""
    
    orchestrator = WorkflowOrchestrator(db)
    
    results = orchestrator.process_campaign(
        campaign_name=request.campaign_name,
        job_query=request.job_query,
        location=request.location,
        limit=request.limit
    )
    
    return results
```

**Checkpoint:** ✅ Complete workflow working end-to-end

---

### Task 2.4: Background Task Processing (2 hours) ⏰ 4:00-6:00 PM

**Simple background tasks (without Celery):**

```python
# backend/app/core/background_tasks.py

import threading
import time
from typing import Callable, Dict
import queue

class BackgroundTaskManager:
    def __init__(self):
        self.task_queue = queue.Queue()
        self.results = {}
        self.worker_thread = None
        self.running = False
    
    def start(self):
        """Start background worker"""
        if not self.running:
            self.running = True
            self.worker_thread = threading.Thread(target=self._worker, daemon=True)
            self.worker_thread.start()
            print("🚀 Background task worker started")
    
    def stop(self):
        """Stop background worker"""
        self.running = False
        if self.worker_thread:
            self.worker_thread.join(timeout=5)
    
    def _worker(self):
        """Worker thread that processes tasks"""
        while self.running:
            try:
                if not self.task_queue.empty():
                    task_id, func, args, kwargs = self.task_queue.get(timeout=1)
                    
                    print(f"📋 Processing task {task_id}")
                    try:
                        result = func(*args, **kwargs)
                        self.results[task_id] = {
                            "status": "completed",
                            "result": result
                        }
                        print(f"✅ Task {task_id} completed")
                    except Exception as e:
                        self.results[task_id] = {
                            "status": "failed",
                            "error": str(e)
                        }
                        print(f"❌ Task {task_id} failed: {e}")
                else:
                    time.sleep(0.5)
            except queue.Empty:
                continue
    
    def submit_task(self, task_id: str, func: Callable, *args, **kwargs):
        """Submit a task to the queue"""
        self.task_queue.put((task_id, func, args, kwargs))
        self.results[task_id] = {"status": "pending"}
        print(f"📥 Task {task_id} queued")
    
    def get_task_status(self, task_id: str) -> Dict:
        """Get task status"""
        return self.results.get(task_id, {"status": "not_found"})

# Global task manager
task_manager = BackgroundTaskManager()
```

**Update main.py to use background tasks:**

```python
# Add to backend/app/main.py

from app.core.background_tasks import task_manager
import uuid

@app.on_event("startup")
def startup_event():
    init_db()
    task_manager.start()  # Start background worker
    print("🚀 FRACTO Voice Agent API started")

@app.on_event("shutdown")
def shutdown_event():
    task_manager.stop()
    print("🛑 FRACTO Voice Agent API stopped")

@app.post("/api/process-campaign-async")
def process_campaign_async(request: ProcessCampaignRequest, db: Session = Depends(get_db)):
    """Process campaign in background"""
    
    task_id = str(uuid.uuid4())
    
    orchestrator = WorkflowOrchestrator(db)
    
    # Submit to background queue
    task_manager.submit_task(
        task_id,
        orchestrator.process_campaign,
        request.campaign_name,
        request.job_query,
        request.location,
        request.limit
    )
    
    return {
        "task_id": task_id,
        "status": "queued",
        "message": "Campaign processing started in background"
    }

@app.get("/api/task-status/{task_id}")
def get_task_status(task_id: str):
    """Get status of background task"""
    status = task_manager.get_task_status(task_id)
    return status
```

**Checkpoint:** ✅ Background task processing working

---

## 🌙 EVENING WRAP-UP (1 hour) - 6:00-7:00 PM

### Testing & Documentation

**Create comprehensive test script:**

```python
# backend/test_day2.py

import requests
import time
import json

BASE_URL = "http://localhost:8000"

def test_complete_workflow():
    """Test end-to-end workflow"""
    print("🧪 Testing complete workflow...\n")
    
    # Test async campaign processing
    response = requests.post(f"{BASE_URL}/api/process-campaign-async", json={
        "campaign_name": "Dental Offices NYC - Test",
        "job_query": "dental office manager",
        "location": "New York",
        "limit": 3
    })
    
    print(f"Campaign started: {response.status_code}")
    data = response.json()
    task_id = data["task_id"]
    print(f"Task ID: {task_id}\n")
    
    # Poll for status
    for i in range(30):
        time.sleep(5)
        status_response = requests.get(f"{BASE_URL}/api/task-status/{task_id}")
        status = status_response.json()
        
        print(f"Status check {i+1}: {status['status']}")
        
        if status["status"] == "completed":
            print("\n✅ Campaign completed!")
            result = status["result"]
            print(f"Jobs processed: {result['jobs_processed']}")
            print(f"Agents created: {result['agents_created']}")
            if result['errors']:
                print(f"Errors: {result['errors']}")
            break
        elif status["status"] == "failed":
            print(f"\n❌ Campaign failed: {status.get('error')}")
            break
    
    # Get all voice agents
    print("\n📋 Fetching voice agents...")
    agents_response = requests.get(f"{BASE_URL}/api/voice-agents")
    if agents_response.status_code == 200:
        agents = agents_response.json()
        print(f"Total agents: {len(agents)}")
        for agent in agents[:3]:
            print(f"  - {agent['name']} (ID: {agent['vapi_assistant_id']})")

if __name__ == "__main__":
    test_complete_workflow()
    print("\n✅ Day 2 testing complete!")
```

**Add missing endpoint:**

```python
# Add to main.py
@app.get("/api/voice-agents")
def get_voice_agents(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all voice agents"""
    agents = db.query(VoiceAgent).offset(skip).limit(limit).all()
    return agents
```

---

## 🎯 DAY 2 SUCCESS CRITERIA

**Must Be Completed:**
- ✅ Prompt generator creates industry-specific prompts
- ✅ VAPI integration creates voice agents
- ✅ Complete workflow: scrape → analyze → generate → create
- ✅ Background task processing working
- ✅ Can process 3+ jobs end-to-end
- ✅ At least 1 voice agent created successfully

---

**Day 2 Complete! Tomorrow: Frontend Dashboard 🎨**

