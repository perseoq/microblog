from flask import Blueprint, Response, jsonify, render_template, request

from blog.arch.models import Category, Post, PostTags, Tag
from blog.core.extensions import db
from blog.core.themes import theme_css as build_theme_css

blog = Blueprint('blog', __name__)


@blog.route('/theme.css')
def theme_css():
    return Response(
        build_theme_css(),
        mimetype='text/css',
        headers={'Cache-Control': 'public, max-age=3600'},
    )


@blog.route('/')
def index():
    posts = Post.query.filter_by(status='published').order_by(Post.date_posted.desc()).all()
    return render_template('blog/home.html', posts=posts)


@blog.route('/categories')
def categories():
    return render_template(
        'blog/categories.html',
        categories=Category.query.order_by(Category.name).all(),
    )


@blog.route('/search')
def search():
    query = request.args.get('q', '').strip()
    if query:
        pattern = f'%{query}%'
        posts = Post.query.filter(
            Post.status == 'published',
            db.or_(Post.title.ilike(pattern), Post.content.ilike(pattern)),
        ).order_by(Post.date_posted.desc()).all()
    else:
        posts = []
    return render_template('blog/search_by.html', posts=posts, query=query)


@blog.route('/search/suggest')
def search_suggest():
    query = request.args.get('q', '').strip()
    if len(query) < 2:
        return jsonify([])
    pattern = f'%{query}%'
    posts = (
        Post.query.filter(Post.title.ilike(pattern))
        .order_by(Post.date_posted.desc())
        .limit(8)
        .all()
    )
    return jsonify([post.title for post in posts])


@blog.route('/category/<int:category_id>')
def category(category_id):
    category = db.get_or_404(Category, category_id)
    posts = Post.query.filter_by(category_id=category.id, status='published').order_by(Post.date_posted.desc()).all()
    return render_template('blog/index.html', posts=posts, heading=f'Categoría: {category.name}', category=category)


@blog.route('/tag/<int:tag_id>')
def tag(tag_id):
    tag = db.get_or_404(Tag, tag_id)
    posts = (
        Post.query.join(PostTags, PostTags.post_id == Post.id)
        .filter(PostTags.tag_id == tag.id, Post.status == 'published')
        .order_by(Post.date_posted.desc())
        .all()
    )
    return render_template('blog/index.html', posts=posts, heading=f'Etiqueta: {tag.name}', tag=tag)
