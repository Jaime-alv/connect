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


@app.route('/user/<username>')
@flask_login.login_required
def user_messages(username):
    user = models.User.query.filter_by(username=username).first_or_404()
    posts = [{'author': user, 'body': 'Test post #1'},
             {'author': user, 'body': 'Test post #2'}
             ]
    return flask.render_template('user.html', user=user, posts=posts, title=user.username)


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
        db.session.commit()
        flask.flash('Your changes have been saved.')
        return flask.redirect(flask.url_for('profile'))
    elif flask.request.method == 'GET':
        form.user_email.data = ''
        form.about_me.data = flask_login.current_user.about_me
        form.website.data = flask_login.current_user.website
        form.location.data = flask_login.current_user.location
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
        flask.flash('Congratulations, you are now a registered user!')
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
