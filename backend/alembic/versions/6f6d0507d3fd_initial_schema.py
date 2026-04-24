"""initial_schema

Revision ID: 6f6d0507d3fd
Revises: 
Create Date: 2026-04-23 12:56:38.111600

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6f6d0507d3fd'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "tenants",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("slug", sa.String(length=64), nullable=False),
        sa.Column("plan", sa.String(length=50), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("settings", sa.JSON(), nullable=True),
        sa.Column("stripe_customer_id", sa.String(length=255), nullable=True),
        sa.Column("stripe_subscription_id", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_tenants_slug"), "tenants", ["slug"], unique=True)

    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("is_admin", sa.Boolean(), nullable=False),
        sa.Column("role", sa.String(length=50), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("tenant_id", sa.String(length=64), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)
    op.create_index(op.f("ix_users_tenant_id"), "users", ["tenant_id"], unique=False)

    op.create_table(
        "companies",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("website", sa.String(length=512), nullable=True),
        sa.Column("position", sa.String(length=255), nullable=True),
        sa.Column("location", sa.String(length=255), nullable=True),
        sa.Column("business_type", sa.String(length=100), nullable=True),
        sa.Column("services", sa.JSON(), nullable=True),
        sa.Column("hours", sa.String(length=255), nullable=True),
        sa.Column("phone", sa.String(length=50), nullable=True),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("analysis_score", sa.Float(), nullable=True),
        sa.Column("analysis_source", sa.String(length=50), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("data_source", sa.String(length=100), nullable=True),
        sa.Column("opted_out", sa.Boolean(), nullable=False),
        sa.Column("opted_out_at", sa.String(length=50), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("tenant_id", sa.String(length=64), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_companies_name"), "companies", ["name"], unique=False)
    op.create_index(op.f("ix_companies_website"), "companies", ["website"], unique=False)
    op.create_index(op.f("ix_companies_status"), "companies", ["status"], unique=False)
    op.create_index(op.f("ix_companies_tenant_id"), "companies", ["tenant_id"], unique=False)

    op.create_table(
        "campaigns",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("target_type", sa.String(length=100), nullable=True),
        sa.Column("search_keywords", sa.String(length=255), nullable=True),
        sa.Column("search_location", sa.String(length=255), nullable=True),
        sa.Column("prospects", sa.JSON(), nullable=True),
        sa.Column("metrics", sa.JSON(), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("created_by", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("tenant_id", sa.String(length=64), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_campaigns_status"), "campaigns", ["status"], unique=False)
    op.create_index(op.f("ix_campaigns_tenant_id"), "campaigns", ["tenant_id"], unique=False)

    op.create_table(
        "voice_agents",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("company_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("vapi_agent_id", sa.String(length=255), nullable=True),
        sa.Column("system_prompt", sa.Text(), nullable=True),
        sa.Column("voice_config", sa.JSON(), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("performance_metrics", sa.JSON(), nullable=True),
        sa.Column("total_calls", sa.Integer(), nullable=False),
        sa.Column("successful_calls", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("tenant_id", sa.String(length=64), nullable=False),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_voice_agents_company_id"), "voice_agents", ["company_id"], unique=False)
    op.create_index(op.f("ix_voice_agents_tenant_id"), "voice_agents", ["tenant_id"], unique=False)
    op.create_index(op.f("ix_voice_agents_vapi_agent_id"), "voice_agents", ["vapi_agent_id"], unique=True)

    op.create_table(
        "call_logs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("voice_agent_id", sa.Integer(), nullable=False),
        sa.Column("campaign_id", sa.Integer(), nullable=True),
        sa.Column("vapi_call_id", sa.String(length=255), nullable=True),
        sa.Column("phone_number", sa.String(length=50), nullable=True),
        sa.Column("duration_seconds", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("transcript", sa.Text(), nullable=True),
        sa.Column("outcome", sa.String(length=100), nullable=True),
        sa.Column("sentiment_score", sa.Float(), nullable=True),
        sa.Column("recording_url", sa.String(length=512), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("tenant_id", sa.String(length=64), nullable=False),
        sa.ForeignKeyConstraint(["campaign_id"], ["campaigns.id"]),
        sa.ForeignKeyConstraint(["voice_agent_id"], ["voice_agents.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_call_logs_campaign_id"), "call_logs", ["campaign_id"], unique=False)
    op.create_index(op.f("ix_call_logs_tenant_id"), "call_logs", ["tenant_id"], unique=False)
    op.create_index(op.f("ix_call_logs_vapi_call_id"), "call_logs", ["vapi_call_id"], unique=True)
    op.create_index(op.f("ix_call_logs_voice_agent_id"), "call_logs", ["voice_agent_id"], unique=False)

    op.create_table(
        "audit_logs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("tenant_id", sa.String(length=64), nullable=False),
        sa.Column("actor_id", sa.Integer(), nullable=True),
        sa.Column("action", sa.String(length=100), nullable=False),
        sa.Column("resource_type", sa.String(length=100), nullable=False),
        sa.Column("resource_id", sa.String(length=255), nullable=True),
        sa.Column("details", sa.JSON(), nullable=True),
        sa.Column("ip_address", sa.String(length=45), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_audit_logs_action"), "audit_logs", ["action"], unique=False)
    op.create_index(op.f("ix_audit_logs_tenant_id"), "audit_logs", ["tenant_id"], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f("ix_audit_logs_tenant_id"), table_name="audit_logs")
    op.drop_index(op.f("ix_audit_logs_action"), table_name="audit_logs")
    op.drop_table("audit_logs")

    op.drop_index(op.f("ix_call_logs_voice_agent_id"), table_name="call_logs")
    op.drop_index(op.f("ix_call_logs_vapi_call_id"), table_name="call_logs")
    op.drop_index(op.f("ix_call_logs_tenant_id"), table_name="call_logs")
    op.drop_index(op.f("ix_call_logs_campaign_id"), table_name="call_logs")
    op.drop_table("call_logs")

    op.drop_index(op.f("ix_voice_agents_vapi_agent_id"), table_name="voice_agents")
    op.drop_index(op.f("ix_voice_agents_tenant_id"), table_name="voice_agents")
    op.drop_index(op.f("ix_voice_agents_company_id"), table_name="voice_agents")
    op.drop_table("voice_agents")

    op.drop_index(op.f("ix_campaigns_tenant_id"), table_name="campaigns")
    op.drop_index(op.f("ix_campaigns_status"), table_name="campaigns")
    op.drop_table("campaigns")

    op.drop_index(op.f("ix_companies_tenant_id"), table_name="companies")
    op.drop_index(op.f("ix_companies_status"), table_name="companies")
    op.drop_index(op.f("ix_companies_website"), table_name="companies")
    op.drop_index(op.f("ix_companies_name"), table_name="companies")
    op.drop_table("companies")

    op.drop_index(op.f("ix_users_tenant_id"), table_name="users")
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_table("users")

    op.drop_index(op.f("ix_tenants_slug"), table_name="tenants")
    op.drop_table("tenants")
