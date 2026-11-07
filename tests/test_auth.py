from itsdangerous import URLSafeTimedSerializer

from blog.arch.models import User


def test_install_creates_admin(client):
    response = client.post('/install', data={
        'username': 'admin',
        'email': 'admin@example.com',
        'password': 'secret123',
        'confirm': 'secret123',
    }, follow_redirects=False)
    assert response.status_code == 302
    user = User.query.filter_by(email='admin@example.com').first()
    assert user is not None
    assert user.check_password('secret123')


def test_install_blocked_when_user_exists(client, user):
    response = client.get('/install', follow_redirects=False)
    assert response.status_code == 302


def test_login_rejects_wrong_password(client, user):
    response = client.post('/login', data={'email': 'ana@example.com', 'password': 'bad'})
    assert response.status_code == 200
    assert b'Iniciar' in response.data


def test_login_and_logout(client, user):
    response = client.post('/login', data={
        'email': 'ana@example.com',
        'password': 'secret123',
    }, follow_redirects=False)
    assert response.status_code == 302
    assert response.headers['Location'].endswith('/admin/')
    response = client.get('/logout', follow_redirects=False)
    assert response.status_code == 302


def test_authenticated_blog_shows_admin_links(auth_client):
    home = auth_client.get('/')
    assert home.status_code == 200
    assert b'/admin/' in home.data
    assert b'/admin/galleries' in home.data


def test_password_reset(client, app, user):
    user_obj = User.query.filter_by(email='ana@example.com').first()
    token = URLSafeTimedSerializer(app.config['SECRET_KEY'], salt='password-reset').dumps({
        'email': 'ana@example.com',
        'pwd': user_obj.password_hash,
    })
    response = client.get(f'/recover/{token}')
    assert response.status_code == 200
    response = client.post(f'/recover/{token}', data={
        'password': 'newsecret1',
        'confirm': 'newsecret1',
    }, follow_redirects=False)
    assert response.status_code == 302
    user = User.query.filter_by(email='ana@example.com').first()
    assert user.check_password('newsecret1')


def test_reset_token_is_single_use(client, app, user):
    user_obj = User.query.filter_by(email='ana@example.com').first()
    token = URLSafeTimedSerializer(app.config['SECRET_KEY'], salt='password-reset').dumps({
        'email': 'ana@example.com',
        'pwd': user_obj.password_hash,
    })
    client.post(f'/recover/{token}', data={
        'password': 'newsecret1',
        'confirm': 'newsecret1',
    }, follow_redirects=False)

    response = client.post(f'/recover/{token}', data={
        'password': 'another1',
        'confirm': 'another1',
    }, follow_redirects=False)
    assert response.status_code == 302
    user = User.query.filter_by(email='ana@example.com').first()
    assert user.check_password('newsecret1')
    assert not user.check_password('another1')


def test_invalid_reset_token(client, user):
    response = client.get('/recover/token-invalido', follow_redirects=False)
    assert response.status_code == 302


def test_recover_sends_email(client, user, monkeypatch):
    sent = {}

    def fake_send_message(subject, recipients, body):
        sent['subject'] = subject
        sent['recipients'] = recipients
        sent['body'] = body

    monkeypatch.setattr('blog.views.auth.mail.send_message', fake_send_message)
    response = client.post('/recover', data={'email': 'ana@example.com'}, follow_redirects=False)
    assert response.status_code == 302
    assert sent['recipients'] == ['ana@example.com']
    assert '/recover/' in sent['body']


def test_recover_unknown_email_does_not_send(client, user, monkeypatch):
    calls = []
    monkeypatch.setattr('blog.views.auth.mail.send_message', lambda *a, **k: calls.append(1))
    response = client.post('/recover', data={'email': 'nadie@example.com'}, follow_redirects=False)
    assert response.status_code == 302
    assert calls == []


def test_login_rate_limited(client, user):
    for _ in range(10):
        client.post('/login', data={'email': 'ana@example.com', 'password': 'bad'})

    response = client.post('/login', data={'email': 'ana@example.com', 'password': 'bad'})
    assert response.status_code == 429
    assert response.headers['Retry-After'] == '300'
