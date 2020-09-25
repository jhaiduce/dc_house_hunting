"""Added a seen field

Revision ID: 608e8b557eac
Revises: 0a0c481f02e5
Create Date: 2020-09-25 18:41:15.994544

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '608e8b557eac'
down_revision = '0a0c481f02e5'
branch_labels = None
depends_on = None

def upgrade():
    with op.batch_alter_table('residence', schema=None) as batch_op:
        batch_op.add_column(sa.Column('seen', sa.Boolean(), nullable=True))

def downgrade():
    with op.batch_alter_table('residence', schema=None) as batch_op:
        batch_op.drop_column('seen')
