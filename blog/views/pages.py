from flask import Blueprint, render_template

from blog.arch.models import Page
from blog.core.extensions import db

pages = Blueprint('pages', __name__)


@pages.route('/page/<int:page_id>')
def detail(page_id):
    page = db.get_or_404(Page, page_id)
    return render_template('blog/pages.html', page=page)
