"""Added user model for authentication

Revision ID: c49b6324267d
Revises: 83e05b1696ec
Create Date: 2020-09-15 20:15:16.038009

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c49b6324267d'
down_revision = '83e05b1696ec'
branch_labels = None
depends_on = None

def upgrade():
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=True),
    sa.Column('pwhash', sa.String(length=255), nullable=True),
    sa.Column('pw_timestamp', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_user')),
    sa.UniqueConstraint('name', name=op.f('uq_user_name')),
    mysql_encrypted='yes'
    )

def downgrade():
    op.drop_table('user')
