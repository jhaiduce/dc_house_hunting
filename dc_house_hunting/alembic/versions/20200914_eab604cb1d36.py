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

    connection = op.get_bind()

    with op.batch_alter_table('residence',schema=None,recreate='auto') as batch_op:
        batch_op.alter_column('price_',new_column_name='price',type_=sa.Numeric())

    # Divide price by 100 since we now treat the cents as a fraction
    connection.execute('update residence set price=price/100')

def downgrade():

    connection = op.get_bind()

    # Multiply by 100 so cents aren't lost to rounding in the conversion
    # to Integer
    connection.execute('update residence set price=price*100')

    with op.batch_alter_table('residence',schema=None,recreate='auto') as batch_op:
        batch_op.alter_column('price',new_column_name='price_',type_=sa.Integer())
