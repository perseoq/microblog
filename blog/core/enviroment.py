import os
from dotenv import dotenv_values, load_dotenv, set_key
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
TRUSTED_HOSTS = [
    host.strip()
    for host in os.getenv('TRUSTED_HOSTS', 'localhost,127.0.0.1,[::1]').split(',')
    if host.strip()
]


def read_env(path):
    return dotenv_values(path) or {}


def write_env(path, values):
    if not os.path.exists(path):
        open(path, 'w', encoding='utf-8').close()
    for key, value in values.items():
        cleaned = str(value).replace('\r', ' ').replace('\n', ' ').strip()
        set_key(path, key, cleaned, quote_mode='always')
