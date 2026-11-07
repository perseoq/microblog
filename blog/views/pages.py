from flask import Blueprint, render_template

from blog.arch.models import Category, Page, Tag
from blog.core.extensions import db

pages = Blueprint('pages', __name__)


@pages.route('/pages')
def index():
    return render_template(
        'blog/pages_index.html',
        pages=Page.query.order_by(Page.title).all(),
        categories=Category.query.order_by(Category.name).all(),
        tags=Tag.query.order_by(Tag.name).all(),
    )


@pages.route('/page/<int:page_id>')
def detail(page_id):
    page = db.get_or_404(Page, page_id)
    return render_template('blog/pages.html', page=page)
