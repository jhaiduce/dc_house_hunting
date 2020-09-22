"""Added tables for weight factors and mappings

Revision ID: 17b951b89df7
Revises: 512e0cb171d5
Create Date: 2020-09-21 00:00:18.678632

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '17b951b89df7'
down_revision = '512e0cb171d5'
branch_labels = None
depends_on = None

def upgrade():
    op.create_table('weightfactor',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('weight', sa.Float(), default=1, nullable=False),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_weightfactor')),
    sa.UniqueConstraint('name', name=op.f('uq_weightfactor_name')),
    mysql_encrypted='yes'
    )
    op.create_table('weightmapping',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('kind', sa.String(length=255), nullable=False),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_weightmapping')),
    sa.UniqueConstraint('name', name=op.f('uq_weightmapping_name')),
    mysql_encrypted='yes'
    )
    op.create_table('factormapping',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('factor', sa.Float(), default=1, nullable=False),
    sa.ForeignKeyConstraint(['id'], ['weightmapping.id'], name=op.f('fk_factormapping_id_weightmapping')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_factormapping'))
    )
    op.create_table('smoothstepmapping',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('lower', sa.Float(), default=0, nullable=False),
    sa.Column('upper', sa.Float(), default=1, nullable=False),
    sa.ForeignKeyConstraint(['id'], ['weightmapping.id'], name=op.f('fk_smoothstepmapping_id_weightmapping')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_smoothstepmapping'))
    )

def downgrade():
    op.drop_table('smoothstepmapping')
    op.drop_table('factormapping')
    op.drop_table('weightmapping')
    op.drop_table('weightfactor')
