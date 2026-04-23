from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Text, Integer, JSON, ForeignKey
from .base import Base, TimestampMixin, TenantMixin

class VoiceAgent(Base, TimestampMixin, TenantMixin):
    __tablename__ = "voice_agents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    company_id: Mapped[int] = mapped_column(Integer, ForeignKey("companies.id"), index=True)
    name: Mapped[str] = mapped_column(String(255))
    vapi_agent_id: Mapped[str | None] = mapped_column(String(255), unique=True)
    system_prompt: Mapped[str | None] = mapped_column(Text)
    voice_config: Mapped[dict | None] = mapped_column(JSON)
    status: Mapped[str] = mapped_column(String(50), default="draft")
    performance_metrics: Mapped[dict | None] = mapped_column(JSON)
    total_calls: Mapped[int] = mapped_column(Integer, default=0)
    successful_calls: Mapped[int] = mapped_column(Integer, default=0)
