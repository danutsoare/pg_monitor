"""Rename hashed_password to encrypted_password on monitored_databases table

Revision ID: 20250505_rename_password_column
Revises: 1fa74f66714b # Previous migration ID for adding apscheduler_jobs
Create Date: 2025-05-05

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '20250505_rename_password_column'
down_revision: Union[str, None] = '1fa74f66714b' # Point to the previous migration
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Rename the column
    op.alter_column('monitored_databases',
                    'hashed_password',
                    new_column_name='encrypted_password',
                    existing_type=sa.String(),
                    nullable=False)


def downgrade() -> None:
    # Rename the column back
    op.alter_column('monitored_databases',
                    'encrypted_password',
                    new_column_name='hashed_password',
                    existing_type=sa.String(),
                    nullable=False) 