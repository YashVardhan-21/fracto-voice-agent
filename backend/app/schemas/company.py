from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class CompanyCreate(BaseModel):
    name: str
    website: Optional[str] = None
    position: Optional[str] = None
    location: Optional[str] = None
    phone: Optional[str] = None


class CompanyRead(BaseModel):
    id: int
    name: str
    website: Optional[str] = None
    location: Optional[str] = None
    business_type: Optional[str] = None
    services: Optional[list] = None
    phone: Optional[str] = None
    analysis_score: Optional[float] = None
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class CompanyUpdate(BaseModel):
    name: Optional[str] = None
    website: Optional[str] = None
    phone: Optional[str] = None
    status: Optional[str] = None
