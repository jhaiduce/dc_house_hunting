"""Added half-bath and URL columns

Revision ID: 6422efa3d28a
Revises: 1ec0444917d1
Create Date: 2020-09-17 13:04:12.737781

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6422efa3d28a'
down_revision = '1ec0444917d1'
branch_labels = None
depends_on = None

def upgrade():
    with op.batch_alter_table('residence', schema=None) as batch_op:
        batch_op.add_column(sa.Column('half_bathrooms', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('url', sa.Text(), nullable=True))

def downgrade():
    with op.batch_alter_table('residence', schema=None) as batch_op:
        batch_op.drop_column('url')
        batch_op.drop_column('half_bathrooms')
