from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Text, Integer, JSON
from .base import Base, TimestampMixin, TenantMixin

class Campaign(Base, TimestampMixin, TenantMixin):
    __tablename__ = "campaigns"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text)
    target_type: Mapped[str | None] = mapped_column(String(100))
    search_keywords: Mapped[str | None] = mapped_column(String(255))
    search_location: Mapped[str | None] = mapped_column(String(255))
    prospects: Mapped[list | None] = mapped_column(JSON)
    metrics: Mapped[dict | None] = mapped_column(JSON)
    status: Mapped[str] = mapped_column(String(50), default="draft", index=True)
    created_by: Mapped[int | None] = mapped_column(Integer)
