"""change_item_author_to_text

Revision ID: 3c51146a302b
Revises: 20251115_add_meta_timestamps
Create Date: 2025-11-18 20:27:09.315141

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3c51146a302b'
down_revision: Union[str, Sequence[str], None] = '20251115_add_meta_timestamps'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema: Change items.author from String(255) to Text."""
    # Change author column from String(255) to Text
    op.alter_column('items', 'author',
                    existing_type=sa.String(length=255),
                    type_=sa.Text(),
                    existing_nullable=True)


def downgrade() -> None:
    """Downgrade schema: Change items.author from Text back to String(255)."""
    # Change author column from Text back to String(255)
    op.alter_column('items', 'author',
                    existing_type=sa.Text(),
                    type_=sa.String(length=255),
                    existing_nullable=True)
