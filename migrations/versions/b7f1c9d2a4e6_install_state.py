"""install state

Revision ID: b7f1c9d2a4e6
Revises: 9e178187db95
Create Date: 2026-11-07 06:40:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b7f1c9d2a4e6'
down_revision = '9e178187db95'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'install_state',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )


def downgrade():
    op.drop_table('install_state')
