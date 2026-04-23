from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class CampaignCreate(BaseModel):
    name: str
    description: Optional[str] = None
    target_type: Optional[str] = None
    search_keywords: Optional[str] = None
    search_location: Optional[str] = None


class CampaignRead(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    target_type: Optional[str] = None
    status: str
    metrics: Optional[dict] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class CampaignUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
