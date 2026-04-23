from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Text, Integer, ForeignKey, Float
from .base import Base, TimestampMixin, TenantMixin

class CallLog(Base, TimestampMixin, TenantMixin):
    __tablename__ = "call_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    voice_agent_id: Mapped[int] = mapped_column(Integer, ForeignKey("voice_agents.id"), index=True)
    campaign_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("campaigns.id"), index=True)
    vapi_call_id: Mapped[str | None] = mapped_column(String(255), unique=True)
    phone_number: Mapped[str | None] = mapped_column(String(50))
    duration_seconds: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(50), default="pending")
    transcript: Mapped[str | None] = mapped_column(Text)
    outcome: Mapped[str | None] = mapped_column(String(100))
    sentiment_score: Mapped[float | None] = mapped_column(Float)
    recording_url: Mapped[str | None] = mapped_column(String(512))
