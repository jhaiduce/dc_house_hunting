"""Drop congressional_representation column

Revision ID: cdf466224f70
Revises: eab604cb1d36
Create Date: 2020-09-14 11:33:57.571377

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'cdf466224f70'
down_revision = 'eab604cb1d36'
branch_labels = None
depends_on = None

def upgrade():
    with op.batch_alter_table('residence', schema=None) as batch_op:
        batch_op.drop_column('congressional_representation')

def downgrade():
    with op.batch_alter_table('residence', schema=None) as batch_op:
        batch_op.add_column(sa.Column('congressional_representation', sa.BOOLEAN(), nullable=True))
