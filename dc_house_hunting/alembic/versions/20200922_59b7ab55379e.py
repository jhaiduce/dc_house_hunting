"""Added a column for the computed score

Revision ID: 59b7ab55379e
Revises: 17b951b89df7
Create Date: 2020-09-22 17:35:22.666239

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '59b7ab55379e'
down_revision = '17b951b89df7'
branch_labels = None
depends_on = None

def upgrade():

    with op.batch_alter_table('residence', schema=None) as batch_op:
        batch_op.add_column(sa.Column('score_', sa.Float(), nullable=True))

def downgrade():

    with op.batch_alter_table('residence', schema=None) as batch_op:
        batch_op.drop_column('score_')
