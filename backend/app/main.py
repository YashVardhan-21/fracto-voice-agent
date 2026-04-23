from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.auth.router import router as auth_router
from app.routers.companies import router as companies_router
from app.routers.voice_agents import router as agents_router
from app.routers.campaigns import router as campaigns_router
from app.routers.pipeline import router as pipeline_router
from app.routers.analytics import router as analytics_router
from app.routers.gdpr import router as gdpr_router
from app.routers.billing import router as billing_router
from app.routers.settings_router import router as settings_router
from app.middleware.rate_limit import limiter, _rate_limit_exceeded_handler, RateLimitExceeded

app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    docs_url="/api/docs" if settings.environment != "production" else None,
    redoc_url="/api/redoc" if settings.environment != "production" else None,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def security_headers(request: Request, call_next):
    response: Response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response


app.include_router(auth_router, prefix="/api")
app.include_router(companies_router, prefix="/api")
app.include_router(agents_router, prefix="/api")
app.include_router(campaigns_router, prefix="/api")
app.include_router(pipeline_router, prefix="/api")
app.include_router(analytics_router, prefix="/api")
app.include_router(gdpr_router, prefix="/api")
app.include_router(billing_router, prefix="/api")
app.include_router(settings_router, prefix="/api")


@app.get("/health")
async def health():
    return {"status": "healthy", "env": settings.environment, "version": "1.0.0"}
