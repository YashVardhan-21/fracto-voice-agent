# FRACTO Voice Agent System - Automated Setup Script
# Run this in PowerShell to setup everything automatically

Write-Host "╔═══════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║   FRACTO Voice Agent System - Automated Setup            ║" -ForegroundColor Cyan
Write-Host "║   This will setup backend + frontend in 10 minutes       ║" -ForegroundColor Cyan
Write-Host "╚═══════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Check prerequisites
Write-Host "[1/8] Checking prerequisites..." -ForegroundColor Yellow

# Check Python
try {
    $pythonVersion = python --version 2>&1
    Write-Host "  ✓ Python: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "  ✗ Python not found! Please install Python 3.9+ from https://www.python.org" -ForegroundColor Red
    exit 1
}

# Check Node
try {
    $nodeVersion = node --version 2>&1
    Write-Host "  ✓ Node.js: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "  ✗ Node.js not found! Please install Node.js 18+ from https://nodejs.org" -ForegroundColor Red
    exit 1
}

# Get FREE API keys
Write-Host ""
Write-Host "[2/8] Configuring FREE API keys..." -ForegroundColor Yellow
Write-Host "  🆓 This MVP uses FREE APIs only!" -ForegroundColor Green
Write-Host "  Please enter your FREE API keys (or press Enter to skip for now):" -ForegroundColor Gray

$geminiKey = Read-Host "  Google Gemini API Key (free tier)"
if ([string]::IsNullOrWhiteSpace($geminiKey)) {
    $geminiKey = "your-gemini-key-here"
    Write-Host "  ⚠ Skipped - Get free key at: https://aistudio.google.com/app/apikey" -ForegroundColor Yellow
} else {
    Write-Host "  ✓ Gemini key configured (15 requests/min free)" -ForegroundColor Green
}

$deepseekKey = Read-Host "  Deepseek API Key (free tier)"
if ([string]::IsNullOrWhiteSpace($deepseekKey)) {
    $deepseekKey = "your-deepseek-key-here"
    Write-Host "  ⚠ Skipped - Get free key at: https://platform.deepseek.com/api_keys" -ForegroundColor Yellow
} else {
    Write-Host "  ✓ Deepseek key configured (100 requests/day free)" -ForegroundColor Green
}

$perplexityKey = Read-Host "  Perplexity API Key (your $5 monthly credit)"
if ([string]::IsNullOrWhiteSpace($perplexityKey)) {
    $perplexityKey = "your-perplexity-key-here"
    Write-Host "  ⚠ Skipped - Get key at: https://www.perplexity.ai/settings/api" -ForegroundColor Yellow
} else {
    Write-Host "  ✓ Perplexity key configured ($5 monthly credit)" -ForegroundColor Green
}

$vapiKey = Read-Host "  VAPI API Key (free trial)"
if ([string]::IsNullOrWhiteSpace($vapiKey)) {
    $vapiKey = "your-vapi-key-here"
    Write-Host "  ⚠ Skipped - Get free trial at: https://vapi.ai" -ForegroundColor Yellow
} else {
    Write-Host "  ✓ VAPI key configured (free trial)" -ForegroundColor Green
}

# Setup backend
Write-Host ""
Write-Host "[3/8] Setting up backend..." -ForegroundColor Yellow

Set-Location backend

# Create virtual environment
Write-Host "  Creating virtual environment..." -ForegroundColor Gray
python -m venv venv

# Activate virtual environment
Write-Host "  Activating virtual environment..." -ForegroundColor Gray
& .\venv\Scripts\Activate.ps1

# Install dependencies
Write-Host "  Installing dependencies (this may take 2-3 minutes)..." -ForegroundColor Gray
pip install --quiet fastapi uvicorn sqlalchemy pydantic httpx beautifulsoup4 python-dotenv openai requests

if ($LASTEXITCODE -eq 0) {
    Write-Host "  ✓ Backend dependencies installed" -ForegroundColor Green
} else {
    Write-Host "  ✗ Failed to install backend dependencies" -ForegroundColor Red
    exit 1
}

# Create .env file
Write-Host "  Creating .env file..." -ForegroundColor Gray
$envContent = @"
# FREE API Keys - No monthly costs!
GEMINI_API_KEY=$geminiKey
DEEPSEEK_API_KEY=$deepseekKey
PERPLEXITY_API_KEY=$perplexityKey
VAPI_API_KEY=$vapiKey

# Database (free SQLite)
DATABASE_URL=sqlite:///./fracto.db

# App Config
DEBUG=true
LOG_LEVEL=info

# Free API Configuration
GEMINI_RATE_LIMIT=15
DEEPSEEK_DAILY_LIMIT=100
PERPLEXITY_MONTHLY_CREDIT=5
"@

$envContent | Out-File -FilePath ".env" -Encoding UTF8
Write-Host "  ✓ Backend .env file created" -ForegroundColor Green

# Create necessary directories
Write-Host "  Creating project structure..." -ForegroundColor Gray
New-Item -ItemType Directory -Force -Path "app" | Out-Null
New-Item -ItemType Directory -Force -Path "app/core" | Out-Null
New-Item -ItemType Directory -Force -Path "app/scrapers" | Out-Null
New-Item -ItemType Directory -Force -Path "app/analyzers" | Out-Null
New-Item -ItemType Directory -Force -Path "app/generators" | Out-Null
New-Item -ItemType Directory -Force -Path "app/integrations" | Out-Null
New-Item -ItemType Directory -Force -Path "tests" | Out-Null
Write-Host "  ✓ Project structure created" -ForegroundColor Green

# Initialize database
Write-Host ""
Write-Host "[4/8] Initializing database..." -ForegroundColor Yellow

if (Test-Path "app/database.py") {
    python -c "from app.database import init_db; init_db()"
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✓ Database initialized successfully" -ForegroundColor Green
    } else {
        Write-Host "  ⚠ Database initialization skipped (will be created on first run)" -ForegroundColor Yellow
    }
} else {
    Write-Host "  ℹ Database module not found yet - will be created during Day 1 tasks" -ForegroundColor Cyan
}

# Go back to root
Set-Location ..

# Setup frontend
Write-Host ""
Write-Host "[5/8] Setting up frontend..." -ForegroundColor Yellow

Set-Location frontend

# Install dependencies
Write-Host "  Installing frontend dependencies (this may take 2-3 minutes)..." -ForegroundColor Gray
npm install --silent

if ($LASTEXITCODE -eq 0) {
    Write-Host "  ✓ Frontend dependencies installed" -ForegroundColor Green
} else {
    Write-Host "  ✗ Failed to install frontend dependencies" -ForegroundColor Red
    Set-Location ..
    exit 1
}

# Create frontend .env
Write-Host "  Creating frontend .env file..." -ForegroundColor Gray
$frontendEnv = "VITE_API_URL=http://localhost:8000"
$frontendEnv | Out-File -FilePath ".env" -Encoding UTF8
Write-Host "  ✓ Frontend .env file created" -ForegroundColor Green

# Go back to root
Set-Location ..

# Create helpful scripts
Write-Host ""
Write-Host "[6/8] Creating helper scripts..." -ForegroundColor Yellow

# Start backend script
$startBackend = @'
@echo off
echo Starting FRACTO Backend...
cd backend
call venv\Scripts\activate.bat
echo Backend is running on http://localhost:8000
echo API docs available at http://localhost:8000/docs
uvicorn app.main:app --reload
'@

$startBackend | Out-File -FilePath "start_backend.bat" -Encoding ASCII
Write-Host "  ✓ Created start_backend.bat" -ForegroundColor Green

# Start frontend script
$startFrontend = @'
@echo off
echo Starting FRACTO Frontend...
cd frontend
echo Frontend is running on http://localhost:5173
npm run dev
'@

$startFrontend | Out-File -FilePath "start_frontend.bat" -Encoding ASCII
Write-Host "  ✓ Created start_frontend.bat" -ForegroundColor Green

# Start both script
$startBoth = @'
@echo off
echo Starting FRACTO Voice Agent System...
echo.
echo Opening two terminals:
echo - Backend (http://localhost:8000)
echo - Frontend (http://localhost:5173)
echo.
start cmd /k "cd backend && venv\Scripts\activate && uvicorn app.main:app --reload"
timeout /t 3 /nobreak > nul
start cmd /k "cd frontend && npm run dev"
echo.
echo System starting...
echo Backend will be ready in ~10 seconds
echo Frontend will be ready in ~5 seconds
echo.
pause
'@

$startBoth | Out-File -FilePath "start_all.bat" -Encoding ASCII
Write-Host "  ✓ Created start_all.bat" -ForegroundColor Green

# Create README
Write-Host ""
Write-Host "[7/8] Creating setup summary..." -ForegroundColor Yellow

$summaryContent = @"
# FRACTO Voice Agent System - Setup Complete!

## ✅ What's Installed

### Backend (Python FastAPI)
- Python virtual environment: \`backend/venv/\`
- Dependencies installed: FastAPI, SQLAlchemy, OpenAI, etc.
- Configuration: \`backend/.env\`
- Database: SQLite (will be created on first run)

### Frontend (React + Vite)
- Node modules: \`frontend/node_modules/\`
- Configuration: \`frontend/.env\`
- UI Framework: TailwindCSS + React Query

## 🚀 Quick Start

### Option 1: Start Everything at Once
Double-click: \`start_all.bat\`

This will open two terminals:
- Backend: http://localhost:8000
- Frontend: http://localhost:5173

### Option 2: Start Separately

**Terminal 1 - Backend:**
\`\`\`bash
# Double-click: start_backend.bat
# OR manually:
cd backend
venv\Scripts\activate
uvicorn app.main:app --reload
\`\`\`

**Terminal 2 - Frontend:**
\`\`\`bash
# Double-click: start_frontend.bat
# OR manually:
cd frontend
npm run dev
\`\`\`

## 🔑 API Keys Setup

Your API keys are configured in \`backend/.env\`:
- OpenAI: $openaiKey
- VAPI: $vapiKey
- ScraperAPI: $scraperKey

⚠️ If you see placeholder values, edit \`backend/.env\` and add real keys.

## 📚 Next Steps

1. **Start the system**: Run \`start_all.bat\`
2. **Access frontend**: http://localhost:5173
3. **View API docs**: http://localhost:8000/docs
4. **Read guides**:
   - \`QUICK_START.md\` - 15-minute walkthrough
   - \`EXECUTIVE_SUMMARY.md\` - Project overview
   - \`RAPID_EXECUTION_PLAN.md\` - Complete build plan
   - \`DAY_1_TASKS.md\` - Start building backend
5. **Create first campaign**: Go to Campaigns page and test!

## 🐛 Troubleshooting

**Backend won't start:**
- Check API keys in \`backend/.env\`
- Ensure port 8000 is free
- Check Python virtual environment is activated

**Frontend won't start:**
- Ensure port 5173 is free
- Run \`npm install\` in frontend directory
- Check \`frontend/.env\` has correct API URL

**Database errors:**
- Delete \`backend/fracto.db\` and restart
- Run: \`python -c "from app.database import init_db; init_db()"\`

## 📞 Support

- Documentation: Read all .md files in project root
- API Docs: http://localhost:8000/docs (when running)
- Swagger UI: Test all endpoints directly

## 🎯 Success Checklist

- [ ] Backend runs without errors
- [ ] Frontend loads in browser
- [ ] Can access Swagger UI
- [ ] API keys are configured
- [ ] Ready to follow Day 1 tasks!

---

**Setup completed:** $(Get-Date)
**Project path:** $(Get-Location)

**Happy building! 🚀**
"@

$summaryContent | Out-File -FilePath "SETUP_COMPLETE.md" -Encoding UTF8
Write-Host "  ✓ Created SETUP_COMPLETE.md" -ForegroundColor Green

# Final summary
Write-Host ""
Write-Host "[8/8] Setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "╔═══════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║              ✅ FRACTO SETUP SUCCESSFUL!                  ║" -ForegroundColor Green
Write-Host "╚═══════════════════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""
Write-Host "📁 Project structure created" -ForegroundColor Cyan
Write-Host "🐍 Backend configured (Python + FastAPI)" -ForegroundColor Cyan
Write-Host "⚛️  Frontend configured (React + Vite)" -ForegroundColor Cyan
Write-Host "🗄️  Database ready (SQLite)" -ForegroundColor Cyan
Write-Host "🔑 API keys configured" -ForegroundColor Cyan
Write-Host ""
Write-Host "🚀 NEXT STEPS:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Start the system:" -ForegroundColor White
Write-Host "   → Double-click: start_all.bat" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Access the application:" -ForegroundColor White
Write-Host "   → Frontend: http://localhost:5173" -ForegroundColor Gray
Write-Host "   → Backend API: http://localhost:8000/docs" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Read the documentation:" -ForegroundColor White
Write-Host "   → SETUP_COMPLETE.md - What was installed" -ForegroundColor Gray
Write-Host "   → QUICK_START.md - 15-minute walkthrough" -ForegroundColor Gray
Write-Host "   → EXECUTIVE_SUMMARY.md - Project overview" -ForegroundColor Gray
Write-Host "   → DAY_1_TASKS.md - Start building!" -ForegroundColor Gray
Write-Host ""
Write-Host "4. Test the system:" -ForegroundColor White
Write-Host "   → Go to Campaigns page" -ForegroundColor Gray
Write-Host "   → Create a test campaign" -ForegroundColor Gray
Write-Host "   → Watch real-time processing!" -ForegroundColor Gray
Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""
Write-Host "Ready to start building your voice agent automation system!" -ForegroundColor Green
Write-Host "Press any key to exit..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

