# FRACTO — AI Voice Agent Outreach Platform

FRACTO is a production-grade, multi-tenant platform that automates the full outreach lifecycle for AI voice agents. It scrapes business leads, analyses company websites with multi-model AI, generates tailored VAPI voice agent prompts, and manages outreach campaigns — all from a single, self-hosted deployment.

Built for agencies that need a systematic, repeatable way to close clients with live AI voice agent demos.

---

## Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Getting Started](#getting-started)
- [Configuration](#configuration)
- [API Reference](#api-reference)
- [Deployment](#deployment)
- [GDPR & Compliance](#gdpr--compliance)
- [Multi-Tenancy & SaaS](#multi-tenancy--saas)
- [Roadmap](#roadmap)

---

## Features

### Lead Intelligence
- **Automated job scraping** — pulls receptionist and appointment-booking job listings from Indeed with built-in rate limiting and ethical scraping delays
- **Multi-model website analysis** — cascading LLM pipeline (Gemini → OpenAI → Deepseek → local keyword fallback) extracts business type, services, and contact info from any company website
- **Confidence scoring** — every analysed lead is scored so you prioritise your highest-potential prospects first

### Voice Agent Automation
- **One-click VAPI agent creation** — generates a fully-configured VAPI voice assistant for each prospect, complete with a tailored system prompt based on their industry and services
- **Industry-specific prompt templates** — dental, medical, legal, salon, restaurant, and generic templates, enhanced by LLM for each specific company
- **Agent lifecycle management** — create, update, and deactivate VAPI agents from the dashboard

### Campaign Management
- **Multi-campaign support** — run parallel outreach campaigns targeting different business types or geographies
- **Pipeline tracking** — every lead moves through a visible status flow: `pending → analyzing → prompt_ready → agent_created`
- **Celery async workers** — all pipeline jobs run in the background; the UI stays responsive

### Analytics & Reporting
- **Real-time dashboard** — pipeline stats, conversion metrics, and campaign performance at a glance
- **Call log tracking** — duration, outcome, and full transcript for every VAPI call
- **Per-agent performance metrics** — track which voice agents convert and which need tuning

### Security & Compliance
- **JWT authentication** with argon2 password hashing
- **Role-based access control** — admin and standard user roles
- **Rate limiting** — 200 requests/minute per IP via slowapi
- **Security response headers** — X-Content-Type-Options, X-Frame-Options, X-XSS-Protection, Referrer-Policy, HSTS in production
- **GDPR compliance** — opt-out endpoint, right to erasure (PII anonymisation), full data export per company
- **Audit log** — every sensitive action is logged with timestamp and actor

### SaaS & White-label
- **Multi-tenant architecture** — tenant isolation from day one; every record carries a `tenant_id`
- **Stripe billing** — self-service checkout for Starter, Pro, and Agency plans; webhook-driven subscription sync
- **Per-tenant branding** — company name, primary colour, and logo configurable per tenant; applied throughout the UI

---

## Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                          FRACTO Platform                         │
│                                                                  │
│  ┌─────────────┐    ┌──────────────────┐    ┌────────────────┐  │
│  │   React UI  │───▶│  FastAPI Backend │───▶│  PostgreSQL DB │  │
│  │  (Vite/TS)  │    │  (REST API)      │    │                │  │
│  └─────────────┘    └────────┬─────────┘    └────────────────┘  │
│                              │                                   │
│                    ┌─────────▼──────────┐                       │
│                    │    Celery Worker    │                       │
│                    │  (Pipeline Engine)  │                       │
│                    └─────────┬──────────┘                       │
│                              │                                   │
│         ┌────────────────────┼──────────────────────┐           │
│         ▼                    ▼                       ▼           │
│  ┌─────────────┐   ┌──────────────────┐   ┌──────────────────┐  │
│  │  Job Scraper│   │ Website Analyzer  │   │   VAPI Client    │  │
│  │  (Indeed)   │   │ Gemini/OAI/DS/   │   │ (Agent Creation) │  │
│  └─────────────┘   │ Local Fallback    │   └──────────────────┘  │
│                    └──────────────────┘                          │
└──────────────────────────────────────────────────────────────────┘
```

### Pipeline Flow

```
Lead Discovered
      │
      ▼
Website Fetched ──► Multi-LLM Analysis ──► Business Profile
                                                │
                                                ▼
                                    Industry Prompt Generated
                                                │
                                                ▼
                                    VAPI Agent Created ──► Ready for Demo
```

### Directory Structure

```
fracto-voice-agent/
├── backend/
│   ├── app/
│   │   ├── auth/              # JWT, password hashing, route protection
│   │   ├── middleware/        # Rate limiting
│   │   ├── models/            # SQLAlchemy 2.0 models (User, Company, Tenant, ...)
│   │   ├── routers/           # FastAPI routers (companies, agents, campaigns, billing, ...)
│   │   ├── schemas/           # Pydantic request/response schemas
│   │   ├── services/          # Business logic (analyzer, pipeline, billing, GDPR, ...)
│   │   ├── workers/           # Celery app and task definitions
│   │   ├── config.py          # Pydantic Settings from environment
│   │   ├── database.py        # Async SQLAlchemy engine and session
│   │   └── main.py            # FastAPI app, CORS, middleware, router registration
│   ├── alembic/               # Database migrations
│   ├── tests/                 # Pytest test suite
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── api/               # Axios client + per-resource API functions
│   │   ├── components/        # Reusable UI components (Badge, Button, Card, Modal, ...)
│   │   ├── hooks/             # React Query hooks (useBranding, ...)
│   │   ├── pages/             # Page components (Dashboard, Companies, Pipeline, ...)
│   │   ├── store/             # Zustand auth store
│   │   └── App.tsx            # Router, providers, protected routes
│   ├── Dockerfile
│   └── nginx.conf
├── docker-compose.yml
└── README.md
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| **Backend** | Python 3.11, FastAPI 0.115, SQLAlchemy 2.0 (async), Alembic |
| **Task Queue** | Celery 5, Redis 7 |
| **Database** | PostgreSQL 16 |
| **Auth** | JWT (python-jose), argon2-cffi password hashing |
| **AI / LLM** | Google Gemini, OpenAI, Deepseek, local keyword fallback |
| **Voice** | VAPI (agent creation, call management) |
| **Billing** | Stripe (checkout sessions, subscriptions, webhooks) |
| **Frontend** | React 18, TypeScript, Vite, Tailwind CSS 3 |
| **State** | Zustand v5 (auth), TanStack Query v5 (server state) |
| **Routing** | React Router v6 |
| **Deployment** | Docker Compose, Nginx (frontend proxy) |
| **Rate Limiting** | slowapi |

---

## Getting Started

### Prerequisites

- Docker and Docker Compose
- A [VAPI](https://vapi.ai) account and API key
- At least one LLM API key: [Google Gemini](https://aistudio.google.com/) (free tier), [OpenAI](https://platform.openai.com/), or [Deepseek](https://platform.deepseek.com/)

### 1. Clone the repository

```bash
git clone https://github.com/YashVardhan-21/fracto-voice-agent.git
cd fracto-voice-agent
```

### 2. Configure environment variables

```bash
cp backend/.env.example backend/.env
```

Edit `backend/.env` with your values (see [Configuration](#configuration) below).

### 3. Start the platform

```bash
docker compose up --build
```

This starts five services:
- **db** — PostgreSQL 16
- **redis** — Redis 7 (Celery broker + result backend)
- **backend** — FastAPI on port 8000
- **worker** — Celery pipeline worker
- **frontend** — React app served via Nginx on port 3000

### 4. Run database migrations

```bash
docker compose exec backend alembic upgrade head
```

### 5. Create your admin user

```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@yourcompany.com", "password": "your-strong-password", "full_name": "Your Name"}'
```

### 6. Open the dashboard

Navigate to [http://localhost:3000](http://localhost:3000) and log in.

---

## Configuration

All configuration is via environment variables in `backend/.env`.

### Required

| Variable | Description |
|---|---|
| `SECRET_KEY` | JWT signing key — generate with `python -c "import secrets; print(secrets.token_hex(32))"` |
| `DATABASE_URL` | PostgreSQL connection string, e.g. `postgresql://user:pass@db:5432/fracto` |

### LLM Keys (at least one required for AI analysis)

| Variable | Description |
|---|---|
| `GEMINI_API_KEY` | Google Gemini API key (free tier: 15 req/min) |
| `OPENAI_API_KEY` | OpenAI API key |
| `DEEPSEEK_API_KEY` | Deepseek API key |

### Voice Agent

| Variable | Description |
|---|---|
| `VAPI_API_KEY` | VAPI API key |
| `VAPI_PHONE_NUMBER_ID` | VAPI phone number ID for outbound calls |

### Stripe (required for billing features)

| Variable | Description |
|---|---|
| `STRIPE_SECRET_KEY` | Stripe secret key |
| `STRIPE_WEBHOOK_SECRET` | Stripe webhook signing secret |
| `STRIPE_STARTER_PRICE_ID` | Stripe Price ID for Starter plan |
| `STRIPE_PRO_PRICE_ID` | Stripe Price ID for Pro plan |

### Optional

| Variable | Default | Description |
|---|---|---|
| `ENVIRONMENT` | `development` | Set to `production` to enable HSTS and hide API docs |
| `REDIS_URL` | `redis://redis:6379/0` | Redis connection string |
| `FRONTEND_URL` | `http://localhost:5173` | Used for Stripe redirect URLs |
| `ALLOWED_ORIGINS` | `http://localhost:5173,http://localhost:3000` | CORS allowed origins (comma-separated) |

---

## API Reference

Interactive documentation is available at:
- **Swagger UI:** `http://localhost:8000/api/docs`
- **ReDoc:** `http://localhost:8000/api/redoc`

(Hidden in production. Set `ENVIRONMENT=development` to access.)

### Core Endpoints

#### Authentication
| Method | Path | Description |
|---|---|---|
| `POST` | `/api/auth/register` | Register a new user (creates tenant automatically) |
| `POST` | `/api/auth/login` | Login, returns JWT access token |

#### Companies
| Method | Path | Description |
|---|---|---|
| `GET` | `/api/companies` | List all companies (paginated) |
| `POST` | `/api/companies` | Create a company record |
| `GET` | `/api/companies/{id}` | Get company details |
| `PUT` | `/api/companies/{id}` | Update company |
| `DELETE` | `/api/companies/{id}` | Delete company |

#### Pipeline
| Method | Path | Description |
|---|---|---|
| `POST` | `/api/pipeline/run/{company_id}` | Trigger full pipeline for a company (async) |
| `POST` | `/api/pipeline/scrape` | Run job scraper |
| `GET` | `/api/pipeline/status/{company_id}` | Get pipeline status |

#### Voice Agents
| Method | Path | Description |
|---|---|---|
| `GET` | `/api/agents` | List voice agents |
| `POST` | `/api/agents` | Create voice agent manually |
| `DELETE` | `/api/agents/{id}` | Delete voice agent |

#### Campaigns
| Method | Path | Description |
|---|---|---|
| `GET` | `/api/campaigns` | List campaigns |
| `POST` | `/api/campaigns` | Create campaign |
| `PUT` | `/api/campaigns/{id}` | Update campaign |

#### GDPR
| Method | Path | Description |
|---|---|---|
| `POST` | `/api/gdpr/opt-out/{company_id}` | Mark company as opted out |
| `DELETE` | `/api/gdpr/delete/{company_id}` | Erase all PII for a company |
| `GET` | `/api/gdpr/export/{company_id}` | Export all held data for a company |

#### Billing
| Method | Path | Description |
|---|---|---|
| `GET` | `/api/billing/plans` | List available plans |
| `POST` | `/api/billing/checkout/{plan}` | Create Stripe checkout session |
| `POST` | `/api/billing/webhook` | Stripe webhook receiver |

#### Settings
| Method | Path | Description |
|---|---|---|
| `GET` | `/api/settings/branding` | Get tenant branding config |
| `PATCH` | `/api/settings/branding` | Update branding (admin only) |

---

## Deployment

### Production with Docker Compose

1. Set `ENVIRONMENT=production` in your `.env`
2. Set `DATABASE_URL` to your production PostgreSQL (e.g. Railway, Render, Supabase, or self-hosted)
3. Generate a strong `SECRET_KEY`
4. Set all required API keys
5. Configure your domain in `ALLOWED_ORIGINS` and `FRONTEND_URL`
6. Run migrations: `docker compose exec backend alembic upgrade head`
7. Start: `docker compose up -d`

### Health Check

```bash
curl http://localhost:8000/health
# {"status": "healthy", "version": "1.0.0", "environment": "production"}
```

### Scaling Workers

To run multiple Celery workers for higher pipeline throughput:

```bash
docker compose up -d --scale worker=3
```

---

## GDPR & Compliance

FRACTO is designed for compliant outreach operations.

### Data Minimisation
Only business-relevant data is stored: company name, website, inferred business type, services, and contact information extracted from public websites.

### Opt-Out
Any company can be flagged as opted out via `POST /api/gdpr/opt-out/{id}`. Opted-out companies are excluded from all future pipeline runs and outreach.

### Right to Erasure
`DELETE /api/gdpr/delete/{id}` anonymises all PII: name, phone, email, and website are overwritten with placeholder values, and all associated call transcripts are cleared. The record is retained in anonymised form for audit integrity.

### Data Export
`GET /api/gdpr/export/{id}` returns a structured JSON export of all data held for a given company, suitable for responding to subject access requests.

### Audit Log
Every sensitive operation (opt-out, erasure, export) is recorded in the `audit_logs` table with timestamp, actor, and action type.

### Scraping Compliance
The job scraper:
- Sends a realistic browser User-Agent header
- Enforces a minimum delay between requests (in a `finally` block — the delay always fires even on error)
- Respects the intent of robots.txt by not scraping at bulk automated rates
- Only collects publicly available information

---

## Multi-Tenancy & SaaS

FRACTO is architected for multi-tenancy from day one.

### Data Isolation
Every model (companies, voice agents, campaigns, call logs) carries a `tenant_id` column. All queries are scoped to the requesting user's tenant, ensuring complete data isolation between organisations.

### Tenant Creation
Registering a new user automatically creates a new `Tenant` record with a unique, human-readable slug derived from the user's name and a 128-bit random token.

### Plans

| Plan | Voice Agents | Campaigns | Price |
|---|---|---|---|
| Starter | 10 | 5 | €99/month |
| Pro | 100 | 50 | €299/month |
| Agency | Unlimited | Unlimited | €999/month |

Plan upgrades are handled via Stripe Checkout. Subscription state is synced to the `tenants` table via the Stripe webhook.

### White-label
Each tenant can configure their own company name, primary brand colour, and logo URL via `PATCH /api/settings/branding`. Changes are reflected immediately throughout the frontend.

---

## Roadmap

- [ ] LinkedIn outreach integration (connect & message automation)
- [ ] Email outreach with tracked open/click rates
- [ ] Lead enrichment via third-party data providers
- [ ] Multi-user workspaces within a single tenant
- [ ] Usage-based billing (per-agent, per-call)
- [ ] Webhooks — notify external systems on pipeline events
- [ ] Self-service onboarding flow
- [ ] SOC 2 Type II compliance

---

## License

Proprietary. All rights reserved. © Fracto.

---

*Built by the [Fracto](https://fracto.ie) team.*
