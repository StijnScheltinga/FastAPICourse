"""Create phone number for user column

Revision ID: f2c22bfacb9d
Revises: 
Create Date: 2025-05-15 10:10:09.220384

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f2c22bfacb9d'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users', sa.Column('phone_number', sa.String(), nullable=True))


def downgrade() -> None:
	op.drop_column('users', 'phone_number')
