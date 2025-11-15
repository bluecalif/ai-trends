"""add created_at/updated_at to dup_group_meta

Revision ID: 20251115_add_meta_timestamps
Revises: 20251115_add_dup_group_meta
Create Date: 2025-11-15
"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime


revision = "20251115_add_meta_timestamps"
down_revision = "20251115_add_dup_group_meta"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("dup_group_meta", sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")))
    op.add_column("dup_group_meta", sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")))
    # remove server_default to keep parity with BaseModel behavior
    op.alter_column("dup_group_meta", "created_at", server_default=None)
    op.alter_column("dup_group_meta", "updated_at", server_default=None)


def downgrade():
    op.drop_column("dup_group_meta", "updated_at")
    op.drop_column("dup_group_meta", "created_at")


