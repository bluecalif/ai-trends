"""add_required_optional_keywords_to_watch_rules

Revision ID: 4a149ba61080
Revises: 3c51146a302b
Create Date: 2025-11-19 19:45:41.247471

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '4a149ba61080'
down_revision: Union[str, Sequence[str], None] = '3c51146a302b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema: Add required_keywords and optional_keywords to watch_rules."""
    # Add required_keywords and optional_keywords columns with default empty list
    op.add_column('watch_rules', sa.Column('required_keywords', postgresql.JSON(astext_type=sa.Text()), nullable=False, server_default='[]'))
    op.add_column('watch_rules', sa.Column('optional_keywords', postgresql.JSON(astext_type=sa.Text()), nullable=False, server_default='[]'))


def downgrade() -> None:
    """Downgrade schema: Remove required_keywords and optional_keywords from watch_rules."""
    op.drop_column('watch_rules', 'optional_keywords')
    op.drop_column('watch_rules', 'required_keywords')
