import pyotp

from blog.arch.models import User
from blog.core.extensions import db


def _enable_totp(user_id):
    user = db.session.get(User, user_id)
    secret = pyotp.random_base32()
    user.totp_secret = secret
    user.totp_enabled = True
    db.session.commit()
    return secret


def test_login_requires_totp(client, user):
    _enable_totp(user)
    response = client.post('/login', data={
        'email': 'ana@example.com',
        'password': 'secret123',
    }, follow_redirects=False)
    assert response.status_code == 302
    assert '/login/2fa' in response.headers['Location']
    assert client.get('/admin/').status_code == 302


def test_totp_login_success(client, user):
    secret = _enable_totp(user)
    client.post('/login', data={'email': 'ana@example.com', 'password': 'secret123'}, follow_redirects=False)
    code = pyotp.TOTP(secret).now()
    response = client.post('/login/2fa', data={'code': code}, follow_redirects=False)
    assert response.status_code == 302
    assert client.get('/admin/').status_code == 200


def test_totp_login_invalid_code(client, user):
    _enable_totp(user)
    client.post('/login', data={'email': 'ana@example.com', 'password': 'secret123'}, follow_redirects=False)
    response = client.post('/login/2fa', data={'code': '000000'}, follow_redirects=True)
    assert 'inválido'.encode('utf-8') in response.data
    assert client.get('/admin/').status_code == 302


def test_totp_setup_and_disable(auth_client, user):
    response = auth_client.get('/admin/profile/2fa')
    assert response.status_code == 200
    assert b'data:image/svg+xml' in response.data

    with auth_client.session_transaction() as session:
        secret = session['totp_setup_secret']

    code = pyotp.TOTP(secret).now()
    response = auth_client.post('/admin/profile/2fa', data={'code': code}, follow_redirects=False)
    assert response.status_code == 302
    user_obj = db.session.get(User, user)
    assert user_obj.totp_enabled is True
    assert user_obj.totp_secret == secret

    code = pyotp.TOTP(secret).now()
    response = auth_client.post('/admin/profile/2fa/disable', data={
        'password': 'secret123',
        'code': code,
    }, follow_redirects=False)
    assert response.status_code == 302
    user_obj = db.session.get(User, user)
    assert user_obj.totp_enabled is False
    assert user_obj.totp_secret is None


def test_totp_setup_requires_login(client):
    assert client.get('/admin/profile/2fa').status_code == 302


def test_verify_without_pending_session(client):
    response = client.get('/login/2fa', follow_redirects=False)
    assert response.status_code == 302
