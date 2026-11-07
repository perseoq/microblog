"""2fa totp

Revision ID: 0cc0f3a789b4
Revises: 3572661ab018
Create Date: 2026-11-06 18:26:55.242207

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0cc0f3a789b4'
down_revision = '3572661ab018'
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    columns = {column['name'] for column in sa.inspect(bind).get_columns('user')}
    if 'totp_secret' in columns and 'totp_enabled' in columns:
        return
    with op.batch_alter_table('user', schema=None) as batch_op:
        if 'totp_secret' not in columns:
            batch_op.add_column(sa.Column('totp_secret', sa.String(length=32), nullable=True))
        if 'totp_enabled' not in columns:
            batch_op.add_column(
                sa.Column('totp_enabled', sa.Boolean(), server_default=sa.false(), nullable=False)
            )


def downgrade():
    bind = op.get_bind()
    columns = {column['name'] for column in sa.inspect(bind).get_columns('user')}
    with op.batch_alter_table('user', schema=None) as batch_op:
        if 'totp_enabled' in columns:
            batch_op.drop_column('totp_enabled')
        if 'totp_secret' in columns:
            batch_op.drop_column('totp_secret')
