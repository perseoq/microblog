import pytest

from blog.arch.models import Category, Comment, Page, Post, PostTags, Tag
from blog.core.extensions import db


@pytest.fixture
def content(app, user):
    category = Category(name='Python')
    tag = Tag(name='flask')
    db.session.add_all([category, tag])
    db.session.commit()

    post = Post(title='Hola Flask', content='Contenido sobre flask', category_id=category.id, user_id=user)
    page = Page(title='Acerca', content='Sobre el blog', user_id=user)
    db.session.add_all([post, page])
    db.session.commit()

    db.session.add(PostTags(post_id=post.id, tag_id=tag.id))
    db.session.add(Comment(content='Buen post', post_id=post.id, user_id=user))
    db.session.commit()

    return {'post': post.id, 'page': page.id, 'category': category.id, 'tag': tag.id}


def test_home_lists_post(client, content):
    response = client.get('/')
    assert response.status_code == 200
    assert b'Hola Flask' in response.data
    assert b'home-hero' in response.data
    assert b'featured-post' in response.data
    assert b'site-sidebar' in response.data
    assert 'Categorías'.encode('utf-8') in response.data
    assert b'footer-login' in response.data


def test_taxonomy_index_pages(client, content):
    categories = client.get('/categories')
    assert categories.status_code == 200
    assert b'Python' in categories.data

    pages = client.get('/pages')
    assert pages.status_code == 200
    assert b'Acerca' in pages.data


def test_search(client, content):
    assert b'Hola Flask' in client.get('/search?q=flask').data
    assert b'Sin resultados' in client.get('/search?q=nada').data


def test_search_suggestions(client, content):
    response = client.get('/search/suggest?q=Hola')
    assert response.status_code == 200
    assert 'Hola Flask' in response.get_json()
    assert client.get('/search/suggest?q=H').get_json() == []


def test_untrusted_host_rejected(client):
    response = client.get('/', headers={'Host': 'evil.example'})
    assert response.status_code == 400


def test_theme_css(client):
    response = client.get('/theme.css')
    assert response.status_code == 200
    assert b'data-theme-style="dracula"' in response.data


def test_sanitizer_allows_media_embeds(app):
    sanitize = app.jinja_env.filters['safe_html']

    youtube = str(sanitize('<iframe src="https://www.youtube.com/embed/abc123" allowfullscreen></iframe>'))
    assert '<iframe' in youtube
    assert 'youtube.com/embed/abc123' in youtube

    spotify = str(sanitize('<iframe src="https://open.spotify.com/embed/track/xyz"></iframe>'))
    assert 'open.spotify.com' not in spotify

    instagram = str(sanitize('<iframe src="https://www.instagram.com/p/abc/embed"></iframe>'))
    assert 'instagram.com' not in instagram

    vimeo = str(sanitize('<iframe src="https://player.vimeo.com/video/123"></iframe>'))
    assert 'player.vimeo.com' not in vimeo

    blocked = str(sanitize('<iframe src="https://evil.example.com/embed"></iframe>'))
    assert 'evil.example.com' not in blocked

    script = str(sanitize('<script>alert(1)</script>'))
    assert '<script>' not in script


def test_sanitizer_allows_safe_inline_styles(app):
    sanitize = app.jinja_env.filters['safe_html']

    styled = str(sanitize('<p style="text-align: center; color: #ff0000; font-size: 18px;">Hola</p>'))
    assert 'text-align: center' in styled
    assert '#ff0000' in styled
    assert 'font-size: 18px' in styled

    font_tag = str(sanitize('<font color="#00ff00" face="Arial" size="4">Hola</font>'))
    assert '<font' in font_tag
    assert '#00ff00' in font_tag

    risky = str(sanitize('<p style="position: fixed; color: red;">x</p>'))
    assert 'position' not in risky


def test_category_and_tag_filters(client, content):
    assert client.get(f"/category/{content['category']}").status_code == 200
    assert client.get(f"/tag/{content['tag']}").status_code == 200
    assert client.get('/category/9999').status_code == 404
    assert client.get('/tag/9999').status_code == 404


def test_post_and_page_detail(client, content):
    response = client.get(f"/post/{content['post']}")
    assert response.status_code == 200
    assert b'Buen post' in response.data
    assert client.get('/post/9999').status_code == 404
    assert client.get(f"/page/{content['page']}").status_code == 200
    assert client.get('/page/9999').status_code == 404


def test_detail_pages_include_sidebar_lists(client, content):
    post_page = client.get(f"/post/{content['post']}")
    assert 'Categorías'.encode('utf-8') in post_page.data
    assert b'Acerca' in post_page.data
    assert b'aria-current="page"' in post_page.data

    page_detail = client.get(f"/page/{content['page']}")
    assert 'Categorías'.encode('utf-8') in page_detail.data
    assert b'Acerca' in page_detail.data
    assert b'aria-current="page"' in page_detail.data

    category_page = client.get(f"/category/{content['category']}")
    assert b'aria-current="page"' in category_page.data


def test_comment_requires_login(client, content):
    response = client.post(f"/post/{content['post']}/comment", data={'content': 'x'}, follow_redirects=False)
    assert response.status_code == 302


def test_comment_authenticated(auth_client, content):
    response = auth_client.post(f"/post/{content['post']}/comment", data={'content': 'Nuevo comentario'}, follow_redirects=False)
    assert response.status_code == 302
    response = auth_client.get(f"/post/{content['post']}")
    assert b'Nuevo comentario' in response.data
