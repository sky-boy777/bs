"""empty message

Revision ID: 174ab37a5742
Revises: 815868588adf
Create Date: 2020-12-14 21:01:19.316903

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '174ab37a5742'
down_revision = '815868588adf'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('index_brief_introduction', 'rates')
    op.drop_column('scenic_spots', 'rates')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('scenic_spots', sa.Column('rates', mysql.VARCHAR(length=20), nullable=False))
    op.add_column('index_brief_introduction', sa.Column('rates', mysql.VARCHAR(length=20), nullable=False))
    # ### end Alembic commands ###