"""add last_name and email to user

Revision ID: bec5fe3d3007
Revises: 
Create Date: 2025-05-31 02:43:55.916825

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bec5fe3d3007'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('users', sa.Column('email', sa.String(), nullable=True))
    op.add_column('users', sa.Column('last_name', sa.String(), nullable=True))

def downgrade():
    op.drop_column('users', 'email')
    op.drop_column('users', 'last_name')
