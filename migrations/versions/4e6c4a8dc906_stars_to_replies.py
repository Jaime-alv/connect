"""stars to replies

Revision ID: 4e6c4a8dc906
Revises: a34a093f55b5
Create Date: 2021-12-19 11:05:04.985314

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4e6c4a8dc906'
down_revision = 'a34a093f55b5'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('stars_reply',
    sa.Column('follower_id', sa.Integer(), nullable=True),
    sa.Column('reply_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['follower_id'], ['user.id'], ),
    sa.ForeignKeyConstraint(['reply_id'], ['reply.id'], )
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('stars_reply')
    # ### end Alembic commands ###
