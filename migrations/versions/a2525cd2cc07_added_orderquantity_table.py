"""added OrderQuantity table

Revision ID: a2525cd2cc07
Revises: b4782c137ced
Create Date: 2022-03-04 01:29:06.814418

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a2525cd2cc07'
down_revision = 'b4782c137ced'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('order_quantity',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('order_name', sa.String(length=64), nullable=True),
    sa.Column('quantity', sa.Integer(), nullable=True),
    sa.Column('profile_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['profile_id'], ['profile.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('order_quantity', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_order_quantity_order_name'), ['order_name'], unique=False)
        batch_op.create_index(batch_op.f('ix_order_quantity_quantity'), ['quantity'], unique=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('order_quantity', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_order_quantity_quantity'))
        batch_op.drop_index(batch_op.f('ix_order_quantity_order_name'))

    op.drop_table('order_quantity')
    # ### end Alembic commands ###