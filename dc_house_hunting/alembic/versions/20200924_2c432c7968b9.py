"""Added rejected and withdrawn fields for residences

Revision ID: 2c432c7968b9
Revises: d0dbef14c17c
Create Date: 2020-09-24 18:47:54.813184

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2c432c7968b9'
down_revision = 'd0dbef14c17c'
branch_labels = None
depends_on = None

def upgrade():
    with op.batch_alter_table('residence', schema=None) as batch_op:
        batch_op.add_column(sa.Column('rejected', sa.Boolean(), nullable=True, default=False))
        batch_op.add_column(sa.Column('withdrawn', sa.Boolean(), nullable=True, default=False))

def downgrade():
    with op.batch_alter_table('residence', schema=None) as batch_op:
        batch_op.drop_column('withdrawn')
        batch_op.drop_column('rejected')
