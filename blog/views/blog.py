from flask import Blueprint, render_template, request

from blog.arch.models import Category, Page, Post, PostTags, Tag
from blog.core.extensions import db

blog = Blueprint('blog', __name__)


def _sidebar_data():
    return {
        'categories': Category.query.order_by(Category.name).all(),
        'tags': Tag.query.order_by(Tag.name).all(),
        'pages': Page.query.order_by(Page.title).all(),
    }


@blog.route('/')
def index():
    posts = Post.query.order_by(Post.date_posted.desc()).all()
    return render_template('blog/index.html', posts=posts, **_sidebar_data())


@blog.route('/search')
def search():
    query = request.args.get('q', '').strip()
    if query:
        pattern = f'%{query}%'
        posts = Post.query.filter(
            db.or_(Post.title.ilike(pattern), Post.content.ilike(pattern))
        ).order_by(Post.date_posted.desc()).all()
    else:
        posts = []
    return render_template('blog/search_by.html', posts=posts, query=query, **_sidebar_data())


@blog.route('/category/<int:category_id>')
def category(category_id):
    category = db.get_or_404(Category, category_id)
    posts = Post.query.filter_by(category_id=category.id).order_by(Post.date_posted.desc()).all()
    return render_template(
        'blog/index.html', posts=posts, heading=f'Categoría: {category.name}', **_sidebar_data()
    )


@blog.route('/tag/<int:tag_id>')
def tag(tag_id):
    tag = db.get_or_404(Tag, tag_id)
    posts = (
        Post.query.join(PostTags, PostTags.post_id == Post.id)
        .filter(PostTags.tag_id == tag.id)
        .order_by(Post.date_posted.desc())
        .all()
    )
    return render_template(
        'blog/index.html', posts=posts, heading=f'Etiqueta: {tag.name}', **_sidebar_data()
    )
