from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate
from flask_wtf import CSRFProtect
from flask_ckeditor import CKEditor

bc = Bcrypt()
db = SQLAlchemy()
login = LoginManager()
mail = Mail()
migrate = Migrate()
csrf = CSRFProtect()
ckeditor = CKEditor()
