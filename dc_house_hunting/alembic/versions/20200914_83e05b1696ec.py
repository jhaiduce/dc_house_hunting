"""Added laundry line-drying field

Revision ID: 83e05b1696ec
Revises: 524b244fc553
Create Date: 2020-09-14 20:45:27.114047

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '83e05b1696ec'
down_revision = '524b244fc553'
branch_labels = None
depends_on = None

def upgrade():
    with op.batch_alter_table('residence', schema=None) as batch_op:
        batch_op.add_column(sa.Column('laundry_hang_drying', sa.Boolean(), nullable=True))

def downgrade():
    with op.batch_alter_table('residence', schema=None) as batch_op:
        batch_op.drop_column('laundry_hang_drying')
