from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import DateTime, String
from datetime import datetime, timezone

class Base(DeclarativeBase):
    pass

class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

class TenantMixin:
    """All data scoped to a tenant. Default 'fracto' for internal use."""
    # FK intentionally omitted — "fracto" default tenant is seeded at deploy time;
    # adding FK here would cascade to all models and require a seed migration.
    tenant_id: Mapped[str] = mapped_column(String(64), index=True, default="fracto")
