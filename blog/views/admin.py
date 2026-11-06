from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from blog.arch.forms import (
    CategoryForm,
    ChangePasswordForm,
    PageForm,
    PostForm,
    ProfileForm,
    TagForm,
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
from blog.core.extensions import db

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
    return render_template('admin/profile.html', form=form, password_form=ChangePasswordForm())


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


@admin.route('/settings')
@login_required
def settings():
    database_uri = current_app.config.get('SQLALCHEMY_DATABASE_URI', '')
    database_driver = database_uri.split('://', 1)[0] if database_uri else 'sin configurar'
    return render_template(
        'admin/settings.html',
        debug=current_app.config.get('DEBUG'),
        mail_server=current_app.config.get('MAIL_SERVER'),
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
