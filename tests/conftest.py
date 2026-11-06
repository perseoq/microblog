import os

os.environ['DATABASE_URI'] = 'sqlite:///:memory:'

import pytest

from main import app as flask_app
from blog.arch.models import User
from blog.core.extensions import db


@pytest.fixture
def app():
    flask_app.config.update(
        TESTING=True,
        WTF_CSRF_ENABLED=False,
    )
    with flask_app.app_context():
        db.create_all()
        yield flask_app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def user(app):
    user = User(username='ana', email='ana@example.com')
    user.set_password('secret123')
    db.session.add(user)
    db.session.commit()
    return user.id


@pytest.fixture
def auth_client(client, user):
    client.post('/login', data={'email': 'ana@example.com', 'password': 'secret123'})
    return client
