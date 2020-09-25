"""empty message

Revision ID: 0a0c481f02e5
Revises: 2c432c7968b9
Create Date: 2020-09-25 06:48:18.392188

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0a0c481f02e5'
down_revision = '2c432c7968b9'
branch_labels = None
depends_on = None

def upgrade():
    with op.batch_alter_table('residence', schema=None) as batch_op:
        batch_op.add_column(sa.Column('insurance', sa.Numeric(), nullable=True))
        batch_op.add_column(sa.Column('mortgage', sa.Numeric(), nullable=True))
        batch_op.add_column(sa.Column('taxes_computed', sa.Numeric(), nullable=True))

def downgrade():
    with op.batch_alter_table('residence', schema=None) as batch_op:
        batch_op.drop_column('taxes_computed')
        batch_op.drop_column('mortgage')
        batch_op.drop_column('insurance')
