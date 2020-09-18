"""Added lotsize column

Revision ID: 512e0cb171d5
Revises: 6422efa3d28a
Create Date: 2020-09-17 21:38:01.003784

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '512e0cb171d5'
down_revision = '6422efa3d28a'
branch_labels = None
depends_on = None

def upgrade():
    with op.batch_alter_table('residence', schema=None) as batch_op:
        batch_op.add_column(sa.Column('lotsize', sa.Float(), nullable=True))


def downgrade():
    with op.batch_alter_table('residence', schema=None) as batch_op:
        batch_op.drop_column('lotsize')

