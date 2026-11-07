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
        'status': 'published',
    }, follow_redirects=False)
    assert response.status_code == 302
    post = Post.query.filter_by(title='Nuevo').first()
    assert post is not None

    response = auth_client.post(f'/admin/posts/{post.id}/edit', data={
        'title': 'Editado',
        'content': 'Cuerpo 2',
        'category': str(category),
        'tags': [],
        'status': 'published',
    }, follow_redirects=False)
    assert response.status_code == 302
    assert db.session.get(Post, post.id).title == 'Editado'

    response = auth_client.post(f'/admin/posts/{post.id}/delete', follow_redirects=False)
    assert response.status_code == 302
    assert db.session.get(Post, post.id) is None


def test_post_draft_and_inline_tags(auth_client, category):
    response = auth_client.post('/admin/posts/new', data={
        'title': 'Borrador',
        'content': 'Cuerpo',
        'category': str(category),
        'tags': [],
        'new_tags': 'flask, nuevo',
        'status': 'draft',
    }, follow_redirects=False)
    assert response.status_code == 302

    post = Post.query.filter_by(title='Borrador').first()
    assert post is not None
    assert post.status == 'draft'
    assert {tag.name for tag in post.tags} == {'flask', 'nuevo'}
    assert b'Borrador' not in auth_client.get('/').data
    assert b'Borrador' in auth_client.get('/admin/posts').data


def test_page_crud(auth_client):
    auth_client.post('/admin/pages/new', data={
        'title': 'Pagina',
        'content': 'x',
        'status': 'published',
    }, follow_redirects=False)
    page = Page.query.filter_by(title='Pagina').first()
    assert page is not None

    auth_client.post(f'/admin/pages/{page.id}/edit', data={
        'title': 'Pagina 2',
        'content': 'y',
        'status': 'published',
    }, follow_redirects=False)
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


def test_site_config_requires_login(client):
    assert client.get('/admin/configuracion').status_code == 302


def test_site_config_update(auth_client):
    assert auth_client.get('/admin/configuracion').status_code == 200

    response = auth_client.post('/admin/configuracion', data={
        'site_title': 'Mi Blog',
        'site_description': 'Otra descripción',
        'footer_text': '© Mi Blog',
    }, follow_redirects=False)
    assert response.status_code == 302

    home = auth_client.get('/')
    assert b'Mi Blog' in home.data
    assert 'Otra descripción'.encode('utf-8') in home.data
    assert '© Mi Blog'.encode('utf-8') in home.data


def test_themes_page_and_apply(auth_client):
    page = auth_client.get('/admin/themes')
    assert page.status_code == 200
    assert b'name="theme"' in page.data
    assert b'Aplicar tema' not in page.data

    response = auth_client.post('/admin/themes', data={'theme': 'dracula'}, follow_redirects=False)
    assert response.status_code == 302

    home = auth_client.get('/')
    assert b'data-theme-style="dracula"' in home.data


def test_settings_update_env(auth_client, app, tmp_path):
    env_file = tmp_path / '.env'
    env_file.write_text(
        'DEBUG=True\n'
        'SECRET_KEY=oldsecretoldsecret\n'
        'DATABASE_URI=sqlite:///old.db\n'
        'MAIL_PORT=587\n'
        'MAIL_PASSWORD=oldpass\n'
    )
    app.config['ENV_FILE'] = str(env_file)

    response = auth_client.get('/admin/settings')
    assert response.status_code == 200
    assert 'Guardar configuración'.encode('utf-8') in response.data

    response = auth_client.post('/admin/settings', data={
        'debug': 'y',
        'database_uri': 'sqlite:///new.db',
        'mail_server': 'smtp.example.com',
        'mail_port': '2525',
        'mail_username': 'user@example.com',
        'mail_password': '',
        'mail_use_tls': 'y',
        'mail_default_sender': 'user@example.com',
    }, follow_redirects=False)
    assert response.status_code == 302

    content = env_file.read_text()
    assert "DEBUG='True'" in content
    assert "DATABASE_URI='sqlite:///new.db'" in content
    assert "MAIL_PORT='2525'" in content
    assert "MAIL_USE_SSL='False'" in content
    assert 'SECRET_KEY=oldsecretoldsecret' in content
    assert 'MAIL_PASSWORD=oldpass' in content
