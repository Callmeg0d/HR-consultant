"""change_dates_to_month_year

Revision ID: 3ddd7b759953
Revises: 65c183997b95
Create Date: 2025-09-20 14:39:47.203622

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3ddd7b759953'
down_revision: Union[str, Sequence[str], None] = '65c183997b95'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Изменяем поля дат на строки для хранения месяца и года
    op.alter_column('work_experiences', 'start_date', type_=sa.String(7), new_column_name='start_period')
    op.alter_column('work_experiences', 'end_date', type_=sa.String(7), new_column_name='end_period')
    
    op.alter_column('educations', 'start_date', type_=sa.String(7), new_column_name='start_period')
    op.alter_column('educations', 'end_date', type_=sa.String(7), new_column_name='end_period')


def downgrade() -> None:
    """Downgrade schema."""
    # Возвращаем обратно к DateTime
    op.alter_column('work_experiences', 'start_period', type_=sa.DateTime, new_column_name='start_date')
    op.alter_column('work_experiences', 'end_period', type_=sa.DateTime, new_column_name='end_date')
    
    op.alter_column('educations', 'start_period', type_=sa.DateTime, new_column_name='start_date')
    op.alter_column('educations', 'end_period', type_=sa.DateTime, new_column_name='end_date')
