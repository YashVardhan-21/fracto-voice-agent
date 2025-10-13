# FRACTO Voice Agent System - Quick Start Guide
## Get Running in 15 Minutes

---

## ⚡ FASTEST PATH TO RUNNING SYSTEM

### Step 1: Prerequisites (2 minutes)

**Check your system:**
```bash
# Windows PowerShell
python --version    # Need 3.9+
node --version      # Need 18+
```

**If missing:**
- Python: https://www.python.org/downloads/
- Node.js: https://nodejs.org/

---

### Step 2: Get API Keys (5 minutes)

#### OpenAI API Key
1. Go to: https://platform.openai.com/api-keys
2. Sign up / Log in
3. Click "Create new secret key"
4. Copy key: `sk-...`
5. Add $10 credit: https://platform.openai.com/account/billing

#### VAPI API Key
1. Go to: https://vapi.ai
2. Sign up (free trial available)
3. Dashboard → API Keys
4. Copy your API key
5. Note: Some test credits included

#### ScraperAPI (Optional - for production scraping)
1. Go to: https://www.scraperapi.com
2. Sign up (free tier: 5K requests/month)
3. Copy API key
4. Note: Can skip for MVP (uses mock data)

---

### Step 3: Setup Backend (4 minutes)

```bash
# Navigate to project
cd C:\Users\hp\Downloads\FRACTO_Voice_Agent_System_Complete\backend

# Create virtual environment
python -m venv venv

# Activate (Windows PowerShell)
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install fastapi uvicorn sqlalchemy pydantic httpx beautifulsoup4 python-dotenv openai requests

# Create .env file
@"
OPENAI_API_KEY=sk-your-key-here
VAPI_API_KEY=your-vapi-key-here
SCRAPER_API_KEY=your-scraper-key-here
DATABASE_URL=sqlite:///./fracto.db
DEBUG=true
"@ | Out-File -FilePath .env -Encoding utf8

# IMPORTANT: Replace "your-key-here" with actual keys!
```

**Edit .env file and add your real API keys!**

---

### Step 4: Initialize Database (1 minute)

```bash
# Still in backend directory with venv activated
python -c "from app.database import init_db; init_db()"

# You should see: ✅ Database initialized successfully
```

---

### Step 5: Start Backend (1 minute)

```bash
# Start FastAPI server
uvicorn app.main:app --reload

# You should see:
# INFO:     Uvicorn running on http://127.0.0.1:8000
# INFO:     Application startup complete
```

**Leave this terminal running!**

Open browser: http://localhost:8000/docs  
You should see Swagger API documentation.

---

### Step 6: Setup Frontend (2 minutes)

**Open a NEW terminal (keep backend running):**

```bash
# Navigate to frontend
cd C:\Users\hp\Downloads\FRACTO_Voice_Agent_System_Complete\frontend

# Install dependencies
npm install

# Create .env file
@"
VITE_API_URL=http://localhost:8000
"@ | Out-File -FilePath .env -Encoding utf8

# Start development server
npm run dev

# You should see:
# VITE v5.x.x  ready in XXX ms
# ➜  Local:   http://localhost:5173/
```

**Open browser: http://localhost:5173**

---

## 🎉 YOU'RE RUNNING!

You should now see:
- **Backend API:** http://localhost:8000/docs (Swagger UI)
- **Frontend Dashboard:** http://localhost:5173 (React app)

---

## 🧪 TEST THE SYSTEM (5 minutes)

### Test 1: Backend API via Swagger

1. Go to: http://localhost:8000/docs
2. Find `POST /api/scrape-jobs`
3. Click "Try it out"
4. Paste this JSON:
```json
{
  "query": "dental office manager",
  "location": "New York",
  "limit": 3
}
```
5. Click "Execute"
6. Should see: 3 jobs returned (mock data if ScraperAPI not configured)

### Test 2: Website Analysis

1. Still in Swagger UI
2. Find `POST /api/analyze-website`
3. Click "Try it out"
4. Paste this JSON:
```json
{
  "url": "https://www.aspendental.com",
  "company_name": "Aspen Dental"
}
```
5. Click "Execute"
6. Should see: Business type, services, confidence score

### Test 3: Frontend Campaign

1. Go to: http://localhost:5173
2. Click "Campaigns" in sidebar
3. Fill form:
   - **Campaign Name:** "Test Campaign"
   - **Job Search Query:** "dental office manager"
   - **Location:** "New York"
   - **Number of Jobs:** 3
4. Click "Start Campaign"
5. Watch real-time status updates
6. After ~2 minutes, click "Dashboard"
7. Should see: Stats updated, voice agents created

---

## 🐛 TROUBLESHOOTING

### Backend Won't Start

**Error: `ModuleNotFoundError: No module named 'app'`**
```bash
# Make sure you're in the backend directory
cd backend

# Check PYTHONPATH
$env:PYTHONPATH = "."

# Try again
uvicorn app.main:app --reload
```

**Error: `Database not found`**
```bash
# Reinitialize database
python -c "from app.database import init_db; init_db()"
```

**Error: `OpenAI API key not found`**
```bash
# Check .env file exists and has keys
cat .env

# Make sure no spaces around = sign
# Correct: OPENAI_API_KEY=sk-...
# Wrong: OPENAI_API_KEY = sk-...
```

---

### Frontend Won't Start

**Error: `Cannot connect to backend`**
```bash
# Check backend is running on port 8000
# Open http://localhost:8000 in browser

# Check .env in frontend directory
cat .env
# Should have: VITE_API_URL=http://localhost:8000

# Restart frontend
npm run dev
```

**Error: `npm install fails`**
```bash
# Clear npm cache
npm cache clean --force

# Delete node_modules
rm -rf node_modules package-lock.json

# Reinstall
npm install
```

---

### API Calls Failing

**Error: `OpenAI API error 401`**
- Invalid API key
- Check: https://platform.openai.com/api-keys
- Regenerate key if needed

**Error: `OpenAI API error 429`**
- Rate limit exceeded
- Add billing: https://platform.openai.com/account/billing
- Wait a few minutes and try again

**Error: `VAPI API error`**
- Check VAPI dashboard: https://vapi.ai
- Verify API key is correct
- Check if trial credits remain

---

### Database Issues

**Error: `Database locked`**
```bash
# Close any DB browser tools
# Stop backend server (Ctrl+C)
# Delete database
rm fracto.db

# Reinitialize
python -c "from app.database import init_db; init_db()"

# Restart backend
uvicorn app.main:app --reload
```

---

## 📁 PROJECT STRUCTURE

```
FRACTO_Voice_Agent_System_Complete/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app
│   │   ├── models.py            # Database models
│   │   ├── database.py          # DB connection
│   │   ├── core/
│   │   │   └── workflow.py      # Orchestrator
│   │   ├── scrapers/
│   │   │   └── job_scraper.py   # Job scraping
│   │   ├── analyzers/
│   │   │   └── website_analyzer.py  # Website analysis
│   │   ├── generators/
│   │   │   └── prompt_generator.py  # Prompt creation
│   │   └── integrations/
│   │       └── vapi_client.py   # VAPI integration
│   ├── requirements.txt
│   ├── .env                     # API keys (YOU CREATE THIS)
│   └── fracto.db               # SQLite database (auto-created)
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx             # Main app
│   │   ├── components/
│   │   │   └── Layout.jsx      # Layout component
│   │   ├── pages/
│   │   │   ├── Dashboard.jsx   # Dashboard page
│   │   │   ├── Campaigns.jsx   # Campaign creation
│   │   │   ├── Companies.jsx   # Companies list
│   │   │   └── VoiceAgents.jsx # Voice agents list
│   │   └── services/
│   │       └── api.js          # API client
│   ├── package.json
│   └── .env                    # API URL (YOU CREATE THIS)
│
├── RAPID_EXECUTION_PLAN.md     # Detailed build plan
├── DAY_1_TASKS.md              # Day 1 implementation
├── DAY_2_TASKS.md              # Day 2 implementation
├── DAY_3_TASKS.md              # Day 3 implementation
├── MCP_INTEGRATION_GUIDE.md    # MCP acceleration guide
└── EXECUTIVE_SUMMARY.md        # Overview & strategy
```

---

## 🎯 NEXT STEPS

### If Everything Works:
1. ✅ Read `EXECUTIVE_SUMMARY.md` for overview
2. ✅ Follow `DAY_1_TASKS.md` to build backend modules
3. ✅ Continue with `DAY_2_TASKS.md` for AI integration
4. ✅ Finish with `DAY_3_TASKS.md` for frontend
5. ✅ Deploy with Docker instructions

### If You Want to Accelerate:
1. Read `MCP_INTEGRATION_GUIDE.md`
2. Enable GitHub, Puppeteer, and Sequential Thinking MCPs
3. Reduce build time by 60%

### If You Want to Customize:
1. Add more business types in `prompt_generator.py`
2. Customize UI colors in `tailwind.config.js`
3. Add more scrapers in `job_scraper.py`
4. Integrate more LLM providers (Gemini, Claude)

---

## 🚦 STATUS CHECKLIST

After setup, verify these are ✅:

### Backend
- [ ] Virtual environment activated
- [ ] Dependencies installed
- [ ] .env file created with API keys
- [ ] Database initialized
- [ ] Server running on port 8000
- [ ] Swagger UI accessible at /docs

### Frontend
- [ ] Dependencies installed
- [ ] .env file created
- [ ] Dev server running on port 5173
- [ ] Can navigate between pages
- [ ] Can connect to backend API

### APIs
- [ ] OpenAI API key valid (test in Swagger)
- [ ] VAPI API key valid
- [ ] ScraperAPI key valid (optional)

### Testing
- [ ] Can scrape jobs (even mock data)
- [ ] Can analyze website
- [ ] Can create campaign
- [ ] Dashboard shows data

---

## 💡 PRO TIPS

1. **Start Small**
   - Test with 3-5 jobs first
   - Verify each component works
   - Scale up gradually

2. **Use Mock Data**
   - Don't worry if ScraperAPI fails
   - System has built-in mock data
   - Focus on workflow, not scraping

3. **Monitor Costs**
   - OpenAI GPT-4o-mini is cheap (~$0.005/call)
   - VAPI charges per minute
   - Start with small campaigns

4. **Check Logs**
   - Backend: Watch terminal for errors
   - Frontend: Check browser console (F12)
   - API: Use Swagger UI for testing

5. **Iterate Quickly**
   - Don't perfect each component
   - Get end-to-end working first
   - Refine based on results

---

## 📞 GETTING HELP

### Documentation
- Read detailed guides in repository
- Check API documentation in Swagger UI
- Review example code in task files

### Common Resources
- OpenAI Docs: https://platform.openai.com/docs
- VAPI Docs: https://docs.vapi.ai
- FastAPI Docs: https://fastapi.tiangolo.com
- React Docs: https://react.dev

### Debug Mode
```bash
# Backend verbose logging
uvicorn app.main:app --reload --log-level debug

# Frontend dev tools
# Open browser, press F12, check Console tab
```

---

## 🎊 SUCCESS!

If you've completed this guide, you should have:

✅ Backend API running and responding  
✅ Frontend dashboard displaying  
✅ Can create campaigns  
✅ Voice agents being created  
✅ Real-time status updates working  

**You're ready to build the full system!**

**Next:** Read `RAPID_EXECUTION_PLAN.md` and start with `DAY_1_TASKS.md`

---

**Happy building! 🚀**

*Last updated: October 2025*

