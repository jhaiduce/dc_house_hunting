"""Added parking, kitchen, and bike storage to score calculation

Revision ID: d0dbef14c17c
Revises: 59b7ab55379e
Create Date: 2020-09-23 23:20:01.533077

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd0dbef14c17c'
down_revision = '59b7ab55379e'
branch_labels = None
depends_on = None

def upgrade():
    op.create_table('idmapping',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['id'], ['weightmapping.id'], name=op.f('fk_idmapping_id_weightmapping')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_idmapping')),
    mysql_encrypted='yes'
    )
    with op.batch_alter_table('parkingtype', schema=None) as batch_op:
        batch_op.add_column(sa.Column('score', sa.Float(), nullable=True))

    with op.batch_alter_table('residence', schema=None) as batch_op:
        batch_op.add_column(sa.Column('bike_storage_score', sa.Float(), nullable=True))
        batch_op.add_column(sa.Column('kitchen_score', sa.Float(), nullable=True))

def downgrade():
    with op.batch_alter_table('residence', schema=None) as batch_op:
        batch_op.drop_column('kitchen_score')
        batch_op.drop_column('bike_storage_score')

    with op.batch_alter_table('parkingtype', schema=None) as batch_op:
        batch_op.drop_column('score')

    op.drop_table('idmapping')
