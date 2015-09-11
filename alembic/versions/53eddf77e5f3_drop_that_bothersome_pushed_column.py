"""Drop that bothersome pushed column.

Revision ID: 53eddf77e5f3
Revises: 70a58ae9f90
Create Date: 2015-09-11 15:11:10.795968

"""

# revision identifiers, used by Alembic.
revision = '53eddf77e5f3'
down_revision = '70a58ae9f90'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.drop_column('updates', 'pushed')


def downgrade():
    op.add_column('updates', sa.Column('pushed', sa.Boolean(), default=False))
