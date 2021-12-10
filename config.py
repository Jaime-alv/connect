import os
import secrets

basedir = os.path.abspath(os.path.dirname(__file__))
secret_key = secrets.token_hex()


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or secret_key
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
