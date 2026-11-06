"""add tool details and verification columns

Revision ID: 002
Revises: 001
Create Date: 2026-11-06

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "002"
down_revision = "001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "professional_tools",
        sa.Column("details", postgresql.JSONB, nullable=False, server_default=sa.text("'{}'::jsonb")),
    )
    op.add_column(
        "professional_tools",
        sa.Column("category_slug", sa.String(120), nullable=True),
    )
    op.add_column(
        "professional_tools",
        sa.Column("publication_status", sa.String(50), nullable=False, server_default="published"),
    )
    op.add_column(
        "professional_tools",
        sa.Column("verification_status", sa.String(50), nullable=False, server_default="verified"),
    )
    op.add_column(
        "tool_categories",
        sa.Column("name_id", sa.String(160), nullable=True),
    )
    op.add_column(
        "tool_categories",
        sa.Column("description_en", sa.Text, nullable=True),
    )
    op.add_column(
        "tool_categories",
        sa.Column("description_id", sa.Text, nullable=True),
    )
    op.create_index(
        "idx_professional_tools_category_slug",
        "professional_tools",
        ["category_slug"],
    )
    op.create_index(
        "idx_professional_tools_pub_status",
        "professional_tools",
        ["publication_status"],
    )


def downgrade() -> None:
    op.drop_index("idx_professional_tools_pub_status", table_name="professional_tools")
    op.drop_index("idx_professional_tools_category_slug", table_name="professional_tools")
    op.drop_column("tool_categories", "description_id")
    op.drop_column("tool_categories", "description_en")
    op.drop_column("tool_categories", "name_id")
    op.drop_column("professional_tools", "verification_status")
    op.drop_column("professional_tools", "publication_status")
    op.drop_column("professional_tools", "category_slug")
    op.drop_column("professional_tools", "details")
