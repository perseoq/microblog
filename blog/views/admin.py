import os

import segno
from flask import Blueprint, current_app, flash, redirect, render_template, request, session, url_for
from flask_login import current_user, login_required

from blog.arch.forms import (
    CategoryForm,
    ChangePasswordForm,
    PageForm,
    PostForm,
    ProfileForm,
    SettingsForm,
    SiteConfigForm,
    TOTPForm,
    TagForm,
    TwoFactorDisableForm,
)
from blog.arch.models import (
    Category,
    Comment,
    ImagesPage,
    ImagesPost,
    Page,
    Post,
    PostTags,
    Tag,
    User,
)
from blog.core.enviroment import read_env, write_env
from blog.core.extensions import db
from blog.core.site import get_site_config
from blog.core.themes import THEMES, themes_for_display
from blog.core.totp import generate_secret, provisioning_uri, verify_code

admin = Blueprint('admin', __name__, url_prefix='/admin')


def _post_form_choices(form):
    form.category.choices = [(c.id, c.name) for c in Category.query.order_by(Category.name).all()]
    form.tags.choices = [(t.id, t.name) for t in Tag.query.order_by(Tag.name).all()]


@admin.route('/')
@login_required
def dashboard():
    stats = {
        'posts': Post.query.count(),
        'pages': Page.query.count(),
        'categories': Category.query.count(),
        'tags': Tag.query.count(),
        'comments': Comment.query.count(),
        'users': User.query.count(),
    }
    recent_posts = Post.query.order_by(Post.date_posted.desc()).limit(5).all()
    return render_template('admin/dashboard.html', stats=stats, recent_posts=recent_posts)


@admin.route('/posts')
@login_required
def posts():
    posts = Post.query.order_by(Post.date_posted.desc()).all()
    return render_template('admin/post_list.html', posts=posts)


@admin.route('/posts/new', methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    _post_form_choices(form)
    if form.validate_on_submit():
        post = Post(
            title=form.title.data,
            content=form.content.data,
            category_id=form.category.data,
            user_id=current_user.id,
        )
        db.session.add(post)
        db.session.flush()
        for tag_id in form.tags.data:
            db.session.add(PostTags(post_id=post.id, tag_id=tag_id))
        db.session.commit()
        flash('Post creado.', 'success')
        return redirect(url_for('admin.posts'))
    return render_template('admin/new_post.html', form=form, heading='Nuevo post')


@admin.route('/posts/<int:post_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    post = db.get_or_404(Post, post_id)
    form = PostForm(obj=post)
    _post_form_choices(form)
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        post.category_id = form.category.data
        PostTags.query.filter_by(post_id=post.id).delete()
        for tag_id in form.tags.data:
            db.session.add(PostTags(post_id=post.id, tag_id=tag_id))
        db.session.commit()
        flash('Post actualizado.', 'success')
        return redirect(url_for('admin.posts'))
    if not form.is_submitted():
        form.category.data = post.category_id
        form.tags.data = [link.tag_id for link in PostTags.query.filter_by(post_id=post.id).all()]
    return render_template('admin/new_post.html', form=form, heading='Editar post')


@admin.route('/posts/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    post = db.get_or_404(Post, post_id)
    PostTags.query.filter_by(post_id=post.id).delete()
    Comment.query.filter_by(post_id=post.id).delete()
    ImagesPost.query.filter_by(post_id=post.id).delete()
    db.session.delete(post)
    db.session.commit()
    flash('Post eliminado.', 'success')
    return redirect(url_for('admin.posts'))


@admin.route('/pages')
@login_required
def pages():
    pages = Page.query.order_by(Page.title).all()
    return render_template('admin/pages_list.html', pages=pages)


@admin.route('/pages/new', methods=['GET', 'POST'])
@login_required
def new_page():
    form = PageForm()
    if form.validate_on_submit():
        page = Page(title=form.title.data, content=form.content.data, user_id=current_user.id)
        db.session.add(page)
        db.session.commit()
        flash('Página creada.', 'success')
        return redirect(url_for('admin.pages'))
    return render_template('admin/new_page.html', form=form, heading='Nueva página')


@admin.route('/pages/<int:page_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_page(page_id):
    page = db.get_or_404(Page, page_id)
    form = PageForm(obj=page)
    if form.validate_on_submit():
        page.title = form.title.data
        page.content = form.content.data
        db.session.commit()
        flash('Página actualizada.', 'success')
        return redirect(url_for('admin.pages'))
    return render_template('admin/new_page.html', form=form, heading='Editar página')


@admin.route('/pages/<int:page_id>/delete', methods=['POST'])
@login_required
def delete_page(page_id):
    page = db.get_or_404(Page, page_id)
    ImagesPage.query.filter_by(page_id=page.id).delete()
    db.session.delete(page)
    db.session.commit()
    flash('Página eliminada.', 'success')
    return redirect(url_for('admin.pages'))


@admin.route('/categories', methods=['GET', 'POST'])
@login_required
def categories():
    form = CategoryForm()
    if form.validate_on_submit():
        if Category.query.filter_by(name=form.name.data).first():
            flash('La categoría ya existe.', 'danger')
        else:
            db.session.add(Category(name=form.name.data))
            db.session.commit()
            flash('Categoría creada.', 'success')
            return redirect(url_for('admin.categories'))
    categories = Category.query.order_by(Category.name).all()
    return render_template('admin/categories_list.html', form=form, categories=categories)


@admin.route('/categories/<int:category_id>/delete', methods=['POST'])
@login_required
def delete_category(category_id):
    category = db.get_or_404(Category, category_id)
    if category.posts:
        flash('No se puede eliminar una categoría con posts.', 'danger')
    else:
        db.session.delete(category)
        db.session.commit()
        flash('Categoría eliminada.', 'success')
    return redirect(url_for('admin.categories'))


@admin.route('/tags', methods=['GET', 'POST'])
@login_required
def tags():
    form = TagForm()
    if form.validate_on_submit():
        if Tag.query.filter_by(name=form.name.data).first():
            flash('La etiqueta ya existe.', 'danger')
        else:
            db.session.add(Tag(name=form.name.data))
            db.session.commit()
            flash('Etiqueta creada.', 'success')
            return redirect(url_for('admin.tags'))
    tags = Tag.query.order_by(Tag.name).all()
    return render_template('admin/tags_list.html', form=form, tags=tags)


@admin.route('/tags/<int:tag_id>/delete', methods=['POST'])
@login_required
def delete_tag(tag_id):
    tag = db.get_or_404(Tag, tag_id)
    PostTags.query.filter_by(tag_id=tag.id).delete()
    db.session.delete(tag)
    db.session.commit()
    flash('Etiqueta eliminada.', 'success')
    return redirect(url_for('admin.tags'))


@admin.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = ProfileForm(obj=current_user)
    if form.validate_on_submit():
        conflict = User.query.filter(
            User.id != current_user.id,
            db.or_(User.username == form.username.data, User.email == form.email.data),
        ).first()
        if conflict:
            flash('El nombre de usuario o el correo ya están en uso.', 'danger')
        else:
            current_user.username = form.username.data
            current_user.email = form.email.data
            db.session.commit()
            flash('Perfil actualizado.', 'success')
            return redirect(url_for('admin.profile'))
    return render_template(
        'admin/profile.html',
        form=form,
        password_form=ChangePasswordForm(),
        disable_form=TwoFactorDisableForm(),
    )


@admin.route('/profile/password', methods=['POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if not current_user.check_password(form.current_password.data):
            flash('La contraseña actual no es correcta.', 'danger')
        else:
            current_user.set_password(form.new_password.data)
            db.session.commit()
            flash('Contraseña actualizada.', 'success')
    else:
        flash('Revisa los datos de la nueva contraseña.', 'danger')
    return redirect(url_for('admin.profile'))


@admin.route('/profile/2fa', methods=['GET', 'POST'])
@login_required
def two_factor():
    if current_user.totp_enabled:
        return redirect(url_for('admin.profile'))
    secret = session.get('totp_setup_secret')
    if not secret:
        secret = generate_secret()
        session['totp_setup_secret'] = secret
    form = TOTPForm()
    if form.validate_on_submit():
        if verify_code(secret, form.code.data):
            current_user.totp_secret = secret
            current_user.totp_enabled = True
            db.session.commit()
            session.pop('totp_setup_secret', None)
            flash('Verificación en dos pasos activada.', 'success')
            return redirect(url_for('admin.profile'))
        flash('Código inválido. Revisa la hora de tu dispositivo e inténtalo de nuevo.', 'danger')
    uri = provisioning_uri(secret, current_user.email)
    qr_data_uri = segno.make(uri).svg_data_uri(scale=4)
    return render_template('admin/two_factor.html', form=form, secret=secret, qr_data_uri=qr_data_uri)


@admin.route('/profile/2fa/disable', methods=['POST'])
@login_required
def disable_two_factor():
    if not current_user.totp_enabled:
        return redirect(url_for('admin.profile'))
    form = TwoFactorDisableForm()
    if form.validate_on_submit():
        if current_user.check_password(form.password.data) and verify_code(current_user.totp_secret, form.code.data):
            current_user.totp_enabled = False
            current_user.totp_secret = None
            db.session.commit()
            flash('Verificación en dos pasos desactivada.', 'success')
        else:
            flash('Contraseña o código incorrectos.', 'danger')
    else:
        flash('Introduce tu contraseña y un código de 6 dígitos.', 'danger')
    return redirect(url_for('admin.profile'))


@admin.route('/themes', methods=['GET', 'POST'])
@login_required
def themes():
    config = get_site_config()
    if request.method == 'POST':
        name = request.form.get('theme', '').strip()
        if name in THEMES:
            config.theme = name
            db.session.commit()
            flash(f'Tema «{THEMES[name]["label"]}» aplicado.', 'success')
            return redirect(url_for('admin.themes'))
        flash('Tema no válido.', 'danger')
    return render_template(
        'admin/themes.html',
        themes=themes_for_display(),
        current=config.theme,
        current_label=THEMES.get(config.theme, THEMES['default'])['label'],
    )


@admin.route('/configuracion', methods=['GET', 'POST'])
@login_required
def site_config():
    config = get_site_config()
    form = SiteConfigForm(obj=config)
    if form.validate_on_submit():
        config.site_title = form.site_title.data.strip()
        config.site_description = (form.site_description.data or '').strip()
        config.footer_text = form.footer_text.data.strip()
        db.session.commit()
        flash('Configuración del sitio actualizada.', 'success')
        return redirect(url_for('admin.site_config'))
    return render_template('admin/site_config.html', form=form)


@admin.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    env_path = current_app.config.get('ENV_FILE') or os.path.join(current_app.root_path, '.env')
    current = read_env(env_path)
    form = SettingsForm()

    if form.validate_on_submit():
        values = {
            'DEBUG': 'True' if form.debug.data else 'False',
            'DATABASE_URI': form.database_uri.data.strip(),
            'MAIL_SERVER': (form.mail_server.data or '').strip(),
            'MAIL_PORT': str(form.mail_port.data),
            'MAIL_USERNAME': (form.mail_username.data or '').strip(),
            'MAIL_USE_TLS': 'True' if form.mail_use_tls.data else 'False',
            'MAIL_USE_SSL': 'True' if form.mail_use_ssl.data else 'False',
            'MAIL_DEFAULT_SENDER': (form.mail_default_sender.data or '').strip(),
        }

        secret_key = (form.secret_key.data or '').strip()
        if secret_key:
            values['SECRET_KEY'] = secret_key

        mail_password = form.mail_password.data or ''
        if mail_password:
            values['MAIL_PASSWORD'] = mail_password

        write_env(env_path, values)
        flash('Configuración guardada. Reinicia la aplicación para aplicar los cambios.', 'success')
        return redirect(url_for('admin.settings'))

    if not form.is_submitted():
        form.debug.data = (current.get('DEBUG') or 'True') == 'True'
        form.database_uri.data = current.get('DATABASE_URI') or ''
        form.mail_server.data = current.get('MAIL_SERVER') or ''
        try:
            form.mail_port.data = int(current.get('MAIL_PORT') or 587)
        except (TypeError, ValueError):
            form.mail_port.data = 587
        form.mail_username.data = current.get('MAIL_USERNAME') or ''
        form.mail_use_tls.data = (current.get('MAIL_USE_TLS') or 'True') == 'True'
        form.mail_use_ssl.data = (current.get('MAIL_USE_SSL') or 'False') == 'True'
        form.mail_default_sender.data = current.get('MAIL_DEFAULT_SENDER') or ''

    database_uri = current.get('DATABASE_URI') or ''
    database_driver = database_uri.split('://', 1)[0] if database_uri else 'sin configurar'
    return render_template(
        'admin/settings.html',
        form=form,
        database_driver=database_driver,
    )


@admin.route('/search')
@login_required
def search():
    query = request.args.get('q', '').strip()
    posts = []
    if query:
        pattern = f'%{query}%'
        posts = Post.query.filter(
            db.or_(Post.title.ilike(pattern), Post.content.ilike(pattern))
        ).order_by(Post.date_posted.desc()).all()
    return render_template('admin/search_by.html', posts=posts, query=query)
