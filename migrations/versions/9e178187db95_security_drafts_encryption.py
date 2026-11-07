"""security drafts encryption

Revision ID: 9e178187db95
Revises: 710da5fe58f0
Create Date: 2026-11-06 22:31:36.920064

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy_utils import StringEncryptedType
from sqlalchemy_utils.types.encrypted.encrypted_type import AesEngine

from blog.core.enviroment import SECRET_KEY


# revision identifiers, used by Alembic.
revision = '9e178187db95'
down_revision = '710da5fe58f0'
branch_labels = None
depends_on = None


def _cipher():
    return StringEncryptedType(sa.String(255), SECRET_KEY, AesEngine, 'pkcs5')


def upgrade():
    with op.batch_alter_table('page', schema=None) as batch_op:
        batch_op.add_column(sa.Column('status', sa.String(length=20), server_default='published', nullable=False))

    with op.batch_alter_table('post', schema=None) as batch_op:
        batch_op.add_column(sa.Column('status', sa.String(length=20), server_default='published', nullable=False))

    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.alter_column(
            'totp_secret',
            existing_type=sa.String(length=32),
            type_=sa.String(length=255),
            existing_nullable=True,
        )

    bind = op.get_bind()
    cipher = _cipher()
    rows = bind.execute(sa.text('SELECT id, totp_secret FROM "user" WHERE totp_secret IS NOT NULL')).fetchall()
    for user_id, secret in rows:
        if not secret:
            continue
        encrypted = cipher.process_bind_param(secret, bind.dialect)
        bind.execute(
            sa.text('UPDATE "user" SET totp_secret = :secret WHERE id = :id'),
            {'secret': encrypted, 'id': user_id},
        )


def downgrade():
    bind = op.get_bind()
    cipher = _cipher()
    rows = bind.execute(sa.text('SELECT id, totp_secret FROM "user" WHERE totp_secret IS NOT NULL')).fetchall()
    for user_id, secret in rows:
        if not secret:
            continue
        try:
            plain = cipher.process_result_value(secret, bind.dialect)
        except Exception:
            plain = secret
        bind.execute(
            sa.text('UPDATE "user" SET totp_secret = :secret WHERE id = :id'),
            {'secret': plain, 'id': user_id},
        )

    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.alter_column(
            'totp_secret',
            existing_type=sa.String(length=255),
            type_=sa.String(length=32),
            existing_nullable=True,
        )

    with op.batch_alter_table('post', schema=None) as batch_op:
        batch_op.drop_column('status')

    with op.batch_alter_table('page', schema=None) as batch_op:
        batch_op.drop_column('status')
