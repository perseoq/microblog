import os
from urllib.parse import urlparse

import bleach
from bleach.css_sanitizer import CSSSanitizer
from flask import Flask, request
from markupsafe import Markup

from blog.arch.models import User
from blog.core.commands import seed_admin
from blog.core.database import ensure_database
from blog.core.extensions import bc, ckeditor, csrf, db, login, mail, migrate
from blog.core.navigation import sidebar_nav
from blog.core.settings import DevelopmentConfig, ProductionConfig
from blog.core.site import get_site_config
from blog.views.admin import admin
from blog.views.auth import auth
from blog.views.blog import blog
from blog.views.gallery import gallery
from blog.views.pages import pages
from blog.views.posts import posts

app = Flask(__name__)
config_class = DevelopmentConfig if os.getenv('DEBUG') == 'True' else ProductionConfig
app.config.from_object(config_class)

bc.init_app(app)
db.init_app(app)
ensure_database(app)
migrate.init_app(app, db)
login.init_app(app)
mail.init_app(app)
csrf.init_app(app)
ckeditor.init_app(app)

app.cli.add_command(seed_admin)

login.login_view = 'auth.login'
login.login_message_category = 'warning'

ALLOWED_HTML_TAGS = [
    'p', 'br', 'hr', 'strong', 'b', 'em', 'i', 'u', 's', 'blockquote',
    'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'ul', 'ol', 'li', 'pre', 'code',
    'a', 'img', 'figure', 'figcaption', 'table', 'thead', 'tbody', 'tr',
    'th', 'td', 'span', 'div', 'font', 'iframe',
]
ALLOWED_HTML_ATTRIBUTES = {
    '*': ['class', 'style'],
    'a': ['href', 'title', 'target', 'rel'],
    'img': ['src', 'alt', 'title', 'width', 'height'],
    'font': ['color', 'face', 'size'],
}
ALLOWED_IFRAME_ATTRIBUTES = {
    'src', 'width', 'height', 'allow', 'allowfullscreen', 'frameborder',
    'loading', 'title', 'referrerpolicy',
}
ALLOWED_EMBED_HOSTS = {
    'youtube.com', 'www.youtube.com', 'youtube-nocookie.com',
    'www.youtube-nocookie.com', 'open.spotify.com', 'instagram.com',
    'www.instagram.com', 'player.vimeo.com',
}
CSS_SANITIZER = CSSSanitizer(allowed_css_properties=[
    'color', 'background-color', 'text-align', 'font-family', 'font-size',
    'font-weight', 'font-style', 'text-decoration',
])


def _is_allowed_embed(value):
    try:
        parsed = urlparse(value)
    except ValueError:
        return False
    return parsed.scheme in ('http', 'https') and parsed.netloc.lower() in ALLOWED_EMBED_HOSTS


def _allowed_attribute(tag, name, value):
    if tag == 'iframe':
        if name not in ALLOWED_IFRAME_ATTRIBUTES:
            return False
        return _is_allowed_embed(value) if name == 'src' else True
    allowed = ALLOWED_HTML_ATTRIBUTES.get('*', []) + ALLOWED_HTML_ATTRIBUTES.get(tag, [])
    return name in allowed


def sanitize_html(value):
    cleaned = bleach.clean(
        value or '',
        tags=ALLOWED_HTML_TAGS,
        attributes=_allowed_attribute,
        protocols=['http', 'https', 'mailto'],
        strip=True,
        css_sanitizer=CSS_SANITIZER,
    )
    return Markup(cleaned)


app.jinja_env.filters['safe_html'] = sanitize_html
app.jinja_env.globals['sidebar_nav'] = sidebar_nav


@app.context_processor
def inject_site_config():
    return {'site': get_site_config()}


@app.after_request
def add_security_headers(response):
    response.headers.setdefault('X-Content-Type-Options', 'nosniff')
    response.headers.setdefault('X-Frame-Options', 'DENY')
    response.headers.setdefault('Referrer-Policy', 'strict-origin-when-cross-origin')
    response.headers.setdefault('Permissions-Policy', 'geolocation=(), microphone=(), camera=()')
    response.headers.setdefault(
        'Content-Security-Policy',
        "default-src 'self'; "
        "img-src 'self' data: blob:; "
        "style-src 'self' 'unsafe-inline'; "
        "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
        "font-src 'self' data:; "
        "connect-src 'self'; "
        "frame-src 'self' https://youtube.com https://www.youtube.com "
        "https://www.youtube-nocookie.com https://open.spotify.com "
        "https://instagram.com https://www.instagram.com https://player.vimeo.com; "
        "frame-ancestors 'none'; "
        "base-uri 'self'; "
        "form-action 'self'; "
        "object-src 'none'",
    )
    if request.is_secure:
        response.headers.setdefault('Strict-Transport-Security', 'max-age=31536000; includeSubDomains')
    return response


@login.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


app.register_blueprint(auth)
app.register_blueprint(admin)
app.register_blueprint(blog)
app.register_blueprint(posts)
app.register_blueprint(pages)
app.register_blueprint(gallery)
