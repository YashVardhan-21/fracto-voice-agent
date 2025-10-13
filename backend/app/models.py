"""
Database models for the FRACTO system
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Float, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class Company(Base):
    """Company model for storing scraped business information"""
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    website = Column(String, unique=True, index=True)
    position = Column(String)
    location = Column(String)
    business_type = Column(String)
    services = Column(JSON)
    hours = Column(String)
    phone = Column(String)
    analysis_score = Column(Float)
    status = Column(String, default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class VoiceAgent(Base):
    """Voice agent model for VAPI integration"""
    __tablename__ = "voice_agents"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, index=True)
    name = Column(String)
    vapi_id = Column(String, unique=True)
    system_prompt = Column(Text)
    voice_config = Column(JSON)
    status = Column(String, default="active")
    performance_metrics = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Campaign(Base):
    """Campaign model for outreach management"""
    __tablename__ = "campaigns"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    description = Column(Text)
    target_type = Column(String)
    prospects = Column(JSON)
    metrics = Column(JSON)
    status = Column(String, default="draft")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class CallLog(Base):
    """Call log model for tracking voice agent interactions"""
    __tablename__ = "call_logs"

    id = Column(Integer, primary_key=True, index=True)
    voice_agent_id = Column(Integer, index=True)
    call_id = Column(String, unique=True)
    phone_number = Column(String)
    duration = Column(Integer)  # seconds
    status = Column(String)
    transcript = Column(Text)
    outcome = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
