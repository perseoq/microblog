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


def test_search(client, content):
    assert b'Hola Flask' in client.get('/search?q=flask').data
    assert b'Sin resultados' in client.get('/search?q=nada').data


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


def test_comment_requires_login(client, content):
    response = client.post(f"/post/{content['post']}/comment", data={'content': 'x'}, follow_redirects=False)
    assert response.status_code == 302


def test_comment_authenticated(auth_client, content):
    response = auth_client.post(f"/post/{content['post']}/comment", data={'content': 'Nuevo comentario'}, follow_redirects=False)
    assert response.status_code == 302
    response = auth_client.get(f"/post/{content['post']}")
    assert b'Nuevo comentario' in response.data
