import os
from dotenv import load_dotenv
load_dotenv()

DATABASE_URI = os.getenv('DATABASE_URI')
MAIL_SERVER = os.getenv('MAIL_SERVER')
MAIL_PORT = int(os.getenv('MAIL_PORT'))
MAIL_USERNAME = os.getenv('MAIL_USERNAME')
MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
MAIL_USE_TLS = os.getenv('MAIL_USE_TLS') == 'True'
MAIL_USE_SSL = os.getenv('MAIL_USE_SSL') == 'True'
MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER')

SQLALCHEMY_DATABASE_URI = DATABASE_URI
SQLALCHEMY_TRACK_MODIFICATIONS = False
DEBUG = os.getenv('DEBUG') == 'True'
SECRET_KEY = os.getenv('SECRET_KEY')
