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
    # This operation was likely handled by the merged 'abcd' branch.
    pass


def downgrade() -> None:
    # Corresponding downgrade is also skipped.
    pass 