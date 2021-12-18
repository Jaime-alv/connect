#  connect. Build your own private social net
#  Copyright (C) 2021 Jaime Alvarez Fernandez
#  Contact info: jaime.af.git@gmail.com
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.

from connect import db, login
import datetime
import werkzeug.security
from flask_login import UserMixin
from hashlib import md5

# followers association table
# auxiliary table that has no data other than the foreign keys
followers = db.Table('followers',
                     db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
                     db.Column('followed_id', db.Integer, db.ForeignKey('user.id')))

stars = db.Table('stars',
                 db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
                 db.Column('post_id', db.Integer, db.ForeignKey('posts.id')))


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    nickname = db.Column(db.String(64))
    password = db.Column(db.String(128))
    about_me = db.Column(db.String(140))
    location = db.Column(db.String(64))
    website = db.Column(db.String(120))
    last_seen = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    follower_bio = db.Column(db.Boolean, default=False)

    # One-to-Many relationship
    # link User with many items
    posts = db.relationship('Posts', backref='author', lazy='dynamic')
    reply = db.relationship('Reply', backref='author', lazy='dynamic')

    # Many-to-Many relationship
    # link Parent class User with another User
    followed = db.relationship('User',
                               secondary=followers,
                               primaryjoin=(followers.c.follower_id == id),
                               secondaryjoin=(followers.c.followed_id == id),
                               backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')

    # Many-to-Many relationship
    # link User to star's post
    starred = db.relationship('Posts',
                              secondary=stars,
                              backref=db.backref('awarded_stars', lazy='dynamic'), lazy='dynamic')

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

    def is_following(self, user):
        # return True if there is a relationship between the two users. If followed_id is equal to user.id, count() will
        # result 1, so return will be True
        return self.followed.filter(followers.c.followed_id == user.id).count() > 0

    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)

    def followed_posts(self):
        # join(create a temporary table that combines data from posts and followers tables,
        # retrieves all posts from people that is followed)
        # filter(Only need those posts from users User follows)
        # union(combines posts from followed with posts from User.id)
        # order_by()
        posts_from_followed = Posts.query. \
            join(followers, (followers.c.followed_id == Posts.user_id)). \
            filter(followers.c.follower_id == self.id)
        posts_from_me = Posts.query.filter_by(user_id=self.id)
        return posts_from_followed.union(posts_from_me).order_by(Posts.timestamp.desc())

    def followed_users(self):
        return self.followed

    def is_starred(self, post):
        return self.starred.filter(stars.c.post_id == post.id).count() > 0

    def star_post(self, post):
        if not self.is_starred(post):
            self.starred.append(post)

    def un_star_post(self, post):
        if self.is_starred(post):
            self.starred.remove(post)


class Posts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    reply = db.relationship('Reply', backref='original', lazy='dynamic')

    def replies(self):
        return Reply.query.filter_by(post_id=self.id)

    def __repr__(self):
        return f'<Post {self.body}>'


class Reply(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))

    def __repr__(self):
        author = User.query.filter_by(id=self.user_id).first()
        to = Posts.query.filter_by(id=self.post_id).first().author
        return f'<Reply:"{self.body}" from {author} to {to}>'


@login.user_loader
def load_user(user_id):
    # pass the user_id to database and get said user
    return User.query.get(int(user_id))
