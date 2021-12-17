#  connect. Build your own private social net
#  Copyright (C) 2021 Jaime Alvarez Fernandez
#  Contact info: jaime.af.git@gmail.com
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.
#

import flask
import flask_login
from werkzeug import urls
import datetime
from connect import app, db
from connect import models, forms


@app.route('/')
@app.route('/index')
def index():
    if flask_login.current_user.is_authenticated:
        return flask.redirect(flask.url_for('user_messages', username=flask_login.current_user.username))
    return flask.render_template('index.html', title='Home page')


@app.route('/user/<username>', methods=['GET', 'POST'])
@flask_login.login_required
def user_messages(username):
    user = models.User.query.filter_by(username=username).first_or_404()
    form = forms.WriteMessage()
    empty_form = forms.EmptyForm()
    if form.validate_on_submit():
        post = models.Posts(body=form.message.data, author=flask_login.current_user)
        db.session.add(post)
        db.session.commit()
        return flask.redirect(flask.url_for('index'))
    posts = models.Posts.query.filter_by(user_id=user.id).order_by(models.Posts.timestamp.desc()).all()
    return flask.render_template('user.html', user=user, posts=posts, title=user.username, form=form, e_form=empty_form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if flask_login.current_user.is_authenticated:
        return flask.redirect(flask.url_for('index'))
    form = forms.LoginForm()
    if form.validate_on_submit():
        user = models.User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flask.flash('Invalid username or password')
            return flask.redirect(flask.url_for('login'))
        flask_login.login_user(user, remember=form.remember_me.data)
        next_page = flask.request.args.get('next')
        if not next_page or urls.url_parse(next_page).netloc != '':
            next_page = flask.url_for('index')
        return flask.redirect(next_page)
    return flask.render_template('login.html', title='Log in', form=form)


@app.route('/profile', methods=['GET', 'POST'])
@flask_login.login_required
def profile():
    form = forms.EditProfileForm()
    if form.validate_on_submit():
        if form.user_email.data != '':
            flask_login.current_user.email = form.user_email.data
        flask_login.current_user.about_me = form.about_me.data
        flask_login.current_user.location = form.location.data
        flask_login.current_user.website = form.website.data
        flask_login.current_user.nickname = form.nickname.data
        flask_login.current_user.follower_bio = form.followers.data
        db.session.commit()
        flask.flash('Your changes have been saved.')
        return flask.redirect(flask.url_for('profile'))
    elif flask.request.method == 'GET':
        form.user_email.data = ''
        form.nickname.data = flask_login.current_user.nickname
        form.about_me.data = flask_login.current_user.about_me
        form.website.data = flask_login.current_user.website
        form.location.data = flask_login.current_user.location
        form.followers.data = flask_login.current_user.follower_bio
    return flask.render_template('profile.html', user=flask_login.current_user, form=form, title='Profile')


@app.route('/sign_in', methods=['GET', 'POST'])
def sign_in():
    if flask_login.current_user.is_authenticated:
        return flask.redirect(flask.url_for('index'))
    form = forms.RegisterForm()
    if form.validate_on_submit():
        user = models.User(username=form.username.data,
                           email=form.user_email.data)
        user.hash_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        app.logger.info('New user registered')
        flask.flash('Congratulations, you are now a registered user!')
        current_user = models.User.query.filter_by(username=form.username.data).first()
        flask_login.login_user(current_user)
        return flask.redirect(flask.url_for('index'))
    return flask.render_template('sign_in.html', form=form, title='Register')


@app.route('/logout')
def logout():
    flask_login.logout_user()
    return flask.redirect(flask.url_for('index'))


# save last time user request anything to server
@app.before_request
def before_request():
    if flask_login.current_user.is_authenticated:
        flask_login.current_user.last_seen = datetime.datetime.utcnow()
        db.session.commit()


@app.route('/change_password', methods=['GET', 'POST'])
@flask_login.login_required
def change_password():
    formulary = forms.ChangePasswordForm()
    if formulary.cancel.data:
        return flask.redirect(flask.url_for('profile'))
    elif formulary.submit.data and formulary.validate_on_submit():
        flask_login.current_user.hash_password(formulary.new_password.data)
        db.session.commit()
        flask.flash('Your new password have been saved.')
        return flask.redirect(flask.url_for('profile'))
    return flask.render_template('change_password.html', title='Change password', form=formulary)


@app.route('/following', methods=['GET', 'POST'])
@flask_login.login_required
def following():
    form = forms.AddFriend()
    empty_form = forms.EmptyForm()
    if form.validate_on_submit():
        # get User object for friend_id
        followed_id = models.User.query.filter_by(username=form.friend_id.data).first()
        app.logger.warning(f'User: {flask_login.current_user} - follow to:{followed_id}')
        flask_login.current_user.follow(user=followed_id)
        db.session.commit()
        flask.flash(f"You are now following {form.friend_id.data}!")
        return flask.redirect(flask.url_for('following'))
    all_follow = flask_login.current_user.followed_users().all()
    return flask.render_template('feed.html', friends=all_follow, title='Feed', form=form, e_form=empty_form)


@app.route('/message_board')
@flask_login.login_required
def followed():
    empty_form = forms.EmptyForm()
    posts = flask_login.current_user.followed_posts().all()
    return flask.render_template('feed.html', title='Feed', posts=posts, e_form=empty_form)


@app.route('/follow/<username>', methods=['POST'])
@flask_login.login_required
def follow(username):
    form = forms.EmptyForm()
    if form.validate_on_submit():
        followed_id = models.User.query.filter_by(username=username).first()
        flask_login.current_user.follow(followed_id)
        flask.flash(f"You are now following {username}!")
        db.session.commit()
        return flask.redirect(flask.url_for('user_messages', username=username))
    else:  # in case anything fails
        return flask.redirect(flask.url_for('index'))


@app.route('/unfollow/<username>', methods=['POST'])
@flask_login.login_required
def unfollow(username):
    form = forms.EmptyForm()
    if form.validate_on_submit():
        followed_id = models.User.query.filter_by(username=username).first()
        flask_login.current_user.unfollow(followed_id)
        flask.flash(f"You stop following {username}!")
        db.session.commit()
        return flask.redirect(flask.url_for('index'))
    else:  # in case anything fails
        return flask.redirect(flask.url_for('index'))


@app.route('/delete_account', methods=['GET', 'POST'])
@flask_login.login_required
def delete_account():
    form = forms.DeleteProfile()
    if form.cancel.data:
        return flask.redirect(flask.url_for('profile'))
    if form.delete.data and form.validate_on_submit():
        db.session.delete(flask_login.current_user)
        db.session.commit()
        flask.flash(f"Profile: '{flask_login.current_user.username}' deleted!")
        return flask.redirect(flask.url_for('logout'))
    return flask.render_template('delete_account.html', title='Delete your account', form=form)


@app.route('/star/<post>/<url>', methods=['POST'])
@flask_login.login_required
def star(post, url):
    form = forms.EmptyForm()
    if form.validate_on_submit():
        post = models.Posts.query.filter_by(id=post).first()
        flask_login.current_user.star_post(post)
        flask.flash(f"You starred a new post from {post.author.username}!")
        db.session.commit()
        print(url)
        if url == 'user_messages':
            return flask.redirect(flask.url_for('user_messages', username=post.author.username))
        else:
            return flask.redirect(flask.url_for(url))
    else:  # in case anything fails
        return flask.redirect(flask.url_for('index'))


@app.route('/un_star/<post>/<url>', methods=['POST'])
@flask_login.login_required
def un_star(post, url):
    form = forms.EmptyForm()
    if form.validate_on_submit():
        post = models.Posts.query.filter_by(id=post).first()
        flask_login.current_user.un_star_post(post)
        flask.flash(f"You un-starred a post from {post.author.username}!")
        db.session.commit()
        if url == 'user_messages':
            return flask.redirect(flask.url_for('user_messages', username=post.author.username))
        else:
            return flask.redirect(flask.url_for(url))
    else:  # in case anything fails
        return flask.redirect(flask.url_for('index'))
