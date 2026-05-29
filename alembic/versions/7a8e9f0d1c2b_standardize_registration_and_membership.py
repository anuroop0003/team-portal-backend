"""standardize registration and membership

Revision ID: 7a8e9f0d1c2b
Revises: 12b47ce7f876
Create Date: 2026-04-16 23:43:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '7a8e9f0d1c2b'
down_revision: Union[str, Sequence[str], None] = '12b47ce7f876'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Rename 'initial' to 'code' in organizations
    op.alter_column('organizations', 'initial', new_column_name='code')
    
    # 2. Drop redundant 'full_name'
    op.drop_column('organizations', 'full_name')
    
    # 3. Create memberships table
    op.create_table(
        'memberships',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('role', sa.String(), nullable=False, server_default='employee'),
        sa.Column('is_active', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_memberships_id'), 'memberships', ['id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_memberships_id'), table_name='memberships')
    op.drop_table('memberships')
    op.add_column('organizations', sa.Column('full_name', sa.String(), nullable=True))
    op.alter_column('organizations', 'code', new_column_name='initial')
