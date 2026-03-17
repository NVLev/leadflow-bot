"""fix user_id type

Revision ID: 3d5291081f91
Revises: c28ec1e31709
Create Date: 2026-03-16 23:49:59.787940

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3d5291081f91'
down_revision: Union[str, Sequence[str], None] = 'c28ec1e31709'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column('leads', 'user_id',
               existing_type=sa.INTEGER(),
               type_=sa.BigInteger(),
               existing_nullable=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column('leads', 'user_id',
               existing_type=sa.BigInteger(),
               type_=sa.INTEGER(),
               existing_nullable=False)
    # ### end Alembic commands ###
