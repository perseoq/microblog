import io

from blog.arch.models import Gallery, Image, User
from blog.core.extensions import db


def test_gallery_requires_login(client):
    assert client.get('/admin/galleries').status_code == 302


def test_gallery_create_and_public(auth_client):
    response = auth_client.post('/admin/galleries/new', data={
        'title': 'Viajes',
        'description': 'fotos',
    }, follow_redirects=False)
    assert response.status_code == 302

    album = Gallery.query.filter_by(title='Viajes').first()
    assert album is not None
    assert b'Viajes' in auth_client.get('/gallery').data
    assert auth_client.get(f'/gallery/{album.id}').status_code == 200
    assert auth_client.get('/gallery/9999').status_code == 404


def test_image_upload_and_delete(auth_client, app, tmp_path):
    app.config['UPLOAD_IMAGE_FOLDER'] = str(tmp_path)
    auth_client.post('/admin/galleries/new', data={'title': 'Viajes', 'description': ''}, follow_redirects=False)
    album = Gallery.query.filter_by(title='Viajes').first()

    response = auth_client.post(
        f'/admin/galleries/{album.id}/upload',
        data={'image': [
            (io.BytesIO(b'\x89PNG uno'), 'uno.png'),
            (io.BytesIO(b'\x89PNG dos'), 'dos.png'),
        ]},
        content_type='multipart/form-data',
        follow_redirects=False,
    )
    assert response.status_code == 302
    images = Image.query.filter_by(gallery_id=album.id).order_by(Image.id).all()
    assert len(images) == 2
    for image in images:
        assert (tmp_path / image.filename).exists()

    response = auth_client.post(
        f'/admin/galleries/{album.id}/upload',
        data={'image': (io.BytesIO(b'texto'), 'malicioso.txt')},
        content_type='multipart/form-data',
        follow_redirects=True,
    )
    assert 'Archivo no'.encode('utf-8') in response.data
    assert Image.query.filter_by(gallery_id=album.id).count() == 2

    stored = [(image.id, image.filename) for image in images]
    for image_id, filename in stored:
        auth_client.post(f'/admin/images/{image_id}/delete', follow_redirects=False)
        assert db.session.get(Image, image_id) is None
        assert not (tmp_path / filename).exists()

    auth_client.post(f'/admin/galleries/{album.id}/delete', follow_redirects=False)
    assert db.session.get(Gallery, album.id) is None


def test_gallery_browser_requires_login(client):
    assert client.get('/admin/gallery/browser').status_code == 302


def test_gallery_manage_page_has_upload_preview(auth_client, app):
    auth_client.post('/admin/galleries/new', data={'title': 'UI', 'description': ''}, follow_redirects=False)
    album = Gallery.query.filter_by(title='UI').first()

    response = auth_client.get(f'/admin/galleries/{album.id}')
    assert response.status_code == 200
    assert b'data-upload-preview' in response.data
    assert b'js/gallery-upload.js' in response.data
    assert b'multiple' in response.data


def test_gallery_list_renders_cards(auth_client):
    auth_client.post('/admin/galleries/new', data={'title': 'Tarjeta', 'description': 'desc'}, follow_redirects=False)

    response = auth_client.get('/admin/galleries')
    assert response.status_code == 200
    assert b'album-card' in response.data
    assert b'Tarjeta' in response.data
    assert 'Eliminar galería'.encode('utf-8') in response.data
    assert b'button-danger' in response.data


def test_gallery_browser_lists_images(auth_client, app):
    user = User.query.first()
    album = Gallery(title='Browser', description='', user_id=user.id)
    db.session.add(album)
    db.session.commit()

    db.session.add(Image(filename='foto.png', url='uploads/imgs/foto.png', gallery_id=album.id, user_id=user.id))
    db.session.commit()

    response = auth_client.get('/admin/gallery/browser')
    assert response.status_code == 200
    assert b'/static/uploads/imgs/foto.png' in response.data
