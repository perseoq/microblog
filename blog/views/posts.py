from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import current_user, login_required

from blog.arch.forms import CommentForm
from blog.arch.models import Comment, Post
from blog.core.extensions import db

posts = Blueprint('posts', __name__)


@posts.route('/post/<int:post_id>')
def detail(post_id):
    post = db.get_or_404(Post, post_id)
    comments = (
        Comment.query.filter_by(post_id=post.id)
        .order_by(Comment.date_posted.asc())
        .all()
    )
    form = CommentForm()
    return render_template('blog/posts.html', post=post, comments=comments, form=form)


@posts.route('/post/<int:post_id>/comment', methods=['POST'])
@login_required
def add_comment(post_id):
    post = db.get_or_404(Post, post_id)
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(
            content=form.content.data,
            post_id=post.id,
            user_id=current_user.id,
        )
        db.session.add(comment)
        db.session.commit()
        flash('Comentario publicado.', 'success')
    else:
        flash('El comentario no puede estar vacío.', 'danger')
    return redirect(url_for('posts.detail', post_id=post.id))
