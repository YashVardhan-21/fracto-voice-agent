"""add_company_owner_stage_fields

Revision ID: 9c4a7d8e1b22
Revises: 8b9d3f4c2a10
Create Date: 2026-05-05 11:55:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "9c4a7d8e1b22"
down_revision: Union[str, Sequence[str], None] = "8b9d3f4c2a10"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("companies", sa.Column("owner_user_id", sa.Integer(), nullable=True))
    op.add_column("companies", sa.Column("pipeline_stage", sa.String(length=50), nullable=True))
    op.add_column("companies", sa.Column("last_contacted_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("companies", sa.Column("notes", sa.String(length=2000), nullable=True))
    op.create_index("ix_companies_owner_user_id", "companies", ["owner_user_id"], unique=False)
    op.create_index("ix_companies_pipeline_stage", "companies", ["pipeline_stage"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_companies_pipeline_stage", table_name="companies")
    op.drop_index("ix_companies_owner_user_id", table_name="companies")
    op.drop_column("companies", "notes")
    op.drop_column("companies", "last_contacted_at")
    op.drop_column("companies", "pipeline_stage")
    op.drop_column("companies", "owner_user_id")
