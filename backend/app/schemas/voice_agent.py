from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class VoiceAgentRead(BaseModel):
    id: int
    company_id: int
    name: str
    vapi_agent_id: Optional[str] = None
    system_prompt: Optional[str] = None
    status: str
    total_calls: int
    successful_calls: int
    created_at: datetime

    model_config = {"from_attributes": True}
