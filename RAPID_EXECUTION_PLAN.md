# FRACTO VOICE AGENT - RAPID 2-3 DAY EXECUTION PLAN
## MVP Implementation Strategy

---

## 🎯 WHAT YOU'RE BUILDING

**FRACTO Voice Agent Outreach Automation** - An AI system that:
1. Scrapes job postings → 2. Analyzes company websites → 3. Generates custom voice agent demos → 4. Automates outreach → 5. Tracks conversions

**From 8-12 weeks to 2-3 days by:** Cutting enterprise features, using pre-built APIs, focusing on core workflow only.

---

## 📋 MVP FEATURE SCOPE (2-3 Days)

### ✅ INCLUDED (Must-Have)
- Basic job scraping (Indeed API or simple scraper)
- Website analysis (OpenAI GPT-4 for extraction)
- VAPI voice agent creation API integration
- Simple dashboard (React + FastAPI)
- Basic outreach tracking (CSV/SQLite)

### ❌ EXCLUDED (Future Phases)
- Multi-platform scraping (LinkedIn, Glassdoor)
- Advanced analytics/predictions
- Compliance frameworks (TCPA, HIPAA)
- Crisis prediction system
- A/B testing framework
- Email automation (focus on demo creation only)

---

## 🔧 RECOMMENDED MCP SETUP

### Enable These MCPs in Cursor:

#### 1. **GitHub MCP** (Essential)
```bash
# For version control and collaboration
npm install -g @modelcontextprotocol/server-github
```

#### 2. **PostgreSQL MCP** (Database)
```bash
# For database operations
npm install -g @modelcontextprotocol/server-postgres
```

#### 3. **Puppeteer MCP** (Web Scraping)
```bash
# For job scraping and website analysis
npm install -g @modelcontextprotocol/server-puppeteer
```

#### 4. **Filesystem MCP** (File Operations)
```bash
# Already enabled by default in Cursor
```

#### 5. **Sequential Thinking MCP** (Planning)
```bash
# For complex decision-making
npm install -g @modelcontextprotocol/server-sequential-thinking
```

### MCP Configuration (.cursor/mcp.json)
```json
{
  "mcps": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_TOKEN": "your_github_token"
      }
    },
    "postgres": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-postgres"],
      "env": {
        "DATABASE_URL": "postgresql://user:pass@localhost:5432/fracto"
      }
    },
    "puppeteer": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-puppeteer"]
    }
  }
}
```

---

## 📅 DAY-BY-DAY EXECUTION PLAN

### **DAY 1: Backend Core + Job Scraping (8-10 hours)**

#### Morning (4 hours)
**Task 1.1:** Setup Project Structure
- [ ] Initialize Git repo
- [ ] Create backend FastAPI structure
- [ ] Setup virtual environment
- [ ] Install dependencies (FastAPI, SQLAlchemy, httpx, beautifulsoup4, openai)
- [ ] Configure environment variables

**Task 1.2:** Database Schema
- [ ] Create SQLite/PostgreSQL database
- [ ] Define models: Jobs, Companies, VoiceAgents, Campaigns
- [ ] Setup Alembic migrations
- [ ] Create seed data

#### Afternoon (4 hours)
**Task 1.3:** Job Scraping Module
- [ ] Implement Indeed scraper (use SerpAPI or ScraperAPI for speed)
- [ ] Parse job data (title, company, website, location)
- [ ] Validate and clean data
- [ ] Store in database
- [ ] Create API endpoint: POST /api/scrape-jobs

**Task 1.4:** Website Analysis Module
- [ ] Create website scraper (httpx + BeautifulSoup)
- [ ] Extract: business type, services, contact info
- [ ] Integrate OpenAI GPT-4 for business classification
- [ ] Create API endpoint: POST /api/analyze-website

**Evening (2 hours)**
**Task 1.5:** Testing & Debugging
- [ ] Test job scraping with 10 sample jobs
- [ ] Test website analysis on 5 sites
- [ ] Fix errors and edge cases

---

### **DAY 2: LLM Integration + VAPI Voice Agents (8-10 hours)**

#### Morning (4 hours)
**Task 2.1:** LLM Prompt Generation
- [ ] Create prompt templates for different business types
- [ ] Implement prompt generation logic
- [ ] Integrate Gemini API (free tier) as primary
- [ ] Add Deepseek as fallback
- [ ] Create API endpoint: POST /api/generate-prompt

**Task 2.2:** VAPI Integration
- [ ] Setup VAPI account and API keys
- [ ] Implement voice agent creation endpoint
- [ ] Test voice customization options
- [ ] Store agent IDs in database
- [ ] Create API endpoint: POST /api/create-voice-agent

#### Afternoon (4 hours)
**Task 2.3:** Complete Workflow Orchestration
- [ ] Create master endpoint: POST /api/process-campaign
- [ ] Flow: Scrape → Analyze → Generate Prompt → Create Agent
- [ ] Add error handling and retries
- [ ] Implement logging for debugging
- [ ] Add progress tracking

**Task 2.4:** Background Task Processing
- [ ] Setup Celery + Redis OR simple task queue
- [ ] Make campaign processing async
- [ ] Add job status tracking
- [ ] Create webhook for completion notifications

**Evening (2 hours)**
**Task 2.5:** API Documentation
- [ ] Enable FastAPI auto-docs (Swagger)
- [ ] Test all endpoints in Swagger UI
- [ ] Create Postman collection

---

### **DAY 3: Frontend Dashboard + Integration (8-10 hours)**

#### Morning (4 hours)
**Task 3.1:** Frontend Setup
- [ ] Initialize React app (Vite for speed)
- [ ] Install dependencies (TailwindCSS, Axios, React Query)
- [ ] Create basic layout (header, sidebar, main)
- [ ] Setup API client service

**Task 3.2:** Core UI Components
- [ ] Campaign creation form (paste job URL or search criteria)
- [ ] Job list view with status indicators
- [ ] Company details view
- [ ] Voice agent preview player
- [ ] Campaign results dashboard

#### Afternoon (4 hours)
**Task 3.3:** Feature Implementation
- [ ] Connect forms to backend APIs
- [ ] Implement real-time status updates
- [ ] Add voice agent testing interface
- [ ] Create simple analytics (success rate, avg response time)
- [ ] Add export functionality (CSV download)

**Task 3.4:** Integration Testing
- [ ] End-to-end workflow test
- [ ] Test error scenarios
- [ ] Performance optimization
- [ ] Cross-browser testing

**Evening (2 hours)**
**Task 3.5:** Deployment & Documentation
- [ ] Create Docker containers (backend, frontend, db)
- [ ] Setup docker-compose for local deployment
- [ ] Write README with setup instructions
- [ ] Create demo video/screenshots
- [ ] Deploy to cloud (Railway, Render, or Vercel)

---

## 🤖 BACKGROUND AGENT TASKS

### Agent 1: Continuous Data Quality Monitor
**Role:** Monitor scraped data quality in background
**Tasks:**
- Check for missing websites (alert if >20%)
- Validate phone numbers and emails
- Flag low-confidence business classifications
- Run every 30 minutes

### Agent 2: Voice Agent Quality Checker
**Role:** Test voice agents after creation
**Tasks:**
- Make test call to each new agent
- Transcribe and analyze responses
- Score agent performance (1-10)
- Flag poorly performing agents
- Run after each agent creation

### Agent 3: Cost Monitor
**Role:** Track API costs and usage
**Tasks:**
- Monitor OpenAI/Gemini API usage
- Track VAPI call costs
- Alert when approaching budget limits
- Generate daily cost reports
- Run every hour

### Agent 4: Backup & Recovery
**Role:** Ensure data safety
**Tasks:**
- Backup database every 6 hours
- Archive completed campaigns
- Monitor disk space
- Clean up temporary files

---

## 🛠️ SIMPLIFIED TECH STACK

### Backend
- **Framework:** FastAPI (fast to build)
- **Database:** SQLite (no setup) → PostgreSQL (production)
- **Task Queue:** Python `threading` (simple) → Celery (production)
- **LLM:** OpenAI GPT-4o-mini (cheap + fast)
- **Scraping:** ScraperAPI (paid but reliable) OR httpx + BeautifulSoup

### Frontend
- **Framework:** React + Vite (fast builds)
- **UI:** TailwindCSS + shadcn/ui (pre-built components)
- **State:** React Query (easy API management)
- **Charts:** Recharts (simple analytics)

### Infrastructure
- **Hosting:** Railway.app (easy deployment)
- **Database:** Railway PostgreSQL
- **Redis:** Railway Redis
- **Storage:** Local filesystem → S3 (future)

---

## 🚨 CRITICAL SUCCESS FACTORS

### Day 1 Checkpoint
✅ Can scrape 10 jobs and get company websites
✅ Can analyze a website and extract business info
✅ All data stored in database

### Day 2 Checkpoint
✅ Can generate custom prompts for 3+ business types
✅ Can create a VAPI voice agent via API
✅ Complete workflow works end-to-end for 1 job

### Day 3 Checkpoint
✅ UI displays all campaigns and results
✅ Can start a new campaign from UI
✅ Can test voice agents from UI
✅ System deployed and accessible via URL

---

## 📞 API SERVICES TO USE (Pre-built Solutions)

### 1. **ScraperAPI** (Job Scraping)
- Cost: $49/month (1M credits)
- Handles rate limits, proxies, captchas
- ```python
  response = requests.get('http://api.scraperapi.com', params={
      'api_key': 'YOUR_KEY',
      'url': 'https://indeed.com/jobs?q=dentist'
  })
  ```

### 2. **VAPI** (Voice Agents)
- Cost: Pay per call (~$0.10/min)
- API: https://docs.vapi.ai
- ```python
  vapi.assistant.create({
      'name': 'Dental Office Assistant',
      'voice': 'jennifer',
      'prompt': generated_prompt
  })
  ```

### 3. **Google Gemini** (Primary LLM - FREE)
- Cost: $0 (free tier: 15 requests/minute, 1M tokens/day)
- Use for: Website analysis, prompt generation
- Fallback: Deepseek (free 100 req/day)

### 4. **Deepseek** (Secondary LLM - FREE)
- Cost: $0 (free tier: 100 requests/day)
- Use for: Prompt enhancement, complex analysis
- Fallback: Local templates

### 5. **Perplexity API** (Research - Your $5 Credit)
- Cost: Your $5 monthly credit
- Use for: Advanced website research, high-value analysis
- Fallback: Gemini

---

## 💰 ESTIMATED COSTS (FREE MVP!)

| Service | Cost | Usage |
|---------|------|-------|
| Google Gemini | $0 | 15 requests/minute (free tier) |
| Deepseek | $0 | 100 requests/day (free tier) |
| Perplexity API | $0 | Your $5 monthly credit |
| VAPI | $0 | Free trial |
| Free Scraping | $0 | httpx + BeautifulSoup |
| SQLite Database | $0 | Built-in |
| Local Development | $0 | Your computer |
| **TOTAL** | **$0** | Completely FREE! |

**Optional Production Costs:**
- Railway Hosting: $5/month (free tier available)
- VAPI Production: $0.10/minute (only when making actual calls)
- **Total Production:** $5-20/month (vs $139+ original plan)

---

## 🎯 MVP FEATURE BREAKDOWN

### Core Features (Must Build)
1. **Job Input** → Manual paste URL or search term
2. **Website Scraper** → Extract company info
3. **Business Analyzer** → GPT-4 classification
4. **Prompt Generator** → Custom templates per industry
5. **VAPI Integration** → Create voice agent
6. **Results Dashboard** → View created agents

### Nice-to-Have (If Time Permits)
- Bulk job import (CSV)
- Email notifications
- Voice agent analytics
- Campaign comparison
- Export reports

### Future Versions
- LinkedIn scraping
- Email outreach automation
- Advanced analytics
- Multi-user support
- White-label options

---

## 📚 DEVELOPMENT WORKFLOW WITH MCPs

### Using GitHub MCP
```bash
# Automatic commits after each major feature
# MCP will handle: git add, commit, push
# You just code, MCP handles version control
```

### Using Puppeteer MCP
```bash
# For web scraping tasks
# MCP handles browser automation
# You provide URLs, MCP returns structured data
```

### Using Postgres MCP
```bash
# For database operations
# MCP handles migrations, queries
# You define schema, MCP executes
```

---

## 🚀 QUICK START COMMANDS

### Backend Setup (5 minutes)
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install fastapi uvicorn sqlalchemy openai httpx beautifulsoup4 python-dotenv
uvicorn app.main:app --reload
```

### Frontend Setup (5 minutes)
```bash
cd frontend
npm create vite@latest . -- --template react
npm install
npm install -D tailwindcss axios @tanstack/react-query
npm run dev
```

### Environment Variables (.env)
```env
# LLM APIs
OPENAI_API_KEY=sk-...
GEMINI_API_KEY=...
DEEPSEEK_API_KEY=...

# Voice Agent
VAPI_API_KEY=...

# Scraping
SCRAPER_API_KEY=...

# Database
DATABASE_URL=sqlite:///./fracto.db

# App Config
DEBUG=true
LOG_LEVEL=info
```

---

## 🎬 DEMONSTRATION SCRIPT

**For Investors/Clients (5-minute demo):**

1. **Show Problem (30 sec)**
   - "Manual outreach takes 2 hours per prospect"
   - "Generic demos have 10% conversion rate"

2. **Paste Job URL (30 sec)**
   - Copy Indeed job posting URL
   - Paste into dashboard
   - Click "Create Campaign"

3. **Show Processing (1 min)**
   - Real-time status updates
   - "Analyzing website..."
   - "Generating custom prompt..."
   - "Creating voice agent..."

4. **Test Voice Agent (2 min)**
   - Click "Test Agent"
   - Make demo call
   - Show personalized response

5. **Show Results (1 min)**
   - Campaign dashboard
   - Efficiency metrics: "90% time saved"
   - Cost analysis: "$2 per demo vs $20 manual"

6. **Close (30 sec)**
   - "From 2 hours to 2 minutes"
   - "Personalized demos = 70% conversion"
   - "Scale to 1000 campaigns/month"

---

## 🔒 SECURITY & COMPLIANCE (Minimal MVP)

### Must-Have
- [ ] API keys in .env (not committed)
- [ ] Input validation on all endpoints
- [ ] Rate limiting (10 req/min per IP)
- [ ] HTTPS in production

### Future Versions
- TCPA compliance checking
- HIPAA compliance for medical
- GDPR compliance
- Audit logging

---

## 📈 SUCCESS METRICS

### Technical Metrics
- [ ] System processes 10 jobs in <5 minutes
- [ ] 95%+ uptime
- [ ] <2 second API response time
- [ ] Zero critical bugs in demo

### Business Metrics
- [ ] Demo creation time: <3 minutes (vs 2 hours manual)
- [ ] Cost per demo: <$2 (vs $20 manual)
- [ ] Voice agent quality: 8+/10 rating
- [ ] Stakeholder approval: "Demo-ready"

---

## 🆘 TROUBLESHOOTING

### Common Issues

**Job scraping fails:**
- Check ScraperAPI credits
- Verify URL format
- Test with direct requests library

**Website analysis returns low confidence:**
- Website may be JavaScript-heavy (need Puppeteer)
- No clear business info on homepage
- Try /about or /services pages

**VAPI agent sounds generic:**
- Improve prompt with more company details
- Test different voice options
- Add example conversations to prompt

**Frontend won't connect to backend:**
- Check CORS settings in FastAPI
- Verify backend is running (http://localhost:8000/docs)
- Check API URLs in frontend config

---

## 📦 DELIVERABLES CHECKLIST

### Code
- [ ] Backend API (FastAPI)
- [ ] Frontend Dashboard (React)
- [ ] Database schema & migrations
- [ ] Docker configuration
- [ ] Environment setup scripts

### Documentation
- [ ] README.md with setup instructions
- [ ] API documentation (Swagger)
- [ ] Architecture diagram
- [ ] Demo script
- [ ] Troubleshooting guide

### Demo Materials
- [ ] Live deployed application
- [ ] Sample campaigns (3-5 examples)
- [ ] Demo video (5 minutes)
- [ ] Screenshots of key features
- [ ] Investor pitch deck

---

## 🎯 NEXT STEPS AFTER MVP

### Week 2-4 (Post-MVP)
- [ ] Add email outreach automation
- [ ] LinkedIn scraping integration
- [ ] Advanced analytics dashboard
- [ ] Multi-user support
- [ ] Campaign templates

### Month 2-3
- [ ] A/B testing framework
- [ ] Performance prediction
- [ ] Compliance frameworks
- [ ] White-label version
- [ ] API for customers

### Month 4-6
- [ ] Enterprise features
- [ ] Crisis prediction
- [ ] Advanced AI models
- [ ] Market expansion
- [ ] Revenue optimization

---

## 💡 PRO TIPS

1. **Start with manual data** - Don't perfect the scraper, use 10 manual examples
2. **Use GPT-4 for everything** - Classification, extraction, generation
3. **Test VAPI first** - Ensure voice agents work before building automation
4. **Deploy early** - Get URL on Day 2, test from real environment
5. **Record everything** - Screen record your workflow for demo video
6. **Keep it simple** - SQLite + single server is fine for MVP
7. **Focus on demo** - Build features that demo well, skip invisible ones
8. **Use templates** - Copy-paste UI components, don't build from scratch
9. **API-first** - Build backend endpoints before frontend
10. **Ship on Day 3** - Even if imperfect, deploy and iterate

---

## 🎉 FINAL CHECKLIST

**Before Calling It Done:**
- [ ] Can create a voice agent from a job URL in <3 minutes
- [ ] Voice agent is personalized to the company
- [ ] Dashboard shows all campaigns and results
- [ ] System is deployed and accessible online
- [ ] Demo video is recorded
- [ ] README has clear setup instructions
- [ ] At least 3 successful test campaigns
- [ ] Stakeholders have reviewed and approved
- [ ] Cost per demo is <$5
- [ ] Ready to show investors/clients

---

**Remember:** Done is better than perfect. Ship the MVP in 3 days, then iterate based on feedback.

**Questions or Stuck?** Document the issue, move to next feature, come back later.

**Good luck! 🚀**

