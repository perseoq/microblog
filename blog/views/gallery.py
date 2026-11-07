import os
from uuid import uuid4

from flask import Blueprint, current_app, flash, redirect, render_template, url_for
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename

from blog.arch.forms import GalleryForm, UploadImageForm
from blog.arch.models import Gallery, Image, ImagesPage, ImagesPost
from blog.core.extensions import db

gallery = Blueprint('gallery', __name__)


@gallery.route('/gallery')
def index():
    galleries = Gallery.query.order_by(Gallery.date_created.desc()).all()
    return render_template('blog/gallery.html', galleries=galleries)


@gallery.route('/gallery/<int:gallery_id>')
def detail(gallery_id):
    album = db.get_or_404(Gallery, gallery_id)
    return render_template('blog/gallery_detail.html', gallery=album)


@gallery.route('/admin/galleries')
@login_required
def manage():
    galleries = Gallery.query.order_by(Gallery.date_created.desc()).all()
    return render_template('admin/gallery.html', galleries=galleries)


@gallery.route('/admin/gallery/browser')
@login_required
def browser():
    galleries = Gallery.query.order_by(Gallery.title).all()
    return render_template('admin/gallery_browser.html', galleries=galleries)


@gallery.route('/admin/galleries/new', methods=['GET', 'POST'])
@login_required
def new():
    form = GalleryForm()
    if form.validate_on_submit():
        album = Gallery(
            title=form.title.data,
            description=form.description.data,
            user_id=current_user.id,
        )
        db.session.add(album)
        db.session.commit()
        flash('Galería creada.', 'success')
        return redirect(url_for('gallery.manage_gallery', gallery_id=album.id))
    return render_template('admin/new_gallery.html', form=form)


@gallery.route('/admin/galleries/<int:gallery_id>')
@login_required
def manage_gallery(gallery_id):
    album = db.get_or_404(Gallery, gallery_id)
    return render_template('admin/gallery_manage.html', gallery=album, form=UploadImageForm())


@gallery.route('/admin/galleries/<int:gallery_id>/upload', methods=['POST'])
@login_required
def upload(gallery_id):
    album = db.get_or_404(Gallery, gallery_id)
    form = UploadImageForm()
    if form.validate_on_submit():
        for storage in form.image.data:
            _save_image(storage, album)
        db.session.commit()
        flash(f'{len(form.image.data)} imagen(es) subida(s).', 'success')
    else:
        flash('Archivo no válido. Usa: png, jpg, jpeg, gif o webp.', 'danger')
    return redirect(url_for('gallery.manage_gallery', gallery_id=album.id))


@gallery.route('/admin/galleries/<int:gallery_id>/delete', methods=['POST'])
@login_required
def delete(gallery_id):
    album = db.get_or_404(Gallery, gallery_id)
    for image in list(album.images):
        _delete_image(image)
    db.session.delete(album)
    db.session.commit()
    flash('Galería eliminada.', 'success')
    return redirect(url_for('gallery.manage'))


@gallery.route('/admin/images/<int:image_id>/delete', methods=['POST'])
@login_required
def delete_image(image_id):
    image = db.get_or_404(Image, image_id)
    gallery_id = image.gallery_id
    _delete_image(image)
    db.session.commit()
    flash('Imagen eliminada.', 'success')
    return redirect(url_for('gallery.manage_gallery', gallery_id=gallery_id))


def _save_image(storage, album):
    extension = secure_filename(storage.filename).rsplit('.', 1)[-1].lower()
    filename = f'{uuid4().hex}.{extension}'
    folder = os.path.join(
        current_app.static_folder, current_app.config['UPLOAD_IMAGE_FOLDER']
    )
    os.makedirs(folder, exist_ok=True)
    storage.save(os.path.join(folder, filename))
    image = Image(
        filename=filename,
        url=f"{current_app.config['UPLOAD_IMAGE_FOLDER']}/{filename}",
        gallery_id=album.id,
        user_id=current_user.id,
    )
    db.session.add(image)


def _delete_image(image):
    path = os.path.join(current_app.static_folder, image.url)
    if os.path.exists(path):
        os.remove(path)
    ImagesPost.query.filter_by(image_id=image.id).delete()
    ImagesPage.query.filter_by(image_id=image.id).delete()
    db.session.delete(image)
