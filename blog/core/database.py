from sqlalchemy_utils import create_database, database_exists

from blog.core.extensions import db


def ensure_database(app):
    with app.app_context():
        url = db.engine.url
        if not database_exists(url):
            create_database(url)
