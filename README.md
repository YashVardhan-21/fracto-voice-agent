# FRACTO Voice Agent Platform

FRACTO is a lead discovery and AI voice-agent operations platform for agencies and internal growth teams. It helps teams identify companies with front-desk or appointment-handling needs, analyze their public web presence, generate tailored voice-agent instructions, and create VAPI assistants for outreach and operational testing.

## Platform Overview

FRACTO combines lead sourcing, website intelligence, prompt generation, VAPI assistant creation, and campaign workflows into one SaaS-style dashboard.

Core capabilities:

- Multi-source lead discovery from public job boards, Google Places, and partner APIs.
- Persistent company database with tenant-scoped records.
- Website analysis for services, hours, booking links, offers, contact details, and website quality.
- Lead scoring to prioritize companies with stronger outreach potential.
- AI receptionist prompt generation tailored to each company.
- VAPI assistant creation with configurable voice settings.
- Website quality and upsell opportunity indicators.
- Excel export for sales and outreach workflows.
- Campaign and call-log foundations for outbound operations.

## Architecture

The platform is split into three primary services:

- **Frontend:** React, TypeScript, Vite, Tailwind CSS, TanStack Query.
- **Backend API:** FastAPI, SQLAlchemy, Alembic, JWT authentication.
- **Background worker:** Celery with Redis for long-running scraping, website analysis, prompt generation, and VAPI assistant creation.

Production data is stored in PostgreSQL. Redis is used as the Celery broker/result backend.

## Multi-Tenant Model

The application includes tenant-scoped data foundations. Core business records such as users, companies, voice agents, campaigns, call logs, and audit logs are associated with a `tenant_id`.

For internal team usage, the recommended operating model is:

- One internal FRACTO workspace tenant.
- Multiple users under the same tenant.
- Shared company, campaign, agent, and call data.
- Role-based access for admins, managers, and outreach operators.

For full self-serve SaaS usage, the next production step is to move integration credentials from environment variables into encrypted tenant-level settings. This allows each customer or internal workspace to configure its own VAPI, voice, lead source, and LLM credentials independently.

## Lead Discovery Pipeline

The lead pipeline is designed to avoid reliance on a single brittle source.

Supported sources include:

- Google Places for verified local business data.
- Adzuna for hiring-intent signals.
- Remotive for public job listings.
- Indeed public pages where available.

Lead records are ranked and deduplicated before being persisted. Existing companies are updated with fresher website, phone, email, hours, booking, and score data when higher-confidence signals are found.

## Website Intelligence

The website analyzer extracts practical business context used by the generated voice agent:

- Business type.
- Services.
- Opening hours.
- Published offers and pricing signals.
- Booking/contact URLs.
- Phone and email.
- Website quality score.
- Website quality issues.

This lets the assistant instructions stay specific to the company rather than generic.

## Voice Agent Personalization

For each company, FRACTO generates compact VAPI-ready system instructions containing:

- Receptionist role.
- Company-specific business facts.
- Services, hours, offers, and contact details.
- Booking guidance.
- Rules to avoid hallucinating unknown policies, prices, or medical/legal advice.
- Sales context for website plus voice automation upsell when appropriate.

The pipeline updates existing voice-agent records for a company so stale prompts are not reused.

## Local Development

### Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
alembic upgrade head
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

### Worker

On Windows, use Celery solo mode:

```bash
cd backend
.venv\Scripts\activate
python -m celery -A app.workers.celery_app worker -P solo --loglevel=info
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend runs on `http://127.0.0.1:5173` by default.

## Environment Variables

Use `.env.example` and `backend/.env.example` as templates. Do not commit real secrets.

Important backend variables:

- `SECRET_KEY`
- `DATABASE_URL`
- `REDIS_URL`
- `VAPI_API_KEY`
- `VAPI_VOICE_ID`
- `GOOGLE_PLACES_API_KEY`
- `ADZUNA_APP_ID`
- `ADZUNA_APP_KEY`
- `GEMINI_API_KEY`, `OPENAI_API_KEY`, or `DEEPSEEK_API_KEY`

For Supabase transaction pooler URLs, include SSL mode:

```text
?sslmode=require
```

URL-encode special characters in passwords, for example `#` as `%23`.

## Production Deployment Notes

Recommended production setup:

- Frontend on Vercel.
- Backend API on Render, Fly.io, Railway, AWS, or another long-running container host.
- Celery worker on the same backend platform or a worker-capable host.
- Managed PostgreSQL via Supabase or another provider.
- Managed Redis via Upstash, Redis Cloud, or equivalent.

Avoid deploying the FastAPI worker stack as pure Vercel serverless functions because scraping, analysis, and VAPI provisioning need background processing.

Before production launch:

- Configure production `ALLOWED_ORIGINS`.
- Rotate all local development secrets.
- Enable HTTPS-only frontend/backend URLs.
- Set per-tenant/user job limits.
- Move customer-specific API credentials into encrypted tenant settings.
- Add monitoring for failed scraping, failed VAPI creation, and queue latency.

## Security Practices

- Real `.env` files are ignored and must not be committed.
- Python cache files, virtual environments, local databases, and frontend build artifacts are ignored.
- Public API keys and third-party credentials should be stored only in platform environment variables or encrypted tenant settings.
- All tenant-owned data should be accessed through authenticated tenant-scoped queries.

## Roadmap

Near-term roadmap:

- Internal team workspace with multiple users.
- Tenant-level VAPI integration settings.
- Lead assignment and outreach stage tracking.
- Campaign execution flow connected to selected agents.
- Better audit trails for scrape, analysis, and assistant creation events.
- Production deployment hardening.

Longer-term roadmap:

- Self-serve workspace onboarding.
- Per-tenant billing and usage limits.
- Encrypted customer integration vault.
- Advanced lead segmentation and outbound sequencing.
- Deeper call analytics and conversion reporting.
