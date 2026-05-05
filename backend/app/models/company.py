from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Float, Integer, JSON, DateTime
from .base import Base, TimestampMixin, TenantMixin

class Company(Base, TimestampMixin, TenantMixin):
    __tablename__ = "companies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    website: Mapped[str | None] = mapped_column(String(512), index=True)
    position: Mapped[str | None] = mapped_column(String(255))
    location: Mapped[str | None] = mapped_column(String(255))
    business_type: Mapped[str | None] = mapped_column(String(100))
    services: Mapped[list | None] = mapped_column(JSON)
    hours: Mapped[str | None] = mapped_column(String(255))
    offers: Mapped[list | None] = mapped_column(JSON)
    booking_url: Mapped[str | None] = mapped_column(String(512))
    phone: Mapped[str | None] = mapped_column(String(50))
    email: Mapped[str | None] = mapped_column(String(255))
    analysis_score: Mapped[float | None] = mapped_column(Float)
    website_quality_score: Mapped[float | None] = mapped_column(Float)
    website_quality_issues: Mapped[list | None] = mapped_column(JSON)
    analysis_source: Mapped[str | None] = mapped_column(String(50))
    owner_user_id: Mapped[int | None] = mapped_column(Integer, index=True)
    pipeline_stage: Mapped[str | None] = mapped_column(String(50), index=True)
    last_contacted_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True))
    notes: Mapped[str | None] = mapped_column(String(2000))
    status: Mapped[str] = mapped_column(String(50), default="pending", index=True)
    data_source: Mapped[str | None] = mapped_column(String(100))
    opted_out: Mapped[bool] = mapped_column(default=False)
    opted_out_at: Mapped[str | None] = mapped_column(String(50))
