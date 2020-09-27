"""Deleted withdrawn column

Revision ID: 49210bf7e6ba
Revises: b06fd20a6ba3
Create Date: 2020-09-27 18:10:23.168892

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '49210bf7e6ba'
down_revision = 'b06fd20a6ba3'
branch_labels = None
depends_on = None

def upgrade():
    with op.batch_alter_table('residence', schema=None) as batch_op:
        batch_op.drop_column('withdrawn')

def downgrade():
    with op.batch_alter_table('residence', schema=None) as batch_op:
        batch_op.add_column(sa.Column('withdrawn', sa.BOOLEAN(), nullable=True))
