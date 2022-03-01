"""empty message

Revision ID: 85e6eb64ea3e
Revises: 8608ae49024e
Create Date: 2022-02-06 02:44:49.810901

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '85e6eb64ea3e'
down_revision = '8608ae49024e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('fumos',
    sa.Column('profile_id', sa.Integer(), nullable=True),
    sa.Column('fumo_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['fumo_id'], ['fumo.id'], ),
    sa.ForeignKeyConstraint(['profile_id'], ['profile.id'], )
    )
    with op.batch_alter_table('fumo', schema=None) as batch_op:
        batch_op.drop_column('desc')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('fumo', schema=None) as batch_op:
        batch_op.add_column(sa.Column('desc', sa.TEXT(length=250), nullable=True))

    op.drop_table('fumos')
    # ### end Alembic commands ###
