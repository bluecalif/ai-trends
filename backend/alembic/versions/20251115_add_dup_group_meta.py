"""add dup_group_meta table

Revision ID: 20251115_add_dup_group_meta
Revises: ea1fbe012a50_initial_migration
Create Date: 2025-11-15
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "20251115_add_dup_group_meta"
down_revision = "ea1fbe012a50"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "dup_group_meta",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("dup_group_id", sa.Integer(), nullable=False),
        sa.Column("first_seen_at", sa.DateTime(), nullable=False),
        sa.Column("last_updated_at", sa.DateTime(), nullable=False),
        sa.Column("member_count", sa.Integer(), nullable=False, server_default="1"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_dup_group_meta_dup_group_id", "dup_group_meta", ["dup_group_id"], unique=True)
    op.create_index("ix_dup_group_meta_first_seen_at", "dup_group_meta", ["first_seen_at"])
    op.create_index("ix_dup_group_meta_last_updated_at", "dup_group_meta", ["last_updated_at"])


def downgrade():
    op.drop_index("ix_dup_group_meta_last_updated_at", table_name="dup_group_meta")
    op.drop_index("ix_dup_group_meta_first_seen_at", table_name="dup_group_meta")
    op.drop_index("ix_dup_group_meta_dup_group_id", table_name="dup_group_meta")
    op.drop_table("dup_group_meta")


