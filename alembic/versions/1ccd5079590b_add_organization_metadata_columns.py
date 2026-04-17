"""add_organization_metadata_columns

Revision ID: 1ccd5079590b
Revises: 7a8e9f0d1c2b
Create Date: 2026-04-17 10:33:36.063424

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1ccd5079590b'
down_revision: Union[str, Sequence[str], None] = '7a8e9f0d1c2b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Add columns as nullable first
    op.add_column('organizations', sa.Column('slug', sa.String(), nullable=True))
    op.add_column('organizations', sa.Column('website_url', sa.String(), nullable=True))
    op.add_column('organizations', sa.Column('industry', sa.String(), nullable=True))
    op.add_column('organizations', sa.Column('company_size', sa.String(), nullable=True))
    
    # 2. Add index for slug
    op.create_index(op.f('ix_organizations_slug'), 'organizations', ['slug'], unique=True)
    
    # 3. Populate slug for existing data
    # Simple SQL logic to generate a slug from name if not present
    op.execute("UPDATE organizations SET slug = LOWER(REPLACE(name, ' ', '-')) WHERE slug IS NULL")
    
    # 4. Set slug to NOT NULL
    op.alter_column('organizations', 'slug', nullable=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_organizations_slug'), table_name='organizations')
    op.drop_column('organizations', 'company_size')
    op.drop_column('organizations', 'industry')
    op.drop_column('organizations', 'website_url')
    op.drop_column('organizations', 'slug')
