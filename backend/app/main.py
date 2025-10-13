"""
FRACTO Voice Agent Outreach Automation System
Main FastAPI application entry point
"""
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import uvicorn

from .core.config import settings
from .core.database import engine, get_db
from .models import Base
from .routers import campaigns, companies, voice_agents, scrapers

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="FRACTO Voice Agent Automation",
    description="Enterprise-grade voice agent outreach automation system",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(campaigns.router, prefix="/api/campaigns", tags=["campaigns"])
app.include_router(companies.router, prefix="/api/companies", tags=["companies"])
app.include_router(voice_agents.router, prefix="/api/voice-agents", tags=["voice-agents"])
app.include_router(scrapers.router, prefix="/api/scrapers", tags=["scrapers"])

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "FRACTO Voice Agent Automation System", "status": "active"}

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT,
        "database": "connected"
    }

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True if settings.ENVIRONMENT == "development" else False
    )
