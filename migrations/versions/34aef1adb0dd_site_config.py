"""site config

Revision ID: 34aef1adb0dd
Revises: 0cc0f3a789b4
Create Date: 2026-11-06 21:22:40.682944

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '34aef1adb0dd'
down_revision = '0cc0f3a789b4'
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    if sa.inspect(bind).has_table('site_config'):
        return
    op.create_table('site_config',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('site_title', sa.String(length=100), nullable=False),
    sa.Column('site_description', sa.Text(), nullable=False),
    sa.Column('footer_text', sa.String(length=200), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    bind = op.get_bind()
    if sa.inspect(bind).has_table('site_config'):
        op.drop_table('site_config')
