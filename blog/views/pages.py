from flask import Blueprint, abort, render_template
from flask_login import current_user

from blog.arch.models import Page
from blog.core.extensions import db

pages = Blueprint('pages', __name__)


@pages.route('/pages')
def index():
    return render_template(
        'blog/pages_index.html',
        pages=Page.query.filter_by(status='published').order_by(Page.title).all(),
    )


@pages.route('/page/<int:page_id>')
def detail(page_id):
    page = db.get_or_404(Page, page_id)
    if page.status != 'published' and not current_user.is_authenticated:
        abort(404)
    return render_template('blog/pages.html', page=page)
