# Copyright (C) 2021 Jaime Alvarez Fernandez

from connect import db, login
import datetime
import werkzeug.security
from flask_login import UserMixin
from hashlib import md5


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password = db.Column(db.String(128))
    about_me = db.Column(db.String(140))
    location = db.Column(db.String(64))
    website = db.Column(db.String(120))
    last_seen = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def __repr__(self):
        return f'<User {self.username}>'

    def hash_password(self, password):
        # hash user password
        self.password = werkzeug.security.generate_password_hash(password)

    def check_password(self, password):
        # compare hash password against input password
        return werkzeug.security.check_password_hash(self.password, password)

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return f'https://www.gravatar.com/avatar/{digest}?d=identicon&s={size}'


class Posts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return f'<Post {self.body}>'


@login.user_loader
def load_user(user_id):
    # pass the user_id to database and get said user
    return User.query.get(int(user_id))
