import pytest

from blog.arch.models import Category, Page, Post, Tag, User
from blog.core.extensions import db


@pytest.fixture
def category(app):
    category = Category(name='Python')
    db.session.add(category)
    db.session.commit()
    return category.id


def test_admin_requires_login(client):
    assert client.get('/admin/').status_code == 302


def test_dashboard(auth_client):
    response = auth_client.get('/admin/')
    assert response.status_code == 200
    assert b'Panel' in response.data


def test_post_crud(auth_client, category):
    response = auth_client.post('/admin/posts/new', data={
        'title': 'Nuevo',
        'content': 'Cuerpo',
        'category': str(category),
        'tags': [],
    }, follow_redirects=False)
    assert response.status_code == 302
    post = Post.query.filter_by(title='Nuevo').first()
    assert post is not None

    response = auth_client.post(f'/admin/posts/{post.id}/edit', data={
        'title': 'Editado',
        'content': 'Cuerpo 2',
        'category': str(category),
        'tags': [],
    }, follow_redirects=False)
    assert response.status_code == 302
    assert db.session.get(Post, post.id).title == 'Editado'

    response = auth_client.post(f'/admin/posts/{post.id}/delete', follow_redirects=False)
    assert response.status_code == 302
    assert db.session.get(Post, post.id) is None


def test_page_crud(auth_client):
    auth_client.post('/admin/pages/new', data={'title': 'Pagina', 'content': 'x'}, follow_redirects=False)
    page = Page.query.filter_by(title='Pagina').first()
    assert page is not None

    auth_client.post(f'/admin/pages/{page.id}/edit', data={'title': 'Pagina 2', 'content': 'y'}, follow_redirects=False)
    assert db.session.get(Page, page.id).title == 'Pagina 2'

    auth_client.post(f'/admin/pages/{page.id}/delete', follow_redirects=False)
    assert db.session.get(Page, page.id) is None


def test_categories_and_tags(auth_client):
    auth_client.post('/admin/categories', data={'name': 'Nueva'}, follow_redirects=False)
    category = Category.query.filter_by(name='Nueva').first()
    assert category is not None

    auth_client.post('/admin/categories', data={'name': 'Nueva'}, follow_redirects=False)
    assert Category.query.filter_by(name='Nueva').count() == 1

    auth_client.post(f'/admin/categories/{category.id}/delete', follow_redirects=False)
    assert Category.query.filter_by(name='Nueva').first() is None

    auth_client.post('/admin/tags', data={'name': 'nueva'}, follow_redirects=False)
    tag = Tag.query.filter_by(name='nueva').first()
    assert tag is not None

    auth_client.post(f'/admin/tags/{tag.id}/delete', follow_redirects=False)
    assert Tag.query.filter_by(name='nueva').first() is None


def test_lists_render_icon_delete(auth_client):
    auth_client.post('/admin/categories', data={'name': 'IconCat'}, follow_redirects=False)
    auth_client.post('/admin/tags', data={'name': 'IconTag'}, follow_redirects=False)

    categories = auth_client.get('/admin/categories')
    assert categories.status_code == 200
    assert 'Eliminar categoría IconCat'.encode('utf-8') in categories.data

    tags = auth_client.get('/admin/tags')
    assert tags.status_code == 200
    assert 'Eliminar etiqueta IconTag'.encode('utf-8') in tags.data


def test_profile_and_password(auth_client, user):
    response = auth_client.post('/admin/profile', data={
        'username': 'ana2',
        'email': 'ana2@example.com',
    }, follow_redirects=False)
    assert response.status_code == 302
    assert db.session.get(User, user).username == 'ana2'

    response = auth_client.post('/admin/profile/password', data={
        'current_password': 'wrong',
        'new_password': 'newpass123',
        'confirm': 'newpass123',
    }, follow_redirects=True)
    assert b'no es correcta' in response.data

    response = auth_client.post('/admin/profile/password', data={
        'current_password': 'secret123',
        'new_password': 'newpass123',
        'confirm': 'newpass123',
    }, follow_redirects=True)
    assert b'actualizada' in response.data
    assert db.session.get(User, user).check_password('newpass123')
