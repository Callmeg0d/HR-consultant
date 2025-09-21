"""add_indexes_for_embds

Revision ID: 65c183997b95
Revises: ff14d24443c2
Create Date: 2025-09-20 14:15:48.291986

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '65c183997b95'
down_revision: Union[str, Sequence[str], None] = 'ff14d24443c2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Добавляем индексы для ускорения поиска
    op.create_index('ix_employee_embeddings_employee_id', 'employee_embeddings', ['employee_id'])
    op.create_index('ix_employees_position', 'employees', ['position'])
    op.create_index('ix_employees_department', 'employees', ['department'])
    op.create_index('ix_employees_experience_years', 'employees', ['experience_years'])


def downgrade() -> None:
    """Downgrade schema."""
    # Удаляем индексы
    op.drop_index('ix_employees_experience_years', table_name='employees')
    op.drop_index('ix_employees_department', table_name='employees')
    op.drop_index('ix_employees_position', table_name='employees')
    op.drop_index('ix_employee_embeddings_employee_id', table_name='employee_embeddings')
