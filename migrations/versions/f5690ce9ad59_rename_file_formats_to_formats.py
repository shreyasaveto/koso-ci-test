"""rename file_formats to formats

Revision ID: f5690ce9ad59
Revises: 7dbd43483cb9
Create Date: 2025-10-07 10:25:46.499083

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'f5690ce9ad59'
down_revision: Union[str, Sequence[str], None] = '7dbd43483cb9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade():
    op.rename_table('file_formats', 'formats')

def downgrade():
    op.rename_table('formats', 'file_formats')

