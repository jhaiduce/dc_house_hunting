"""Add basic database models

Revision ID: ef57d275dd92
Revises: 
Create Date: 2020-09-13 19:26:30.421576

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ef57d275dd92'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table('location',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('street_address', sa.String(), nullable=True),
    sa.Column('city', sa.String(), nullable=True),
    sa.Column('state', sa.String(length=2), nullable=True),
    sa.Column('postal_code', sa.String(length=5), nullable=True),
    sa.Column('lat', sa.Float(), nullable=True),
    sa.Column('lon', sa.Float(), nullable=True),
    sa.Column('elevation', sa.Float(), nullable=True),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_location')),
    mysql_encrypted='yes'
    )
    op.create_table('parkingtype',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_parkingtype'))
    )
    op.create_table('residencetype',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_residencetype'))
    )
    op.create_table('residence',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('location_id', sa.Integer(), nullable=True),
    sa.Column('residencetype_id', sa.Integer(), nullable=True),
    sa.Column('parkingtype_id', sa.Integer(), nullable=True),
    sa.Column('bedrooms', sa.Integer(), nullable=True),
    sa.Column('bathrooms', sa.Integer(), nullable=True),
    sa.Column('area', sa.Float(), nullable=True),
    sa.Column('laundry', sa.Boolean(), nullable=True),
    sa.Column('basement', sa.Boolean(), nullable=True),
    sa.Column('price_', sa.Integer(), nullable=True),
    sa.Column('notes', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['location_id'], ['location.id'], name='fk_residence_location_id'),
    sa.ForeignKeyConstraint(['parkingtype_id'], ['parkingtype.id'], name='fk_residence_parkingtype_id'),
    sa.ForeignKeyConstraint(['residencetype_id'], ['residencetype.id'], name='fk_residence_residencetype_id'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_residence')),
    mysql_encrypted='yes'
    )
    op.create_table('school',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('location_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['location_id'], ['location.id'], name='fk_school_location_id'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_school')),
    mysql_encrypted='yes'
    )

def downgrade():
    op.drop_table('school')
    op.drop_table('residence')
    op.drop_table('residencetype')
    op.drop_table('parkingtype')
    op.drop_table('location')
