import flask
import flask_login
from werkzeug import urls
import datetime
from connect import app, db
from connect import models, forms


@app.route('/')
@app.route('/index')
def index():
    return flask.render_template('index.html', title='Home page')


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
        db.session.commit()
        flask.flash('Your changes have been saved.')
        return flask.redirect(flask.url_for('profile'))
    elif flask.request.method == 'GET':
        form.user_email.data = ''
        form.about_me.data = flask_login.current_user.about_me
    return flask.render_template('profile.html', user=flask_login.current_user, form=form, title='Profile')


@app.route('/sign_in', methods=['GET', 'POST'])
def sign_in():
    if flask_login.current_user.is_authenticated:
        return flask.redirect(flask.url_for('index'))
    form = forms.RegisterForm()
    if form.validate_on_submit():
        user = models.User(username=form.username.data, email=form.user_email.data)
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
