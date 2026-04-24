"""add_company_context_fields

Revision ID: 8b9d3f4c2a10
Revises: 6f6d0507d3fd
Create Date: 2026-04-23 20:20:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "8b9d3f4c2a10"
down_revision: Union[str, Sequence[str], None] = "6f6d0507d3fd"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("companies", sa.Column("offers", sa.JSON(), nullable=True))
    op.add_column("companies", sa.Column("booking_url", sa.String(length=512), nullable=True))
    op.add_column("companies", sa.Column("website_quality_score", sa.Float(), nullable=True))
    op.add_column("companies", sa.Column("website_quality_issues", sa.JSON(), nullable=True))


def downgrade() -> None:
    op.drop_column("companies", "website_quality_issues")
    op.drop_column("companies", "website_quality_score")
    op.drop_column("companies", "booking_url")
    op.drop_column("companies", "offers")
