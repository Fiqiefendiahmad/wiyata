"""initial schema

Revision ID: 001
Revises:
Create Date: 2026-11-06

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")

    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("email", sa.String(320), unique=True, nullable=True),
        sa.Column("display_name", sa.String(160), nullable=True),
        sa.Column("password_hash", sa.Text, nullable=True),
        sa.Column("status", sa.String(30), nullable=False, server_default="active"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    op.create_table(
        "workspaces",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(160), nullable=False),
        sa.Column("owner_user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    op.create_table(
        "user_preferences",
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("language", sa.String(2), nullable=False, server_default="en"),
        sa.Column("theme", sa.String(20), nullable=False, server_default="system"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    op.create_table(
        "saved_queries",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("workspace_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False),
        sa.Column("owner_user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("engine", sa.String(50), nullable=True),
        sa.Column("dialect", sa.String(50), nullable=True),
        sa.Column("query_text", sa.Text, nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )
    op.create_index("idx_saved_queries_workspace", "saved_queries", ["workspace_id"])

    op.create_table(
        "sandboxes",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("owner_user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("guest_session_hash", sa.Text, nullable=True),
        sa.Column("engine", sa.String(50), nullable=False),
        sa.Column("engine_version", sa.String(80), nullable=True),
        sa.Column("template_slug", sa.String(100), nullable=True),
        sa.Column("status", sa.String(30), nullable=False, server_default="requested"),
        sa.Column("storage_reference", sa.Text, nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("resource_policy", postgresql.JSONB, nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )
    op.create_index("idx_sandboxes_expiry", "sandboxes", ["status", "expires_at"])

    op.create_table(
        "knowledge_categories",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("slug", sa.String(120), unique=True, nullable=False),
        sa.Column("parent_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("knowledge_categories.id"), nullable=True),
        sa.Column("sort_order", sa.Integer, nullable=False, server_default="0"),
    )

    op.create_table(
        "knowledge_articles",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("slug", sa.String(200), nullable=False),
        sa.Column("language", sa.String(2), nullable=False),
        sa.Column("title", sa.String(300), nullable=False),
        sa.Column("summary", sa.Text, nullable=True),
        sa.Column("body_markdown", sa.Text, nullable=False),
        sa.Column("status", sa.String(30), nullable=False, server_default="draft"),
        sa.Column("category_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("knowledge_categories.id"), nullable=True),
        sa.Column("engine", sa.String(50), nullable=True),
        sa.Column("version_scope", postgresql.JSONB, nullable=False, server_default="[]"),
        sa.Column("references_json", postgresql.JSONB, nullable=False, server_default="[]"),
        sa.Column("last_reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.UniqueConstraint("slug", "language"),
    )

    op.create_table(
        "tool_categories",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("slug", sa.String(120), unique=True, nullable=False),
        sa.Column("name", sa.String(160), nullable=False),
    )

    op.create_table(
        "professional_tools",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("slug", sa.String(160), unique=True, nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("vendor", sa.String(200), nullable=True),
        sa.Column("category_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("summary", sa.Text, nullable=True),
        sa.Column("official_url", sa.Text, nullable=True),
        sa.Column("documentation_url", sa.Text, nullable=True),
        sa.Column("license_model", sa.String(50), nullable=True),
        sa.Column("supported_platforms", postgresql.JSONB, nullable=False, server_default="[]"),
        sa.Column("supported_engines", postgresql.JSONB, nullable=False, server_default="[]"),
        sa.Column("last_verified_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    op.create_table(
        "learning_paths",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("slug", sa.String(160), unique=True, nullable=False),
        sa.Column("title", sa.String(240), nullable=False),
        sa.Column("language", sa.String(2), nullable=False, server_default="en"),
        sa.Column("level", sa.String(30), nullable=True),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("published", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    op.create_table(
        "audit_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("actor_user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("workspace_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("workspaces.id", ondelete="SET NULL"), nullable=True),
        sa.Column("action", sa.String(120), nullable=False),
        sa.Column("resource_type", sa.String(100), nullable=True),
        sa.Column("resource_id", sa.Text, nullable=True),
        sa.Column("outcome", sa.String(30), nullable=False),
        sa.Column("correlation_id", sa.Text, nullable=True),
        sa.Column("metadata", postgresql.JSONB, nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )
    op.create_index("idx_audit_events_created_at", "audit_events", [sa.text("created_at DESC")])


def downgrade() -> None:
    op.drop_table("audit_events")
    op.drop_table("learning_paths")
    op.drop_table("professional_tools")
    op.drop_table("tool_categories")
    op.drop_table("knowledge_articles")
    op.drop_table("knowledge_categories")
    op.drop_table("sandboxes")
    op.drop_index("idx_saved_queries_workspace", "saved_queries")
    op.drop_table("saved_queries")
    op.drop_table("user_preferences")
    op.drop_table("workspaces")
    op.drop_table("users")
