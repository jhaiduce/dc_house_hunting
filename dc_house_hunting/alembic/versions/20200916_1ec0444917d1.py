"""Change notes type to Text

Revision ID: 1ec0444917d1
Revises: c49b6324267d
Create Date: 2020-09-16 14:28:39.023186

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1ec0444917d1'
down_revision = 'c49b6324267d'
branch_labels = None
depends_on = None

def upgrade():

    with op.batch_alter_table('residence', schema=None) as batch_op:
        batch_op.alter_column('notes',
               existing_type=sa.String(length=255),
               type_=sa.Text(),
               existing_nullable=True)

def downgrade():

    with op.batch_alter_table('residence', schema=None) as batch_op:
        batch_op.alter_column('notes',
               existing_type=sa.Text(),
               type_=sa.String(length=255),
               existing_nullable=True)
