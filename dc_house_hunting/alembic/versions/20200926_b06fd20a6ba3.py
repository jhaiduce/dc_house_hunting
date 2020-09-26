"""Added a field for listing state

Revision ID: b06fd20a6ba3
Revises: 608e8b557eac
Create Date: 2020-09-26 09:24:39.707761

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b06fd20a6ba3'
down_revision = '608e8b557eac'
branch_labels = None
depends_on = None

def upgrade():
    op.create_table('listingstate',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=True),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_listingstate'))
    )
    with op.batch_alter_table('residence', schema=None) as batch_op:
        batch_op.add_column(sa.Column('listingstate_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key(batch_op.f('fk_residence_listingstate_id_listingstate'), 'listingstate', ['listingstate_id'], ['id'])
    
    listingstate=sa.table(
        'listingstate',
        sa.column('name',sa.String)
    )

    conn=op.get_bind()
    result = conn.execute(listingstate.insert().values(name='Active'))
    active_id=result.lastrowid
    result = conn.execute(listingstate.insert().values(name='Withdrawn'))
    withdrawn_id=result.lastrowid
    result = conn.execute(listingstate.insert().values(name='Pending'))
    pending_id=result.lastrowid
    result = conn.execute(listingstate.insert().values(name='Closed'))
    closed_id=result.lastrowid

    residence=sa.table(
        'residence',
        sa.column('listingstate_id',sa.Integer),
        sa.column('withdrawn',sa.Boolean)
    )

    result = conn.execute(
        residence.update().where(
            residence.c.withdrawn==True
        ).values(
            listingstate_id=active_id
        )
    )

def downgrade():

    listingstate=sa.table(
        'listingstate',
        sa.column('id',sa.Integer),
        sa.column('name',sa.String)
    )

    residence=sa.table(
        'residence',
        sa.column('listingstate_id',sa.Integer),
        sa.column('withdrawn',sa.Boolean)
    )

    conn=op.get_bind()

    result = conn.execute(
        sa.select([listingstate]).where(listingstate.c.name=='Withdrawn')
    )
    withdrawn_id=result.fetchone().id

    conn.execute(
        residence.update().where(
            residence.c.listingstate_id==withdrawn_id
        ).values(
            withdrawn=True
        )
    )

    with op.batch_alter_table('residence', schema=None) as batch_op:
        batch_op.drop_constraint(batch_op.f('fk_residence_listingstate_id_listingstate'), type_='foreignkey')
        batch_op.drop_column('listingstate_id')

    op.drop_table('listingstate')
