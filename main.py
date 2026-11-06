import bleach
from flask import Flask
from markupsafe import Markup

from blog.arch.models import User
from blog.core.extensions import bc, ckeditor, csrf, db, login, mail
from blog.core.settings import ProductionConfig
from blog.views.admin import admin
from blog.views.auth import auth
from blog.views.blog import blog
from blog.views.gallery import gallery
from blog.views.pages import pages
from blog.views.posts import posts

app = Flask(__name__)
app.config.from_object(ProductionConfig)

bc.init_app(app)
db.init_app(app)
login.init_app(app)
mail.init_app(app)
csrf.init_app(app)
ckeditor.init_app(app)

login.login_view = 'auth.login'
login.login_message_category = 'warning'

ALLOWED_HTML_TAGS = [
    'p', 'br', 'hr', 'strong', 'b', 'em', 'i', 'u', 's', 'blockquote',
    'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'ul', 'ol', 'li', 'pre', 'code',
    'a', 'img', 'figure', 'figcaption', 'table', 'thead', 'tbody', 'tr',
    'th', 'td', 'span', 'div',
]
ALLOWED_HTML_ATTRIBUTES = {
    '*': ['class'],
    'a': ['href', 'title', 'target', 'rel'],
    'img': ['src', 'alt', 'title', 'width', 'height'],
}


def sanitize_html(value):
    cleaned = bleach.clean(
        value or '',
        tags=ALLOWED_HTML_TAGS,
        attributes=ALLOWED_HTML_ATTRIBUTES,
        protocols=['http', 'https', 'mailto'],
        strip=True,
    )
    return Markup(cleaned)


app.jinja_env.filters['safe_html'] = sanitize_html


@login.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


app.register_blueprint(auth)
app.register_blueprint(admin)
app.register_blueprint(blog)
app.register_blueprint(posts)
app.register_blueprint(pages)
app.register_blueprint(gallery)
