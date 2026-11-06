from flask import Flask

from blog.arch.models import User
from blog.core.extensions import bc, ckeditor, csrf, db, login, mail
from blog.core.settings import ProductionConfig
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


@login.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


app.register_blueprint(auth)
app.register_blueprint(blog)
app.register_blueprint(posts)
app.register_blueprint(pages)
app.register_blueprint(gallery)
