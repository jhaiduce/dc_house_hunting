"""Added more columns/tables of information to support decision-making

Revision ID: 7da7e6f4ab1f
Revises: ef57d275dd92
Create Date: 2020-09-14 07:53:30.222341

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7da7e6f4ab1f'
down_revision = 'ef57d275dd92'
branch_labels = None
depends_on = None

def upgrade():
    op.create_table('foodsourcetype',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_foodsourcetype'))
    )
    op.create_table('foodsource',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=True),
    sa.Column('location_id', sa.Integer(), nullable=True),
    sa.Column('foodsourcetype_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['foodsourcetype_id'], ['foodsourcetype.id'], name=op.f('fk_foodsource_foodsourcetype_id_foodsourcetype')),
    sa.ForeignKeyConstraint(['location_id'], ['location.id'], name=op.f('fk_foodsource_location_id_location')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_foodsource')),
    mysql_encrypted='yes'
    )
    op.create_table('park',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('location_id', sa.Integer(), nullable=True),
    sa.Column('playground', sa.Boolean(), nullable=True),
    sa.Column('trees', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['location_id'], ['location.id'], name=op.f('fk_park_location_id_location')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_park')),
    mysql_encrypted='yes'
    )

    with op.batch_alter_table('residence',schema=None,recreate='auto') as batch_op:
        batch_op.add_column(sa.Column('air_drying_clothes', sa.Boolean(), nullable=True))
        batch_op.add_column(sa.Column('attic', sa.Boolean(), nullable=True))
        batch_op.add_column(sa.Column('bicycle_storage', sa.Boolean(), nullable=True))
        batch_op.add_column(sa.Column('congressional_representation', sa.Boolean(), nullable=True))
        batch_op.add_column(sa.Column('interracial_neighborhood', sa.Boolean(), nullable=True))
        batch_op.add_column(sa.Column('kitchen_cabinet_space', sa.Float(), nullable=True))
        batch_op.add_column(sa.Column('kitchen_counter_space', sa.Float(), nullable=True))

    with op.batch_alter_table('school',schema=None,recreate='auto') as batch_op:
        batch_op.add_column(sa.Column('class_size', sa.Float(), nullable=True))
        batch_op.add_column(sa.Column('highest_grade', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('lowest_grade', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('name', sa.String(), nullable=True))

def downgrade():
    with op.batch_alter_table('school',schema=None,recreate='auto') as batch_op:
        batch_op.drop_column('name')
        batch_op.drop_column('lowest_grade')
        batch_op.drop_column('highest_grade')
        batch_op.drop_column('class_size')

    with op.batch_alter_table('residence',schema=None,recreate='auto') as batch_op:
        batch_op.drop_column('kitchen_counter_space')
        batch_op.drop_column('kitchen_cabinet_space')
        batch_op.drop_column('interracial_neighborhood')
        batch_op.drop_column('congressional_representation')
        batch_op.drop_column('bicycle_storage')
        batch_op.drop_column('attic')
        batch_op.drop_column('air_drying_clothes')

    op.drop_table('park')
    op.drop_table('foodsource')
    op.drop_table('foodsourcetype')
