"""security drafts encryption

Revision ID: 9e178187db95
Revises: 710da5fe58f0
Create Date: 2026-11-06 22:31:36.920064

"""
import re

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


def _columns(bind, table):
    return {column['name']: column for column in sa.inspect(bind).get_columns(table)}


def _add_status_if_missing(bind, table):
    if 'status' in _columns(bind, table):
        return
    with op.batch_alter_table(table, schema=None) as batch_op:
        batch_op.add_column(
            sa.Column('status', sa.String(length=20), server_default='published', nullable=False)
        )


def _ensure_totp_length(bind):
    column = _columns(bind, 'user').get('totp_secret')
    if column is None:
        return
    length = getattr(column['type'], 'length', None)
    if length is not None and length < 255:
        with op.batch_alter_table('user', schema=None) as batch_op:
            batch_op.alter_column(
                'totp_secret',
                existing_type=column['type'],
                type_=sa.String(length=255),
                existing_nullable=True,
            )


def _is_decryptable(cipher, value, dialect):
    try:
        cipher.process_result_value(value, dialect)
        return True
    except Exception:
        return False


def _looks_like_totp_secret(value):
    if not isinstance(value, str):
        return False
    value = value.strip()
    return (
        16 <= len(value.rstrip('=')) <= 64
        and re.fullmatch(r'[A-Z2-7]+=*', value, re.IGNORECASE) is not None
    )


def _quoted_user(bind):
    return bind.dialect.identifier_preparer.quote_identifier('user')


def upgrade():
    bind = op.get_bind()
    _add_status_if_missing(bind, 'page')
    _add_status_if_missing(bind, 'post')
    _ensure_totp_length(bind)

    cipher = _cipher()
    quoted_user = _quoted_user(bind)
    rows = bind.execute(
        sa.text(f'SELECT id, totp_secret FROM {quoted_user} WHERE totp_secret IS NOT NULL')
    ).fetchall()
    for user_id, secret in rows:
        if not secret:
            continue
        if isinstance(secret, bytes):
            secret = secret.decode('utf-8', errors='ignore')
        if _is_decryptable(cipher, secret, bind.dialect):
            continue
        if not _looks_like_totp_secret(secret):
            continue
        encrypted = cipher.process_bind_param(secret, bind.dialect)
        bind.execute(
            sa.text(f'UPDATE {quoted_user} SET totp_secret = :secret WHERE id = :id'),
            {'secret': encrypted, 'id': user_id},
        )


def downgrade():
    bind = op.get_bind()
    cipher = _cipher()
    quoted_user = _quoted_user(bind)
    rows = bind.execute(
        sa.text(f'SELECT id, totp_secret FROM {quoted_user} WHERE totp_secret IS NOT NULL')
    ).fetchall()
    for user_id, secret in rows:
        if not secret:
            continue
        if isinstance(secret, bytes):
            secret = secret.decode('utf-8', errors='ignore')
        try:
            plain = cipher.process_result_value(secret, bind.dialect)
        except Exception:
            plain = secret
        if plain != secret:
            bind.execute(
                sa.text(f'UPDATE {quoted_user} SET totp_secret = :secret WHERE id = :id'),
                {'secret': plain, 'id': user_id},
            )

    for table in ('page', 'post'):
        if 'status' in _columns(bind, table):
            with op.batch_alter_table(table, schema=None) as batch_op:
                batch_op.drop_column('status')

    column = _columns(bind, 'user').get('totp_secret')
    length = getattr(column['type'], 'length', None) if column else None
    if length is not None and length != 32:
        with op.batch_alter_table('user', schema=None) as batch_op:
            batch_op.alter_column(
                'totp_secret',
                existing_type=column['type'],
                type_=sa.String(length=32),
                existing_nullable=True,
            )
