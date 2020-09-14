"""Changed price to numeric

Revision ID: eab604cb1d36
Revises: 7da7e6f4ab1f
Create Date: 2020-09-14 09:51:23.900983

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'eab604cb1d36'
down_revision = '7da7e6f4ab1f'
branch_labels = None
depends_on = None

def upgrade():
    with op.batch_alter_table('residence',schema=None,recreate='auto') as batch_op:
        batch_op.alter_column('price_',new_column_name='price')

def downgrade():
    with op.batch_alter_table('residence',schema=None,recreate='auto') as batch_op:
        batch_op.alter_column('price',new_column_name='price_')
