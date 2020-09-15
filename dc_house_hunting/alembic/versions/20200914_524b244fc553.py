"""Added Co-op, HOA fee, and taxes columns

Revision ID: 524b244fc553
Revises: cdf466224f70
Create Date: 2020-09-14 20:28:16.845356

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '524b244fc553'
down_revision = 'cdf466224f70'
branch_labels = None
depends_on = None

def upgrade():
    with op.batch_alter_table('residence', schema=None) as batch_op:
        batch_op.add_column(sa.Column('coop', sa.Boolean(), nullable=True))
        batch_op.add_column(sa.Column('hoa_fee', sa.Numeric(), nullable=True))
        batch_op.add_column(sa.Column('taxes', sa.Numeric(), nullable=True))

def downgrade():
    with op.batch_alter_table('residence', schema=None) as batch_op:
        batch_op.drop_column('taxes')
        batch_op.drop_column('hoa_fee')
        batch_op.drop_column('coop')
